import asyncio
import base64
import json
import logging
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dashboard import db
from dashboard.chat import stream_chat, list_lmstudio_models, list_ollama_models, \
    load_lmstudio_model, unload_lmstudio_model, list_lmstudio_loaded_models, LMS_MGMT_BASE
from dashboard.voice import (
    generate_tts, transcribe_audio, load_voice_config, save_voice_config,
    get_greeting_context, build_greeting_prompt,
    get_voice_system_prompt, add_voice_message, get_voice_history, clear_voice_history,
    build_classify_prompt, parse_action_intent, extract_identity_updates,
    apply_identity_updates, get_system_context, build_system_response_prompt,
)

logger = logging.getLogger("mantisclaw.dashboard")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent

app = FastAPI(title="MantisClaw Dashboard")
app.mount("/static", StaticFiles(directory=DASHBOARD_DIR / "static"), name="static")
templates = Jinja2Templates(directory=DASHBOARD_DIR / "templates")


# --- Runtime reference (set externally or None for standalone dashboard) ---
_runtime_instance = None


def set_runtime(runtime) -> None:
    """Allow runtime to register itself with the dashboard."""
    global _runtime_instance
    _runtime_instance = runtime


# --- State ---
class AppState:
    backend: str = "lmstudio"
    model: str = "qwen3-coder-30b-a3b-instruct"
    lmstudio_url: str = "http://localhost:1234/v1"
    ollama_url: str = "http://localhost:11434"

state = AppState()


def _load_identity() -> dict:
    identity_dir = PROJECT_ROOT / "identity"
    result = {"name": "", "owner": "", "agenda": "", "ethik": ""}
    for name, key in [("base.md", "base"), ("agenda.md", "agenda")]:
        path = identity_dir / name
        if not path.exists():
            path = identity_dir / f"{name}.example"
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if key == "base":
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("name:"):
                        result["name"] = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("owner:"):
                        result["owner"] = line.split(":", 1)[1].strip().strip('"')
                result["base_raw"] = content
            else:
                result["agenda"] = content
    return result


def _get_workpapers() -> list[dict]:
    wp_dir = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "WORKPAPER"
    result = []
    if wp_dir.exists():
        for f in sorted(wp_dir.glob("*.md"), reverse=True):
            content = f.read_text(encoding="utf-8")
            status = "OPEN"
            if "**Status:** CLOSED" in content:
                status = "CLOSED"
            result.append({"name": f.name, "status": status, "path": str(f)})
    return result


def _get_active_workpaper() -> dict | None:
    wps = _get_workpapers()
    for wp in wps:
        if wp["status"] == "OPEN":
            content = Path(wp["path"]).read_text(encoding="utf-8")
            return {"name": wp["name"], "content": content}
    return None


def _get_workspace_tree() -> list[dict]:
    """Get workspace folder tree. If a project is active, show project-scoped view."""
    working = PROJECT_ROOT / "WORKSPACE" / "WORKING"
    result = []
    # Agent-level folders (always shown, marked as agent-scope)
    agent_folders = {"AGENT-MEMORY"}
    # Project-level folders (will be scoped to active project in future)
    if working.exists():
        for d in sorted(working.iterdir()):
            if d.is_dir():
                count = sum(1 for f in d.rglob("*") if f.is_file() and f.name != ".gitkeep")
                result.append({
                    "name": d.name,
                    "count": count,
                    "scope": "agent" if d.name in agent_folders else "project",
                })
    return result


def _get_tool_names() -> list[str]:
    """Get current tool names from registry (live, not from stale diary)."""
    try:
        from core.registry import ToolRegistry
        from core.registry.tools.filesystem import create_filesystem_tools
        from core.registry.tools.memory import create_memory_tools
        from core.registry.tools.analysis import create_analysis_tools
        workspace = PROJECT_ROOT / "WORKSPACE"
        names = []
        for t in create_filesystem_tools(workspace, [str(workspace)]):
            names.append(t.name)
        for t in create_memory_tools(workspace):
            names.append(t.name)
        # analysis tools need LLM backend, just list names
        names.extend(["analyze", "summarize", "list_models", "switch_model"])
        return names
    except Exception:
        return []


def _get_active_project() -> dict | None:
    """Load active project manifest."""
    import yaml as _yaml
    active_path = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "PROJECT" / "_active.yaml"
    if not active_path.exists():
        return None
    try:
        with open(active_path, encoding="utf-8") as f:
            active = _yaml.safe_load(f) or {}
        slug = active.get("active_project")
        if not slug:
            return None
        manifest_path = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "PROJECT" / slug / "project.yaml"
        if not manifest_path.exists():
            return None
        with open(manifest_path, encoding="utf-8") as f:
            project = _yaml.safe_load(f) or {}
        project["slug"] = slug
        return project
    except Exception:
        return None


def _build_system_prompt(identity: dict) -> str:
    name = identity.get("name") or "MantisClaw"
    owner = identity.get("owner") or "unknown"
    agenda = identity.get("agenda") or ""

    # Enrich with working context
    context_parts = []

    # Active project
    project = _get_active_project()
    if project:
        milestones = project.get("milestones", [])
        open_ms = [m["name"] for m in milestones if m.get("status") in ("open", "in-progress")]
        done_ms = [m["name"] for m in milestones if m.get("status") == "done"]
        proj_block = f"Aktives Projekt: {project.get('name', '?')} ({project.get('slug', '?')})"
        proj_block += f"\nScope: {project.get('scope', '').strip()[:300]}"
        if done_ms:
            proj_block += f"\nErledigt: {', '.join(done_ms)}"
        if open_ms:
            proj_block += f"\nOffen: {', '.join(open_ms)}"
        context_parts.append(proj_block)

    # Current tool registry (live, not from stale diary)
    tool_names = _get_tool_names()
    if tool_names:
        context_parts.append(f"Registrierte Tools ({len(tool_names)}): {', '.join(tool_names)}")

    # Active workpaper
    active_wp = _get_active_workpaper()
    if active_wp:
        # Truncate to avoid blowing token budget
        wp_content = active_wp["content"][:1500]
        context_parts.append(f"Aktives Workpaper: {active_wp['name']}\n{wp_content}")

    # Workspace structure
    tree = _get_workspace_tree()
    if tree:
        tree_str = ", ".join(f"{t['name']}({t['count']})" for t in tree)
        context_parts.append(f"Workspace: {tree_str}")

    # Last diary entries
    diary_path = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "DIARY"
    if diary_path.exists():
        diary_files = sorted(diary_path.glob("*.md"), reverse=True)
        if diary_files:
            lines = diary_files[0].read_text(encoding="utf-8").strip().split("\n")
            # Last 5 substantive lines
            recent = [l for l in lines if l.strip() and not l.startswith("#") and not l.startswith(">")][-5:]
            if recent:
                context_parts.append("Letzte Diary-Einträge:\n" + "\n".join(recent))

    working_context = "\n\n".join(context_parts) if context_parts else ""

    return f"""Du bist {name}, ein autonomer Agent von {owner}.
Formel: soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
Agenda: {agenda}

{f"--- Working Context ---{chr(10)}{working_context}" if working_context else ""}

Regeln:
- Antworte hilfreich, präzise und auf Deutsch wenn der User Deutsch spricht.
- Beziehe dich auf den Working Context wenn relevant.
- Du kennst den aktuellen Projektstand aus Workpaper und Diary.
- Erfinde keine Dateien oder Pfade die nicht im Context stehen."""


def _check_connection() -> dict:
    from urllib.request import Request, urlopen
    result = {"lmstudio": False, "ollama": False}
    try:
        with urlopen(Request(f"{state.lmstudio_url}/models"), timeout=3) as r:
            result["lmstudio"] = r.status == 200
    except Exception:
        pass
    try:
        with urlopen(Request(f"{state.ollama_url}/api/tags"), timeout=3) as r:
            result["ollama"] = r.status == 200
    except Exception:
        pass
    return result


# --- Startup ---
@app.on_event("startup")
async def startup():
    await db.init_db()
    logger.info("Dashboard started. DB initialized.")


# --- Pages ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conversations = await db.list_conversations()
    identity = _load_identity()
    workpapers = _get_workpapers()
    active_wp = _get_active_workpaper()
    workspace = _get_workspace_tree()
    connection = await asyncio.to_thread(_check_connection)
    active_project = _get_active_project()

    return templates.TemplateResponse(request, "index.html", context={
        "conversations": conversations,
        "identity": identity,
        "workpapers": workpapers,
        "active_wp": active_wp,
        "workspace": workspace,
        "connection": connection,
        "state": state,
        "conv_id": None,
        "messages": [],
        "active_project": active_project,
    })


@app.get("/chat/{conv_id}", response_class=HTMLResponse)
async def chat_page(request: Request, conv_id: str):
    conv = await db.get_conversation(conv_id)
    if not conv:
        return RedirectResponse("/")
    messages = await db.get_messages(conv_id)
    conversations = await db.list_conversations()
    identity = _load_identity()
    workpapers = _get_workpapers()
    active_wp = _get_active_workpaper()
    workspace = _get_workspace_tree()
    connection = await asyncio.to_thread(_check_connection)
    active_project = _get_active_project()

    return templates.TemplateResponse(request, "index.html", context={
        "conversations": conversations,
        "identity": identity,
        "workpapers": workpapers,
        "active_wp": active_wp,
        "workspace": workspace,
        "connection": connection,
        "state": state,
        "conv_id": conv_id,
        "conv": conv,
        "messages": messages,
        "active_project": active_project,
    })


# --- API ---
@app.post("/conversations")
async def new_conversation():
    conv = await db.create_conversation(model=state.model)
    return RedirectResponse(f"/chat/{conv['id']}", status_code=303)


@app.post("/chat/{conv_id}/send")
async def send_message(conv_id: str, request: Request):
    form = await request.form()
    content = form.get("message", "").strip()
    if not content:
        return RedirectResponse(f"/chat/{conv_id}", status_code=303)

    await db.add_message(conv_id, "user", content)
    return RedirectResponse(f"/chat/{conv_id}/generating", status_code=303)


@app.get("/chat/{conv_id}/generating", response_class=HTMLResponse)
async def generating_page(request: Request, conv_id: str):
    """Page that auto-starts SSE streaming."""
    conv = await db.get_conversation(conv_id)
    messages = await db.get_messages(conv_id)
    conversations = await db.list_conversations()
    identity = _load_identity()
    workpapers = _get_workpapers()
    active_wp = _get_active_workpaper()
    workspace = _get_workspace_tree()
    connection = await asyncio.to_thread(_check_connection)

    return templates.TemplateResponse(request, "index.html", context={
        "conversations": conversations,
        "identity": identity,
        "workpapers": workpapers,
        "active_wp": active_wp,
        "workspace": workspace,
        "connection": connection,
        "state": state,
        "conv_id": conv_id,
        "conv": conv,
        "messages": messages,
        "generating": True,
    })


@app.get("/chat/{conv_id}/stream")
async def stream_response(conv_id: str):
    messages = await db.get_messages(conv_id)
    identity = _load_identity()
    system = _build_system_prompt(identity)

    chat_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    full_response = []
    base_url = state.lmstudio_url if state.backend == "lmstudio" else state.ollama_url

    async def generate():
        loop = asyncio.get_event_loop()
        chunks_iter = await loop.run_in_executor(
            None,
            lambda: list(stream_chat(
                messages=chat_messages,
                model=state.model,
                backend=state.backend,
                base_url=base_url,
                system=system,
            ))
        )
        for chunk in chunks_iter:
            full_response.append(chunk)
            yield f"data: {json.dumps({'content': chunk})}\n\n"

        # Save complete response
        complete = "".join(full_response)
        await db.add_message(conv_id, "assistant", complete, model=state.model)

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/models")
async def get_models():
    lm_models = list_lmstudio_models(state.lmstudio_url)
    ol_models = list_ollama_models(state.ollama_url)
    return {
        "lmstudio": lm_models,
        "ollama": ol_models,
        "current_backend": state.backend,
        "current_model": state.model,
    }


@app.post("/api/model")
async def set_model(request: Request):
    data = await request.json()
    state.backend = data.get("backend", state.backend)
    state.model = data.get("model", state.model)
    return {"backend": state.backend, "model": state.model}


@app.post("/api/models/load")
async def api_load_model(request: Request):
    """Load a model in LM Studio (unloads current if different)."""
    data = await request.json()
    model_id = data.get("model_id", "")
    if not model_id:
        return {"error": "model_id required"}

    # Unload current if different
    current_loaded = await asyncio.to_thread(list_lmstudio_loaded_models)
    loaded_ids = [m.get("identifier", m.get("id", "")) for m in current_loaded]
    if loaded_ids and model_id not in loaded_ids:
        for mid in loaded_ids:
            await asyncio.to_thread(unload_lmstudio_model, mid)
        logger.info(f"Unloaded: {loaded_ids}")

    result = await asyncio.to_thread(load_lmstudio_model, model_id)
    if "error" not in result:
        state.model = model_id
        logger.info(f"Loaded model: {model_id}")
    return {"model_id": model_id, "result": result, "current_model": state.model}


@app.post("/api/models/unload")
async def api_unload_model(request: Request):
    """Unload a specific model from LM Studio."""
    data = await request.json()
    model_id = data.get("model_id", state.model)
    result = await asyncio.to_thread(unload_lmstudio_model, model_id)
    return {"model_id": model_id, "result": result}


@app.get("/api/models/loaded")
async def api_loaded_models():
    """List currently loaded models in LM Studio."""
    loaded = await asyncio.to_thread(list_lmstudio_loaded_models)
    return {"loaded": loaded}


@app.get("/api/health")
async def health():
    connection = await asyncio.to_thread(_check_connection)
    return {
        "status": "ok",
        "connection": connection,
        "backend": state.backend,
        "model": state.model,
    }


@app.delete("/conversations/{conv_id}")
async def remove_conversation(conv_id: str):
    await db.delete_conversation(conv_id)
    return {"ok": True}


# --- Runtime Bridge ---
BRIDGE_PATH = PROJECT_ROOT / "data" / "runtime_state.json"


def _read_bridge() -> dict | None:
    """Read runtime state from bridge file. Returns None if unavailable or stale."""
    try:
        if not BRIDGE_PATH.exists():
            return None
        data = json.loads(BRIDGE_PATH.read_text(encoding="utf-8"))
        return data
    except Exception:
        return None


# --- Runtime API ---
@app.get("/api/runtime")
async def runtime_status():
    """Get runtime state from bridge file or in-process instance."""
    # Load project tools (available even without runtime)
    project = _get_active_project()
    project_tools = []
    project_tool_names = set()
    if project and "tools" in project:
        for pt in project["tools"]:
            project_tools.append({
                "name": pt.get("name", ""),
                "description": pt.get("description", ""),
                "file": pt.get("file", ""),
                "skill": pt.get("skill", ""),
            })
            project_tool_names.add(pt.get("name", ""))

    # Try in-process instance first, then bridge file
    if _runtime_instance:
        rt = _runtime_instance
        return {
            "running": rt.running,
            "tick_count": rt.tick_count,
            "health": rt.observer.health,
            "heartbeat": rt.heartbeat_interval,
            "voice_enabled": rt.voice.enabled,
            "tools": [{"name": t.name, "description": t.description, "level": t.security_level,
                        "project": t.name in project_tool_names}
                      for t in rt.registry.list_available()],
            "project_tools": project_tools,
            "project_name": project.get("name") if project else None,
            "session": {
                "workpaper": str(rt.session.workpaper_path) if rt.session.workpaper_path else None,
                "agent": rt.session.agent_name,
            },
        }

    # Bridge file fallback (separate process runtime)
    bridge = _read_bridge()
    if bridge and bridge.get("running"):
        # Mark project tools
        for t in bridge.get("tools", []):
            t["project"] = t.get("name", "") in project_tool_names
        bridge["project_tools"] = project_tools
        bridge["project_name"] = project.get("name") if project else None
        return bridge

    return {"running": False, "message": "Runtime not connected",
            "project_tools": project_tools,
            "project_name": project.get("name") if project else None}


@app.get("/api/runtime/ticks")
async def runtime_ticks(limit: int = 10):
    """Get recent tick history from observer or bridge file."""
    if _runtime_instance:
        rt = _runtime_instance
        ticks = []
        for m in rt.observer.history[-limit:]:
            ticks.append({
                "tick": m.tick_number,
                "ts": m.timestamp,
                "goal": m.plan_goal,
                "steps": m.steps_total,
                "ok": m.steps_succeeded,
                "fail": m.steps_failed,
                "anomalies": m.anomalies[:3],
            })
        ticks.reverse()
        return {
            "ticks": ticks,
            "idle_repeats": getattr(rt, '_repeat_count', 0),
            "tick_summaries": getattr(rt, '_tick_summaries', [])[-5:],
        }

    # Bridge file fallback
    bridge = _read_bridge()
    if bridge:
        ticks = bridge.get("ticks", [])[:limit]
        return {
            "ticks": ticks,
            "idle_repeats": bridge.get("idle_repeats", 0),
            "tick_summaries": bridge.get("tick_summaries", []),
        }

    return {"ticks": [], "idle_repeats": 0}


@app.post("/api/runtime/voice")
async def toggle_runtime_voice(request: Request):
    """Toggle voice on/off for runtime via bridge file."""
    body = await request.json()
    enabled = body.get("enabled", True)

    # In-process: direct toggle
    if _runtime_instance:
        _runtime_instance.voice.enabled = enabled
        return {"voice_enabled": enabled}

    # Bridge: read-modify-write
    bridge = _read_bridge()
    if bridge:
        bridge["voice_enabled"] = enabled
        try:
            BRIDGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            tmp = BRIDGE_PATH.with_suffix(".tmp")
            tmp.write_text(json.dumps(bridge, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(BRIDGE_PATH)
            return {"voice_enabled": enabled}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Runtime not connected"}


@app.get("/api/workpapers")
async def list_workpapers_api():
    """List all workpapers with status (open/closed)."""
    wps = _get_workpapers()
    closed_dir = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "WORKPAPER" / "closed"
    if closed_dir.exists():
        for f in sorted(closed_dir.glob("*.md"), reverse=True):
            wps.append({"name": f.name, "status": "CLOSED", "path": str(f)})
    return {"workpapers": wps}


@app.get("/api/workpapers/{wp_name}")
async def get_workpaper_content(wp_name: str):
    """Get content of a specific workpaper."""
    # Validate filename to prevent path traversal
    if ".." in wp_name or "/" in wp_name or "\\" in wp_name:
        return {"error": "Invalid filename"}
    for search_dir in [
        PROJECT_ROOT / "WORKSPACE" / "WORKING" / "WORKPAPER",
        PROJECT_ROOT / "WORKSPACE" / "WORKING" / "WORKPAPER" / "closed",
    ]:
        path = search_dir / wp_name
        if path.exists() and path.is_file():
            content = path.read_text(encoding="utf-8")
            status = "CLOSED" if "**Status:** CLOSED" in content else "OPEN"
            return {"name": wp_name, "status": status, "content": content}
    return {"error": "Workpaper not found"}


@app.get("/api/identity")
async def get_identity_files():
    """Return all identity files + computed soul(t) for the inspector panel."""
    identity_dir = PROJECT_ROOT / "identity"
    files = {}
    for fname in ["base.md", "agenda.md", "account.md", "social.md", "decentral.md", "hook.md"]:
        path = identity_dir / fname
        if not path.exists():
            path = identity_dir / f"{fname}.example"
        if path.exists():
            files[fname] = path.read_text(encoding="utf-8")
        else:
            files[fname] = ""

    # Compute soul(t) summary
    base_raw = files.get("base.md", "")
    soul_fields = {}
    for line in base_raw.split("\n"):
        line = line.strip()
        if line.startswith("name:"):
            soul_fields["name"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("owner:"):
            soul_fields["owner"] = line.split(":", 1)[1].strip().strip('"')

    active_project = _get_active_project()

    return {
        "files": files,
        "soul_formula": "soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)",
        "soul_fields": soul_fields,
        "active_project": active_project.get("name") if active_project else None,
    }


# --- Project API ---
def _list_projects() -> list[dict]:
    """List all projects from WORKING/PROJECT/*/project.yaml."""
    import yaml as _yaml
    project_dir = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "PROJECT"
    projects = []
    if not project_dir.exists():
        return projects
    for d in sorted(project_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        manifest = d / "project.yaml"
        if not manifest.exists():
            continue
        try:
            with open(manifest, encoding="utf-8") as f:
                data = _yaml.safe_load(f) or {}
            projects.append({
                "slug": d.name,
                "name": data.get("name", d.name),
                "status": data.get("status", "unknown"),
            })
        except Exception:
            projects.append({"slug": d.name, "name": d.name, "status": "error"})
    return projects


def _get_active_project_slug() -> str | None:
    """Get the slug of the active project from _active.yaml."""
    import yaml as _yaml
    active_path = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "PROJECT" / "_active.yaml"
    if not active_path.exists():
        return None
    try:
        with open(active_path, encoding="utf-8") as f:
            data = _yaml.safe_load(f) or {}
        return data.get("active_project")
    except Exception:
        return None


def _set_active_project(slug: str) -> bool:
    """Set the active project in _active.yaml."""
    import yaml as _yaml
    project_dir = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "PROJECT"
    active_path = project_dir / "_active.yaml"
    # Verify project exists
    if not (project_dir / slug / "project.yaml").exists():
        return False
    try:
        from datetime import datetime, timezone
        data = {
            "active_project": slug,
            "since": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        active_path.write_text(
            _yaml.dump(data, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


@app.get("/api/projects")
async def api_list_projects():
    """List all projects with active marker."""
    projects = _list_projects()
    active_slug = _get_active_project_slug()
    for p in projects:
        p["active"] = p["slug"] == active_slug
    return {"projects": projects, "active": active_slug}


@app.get("/api/projects/active")
async def api_get_active_project():
    """Get full active project data."""
    project = _get_active_project()
    if not project:
        return {"error": "No active project"}
    return project


@app.post("/api/projects/active")
async def api_set_active_project(request: Request):
    """Switch the active project."""
    data = await request.json()
    slug = data.get("slug", "").strip()
    if not slug:
        return {"error": "slug required"}
    if _set_active_project(slug):
        project = _get_active_project()
        return {"ok": True, "project": project}
    return {"error": f"Project '{slug}' not found"}


@app.get("/api/projects/{slug}/tree")
async def api_project_tree(slug: str):
    """Return WORKING folder tree. Currently global WORKING (project-scoped migration planned)."""
    # Validate slug
    if ".." in slug or "/" in slug or "\\" in slug:
        return {"error": "Invalid slug"}
    working = PROJECT_ROOT / "WORKSPACE" / "WORKING"
    if not working.exists():
        return {"folders": []}
    folders = []
    # Show AAMS folders with file listing
    for d in sorted(working.iterdir()):
        if not d.is_dir() or d.name.startswith("_") or d.name == "PROJECT":
            continue
        files = []
        for f in sorted(d.rglob("*")):
            if f.is_file() and f.name != ".gitkeep":
                rel = f.relative_to(d)
                files.append({"name": str(rel), "size": f.stat().st_size})
        folders.append({
            "name": d.name,
            "count": len(files),
            "files": files[:50],  # limit per folder
        })
    return {"slug": slug, "folders": folders}


@app.get("/api/projects/{slug}/file")
async def api_project_file(slug: str, path: str = ""):
    """Read a file from WORKING by relative path. Path-traversal protected."""
    if ".." in path or ".." in slug:
        return {"error": "Invalid path"}
    working = PROJECT_ROOT / "WORKSPACE" / "WORKING"
    target = (working / path).resolve()
    # Ensure target is under WORKING
    if not str(target).startswith(str(working.resolve())):
        return {"error": "Access denied"}
    if not target.exists() or not target.is_file():
        return {"error": "File not found"}
    try:
        content = target.read_text(encoding="utf-8")
        return {"name": target.name, "path": path, "content": content}
    except Exception:
        return {"error": "Cannot read file"}


async def get_prompt_log(limit: int = 20):
    """Return the last N prompt entries from LOGS/prompt_log.jsonl."""
    log_path = PROJECT_ROOT / "WORKSPACE" / "WORKING" / "LOGS" / "prompt_log.jsonl"
    if not log_path.exists():
        return {"entries": [], "total": 0}
    try:
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        # Return last N entries newest-first
        entries = []
        for line in reversed(lines[-limit * 2:]):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(entries) >= limit:
                break
        return {"entries": entries, "total": len(lines)}
    except Exception as e:
        return {"error": str(e), "entries": []}


# --- Voice API ---
@app.post("/api/tts")
async def api_tts(request: Request):
    """Generate TTS audio from text. Returns base64-encoded MP3."""
    data = await request.json()
    text = data.get("text", "").strip()
    if not text:
        return {"error": "No text provided"}
    voice = data.get("voice") or load_voice_config().get("voice")
    audio_bytes = await generate_tts(text, voice)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    return {"audio_b64": audio_b64, "voice": voice}


@app.post("/api/stt")
async def api_stt(audio: UploadFile = File(...)):
    """Transcribe uploaded audio to text via faster-whisper."""
    audio_bytes = await audio.read()
    if not audio_bytes:
        return {"text": "", "error": "Empty audio"}
    text = await asyncio.to_thread(transcribe_audio, audio_bytes)
    return {"text": text}


@app.get("/api/voice/config")
async def api_voice_config():
    """Get current voice configuration."""
    return load_voice_config()


@app.post("/api/voice/config")
async def api_set_voice_config(request: Request):
    """Update voice configuration (name, voice, enabled, auto_read)."""
    data = await request.json()
    config = load_voice_config()
    for key in ("name", "voice", "enabled", "auto_read"):
        if key in data:
            config[key] = data[key]
    save_voice_config(config)
    return config


@app.get("/api/voice/greeting")
async def api_greeting():
    """Get greeting context and generate greeting via LLM + TTS."""
    ctx = get_greeting_context()
    prompt = build_greeting_prompt(ctx)

    # Use the chat LLM to generate greeting text
    from dashboard.chat import stream_chat
    messages = [{"role": "user", "content": "Starte Begrüßung."}]
    base_url = state.lmstudio_url if state.backend == "lmstudio" else state.ollama_url

    loop = asyncio.get_event_loop()
    chunks = await loop.run_in_executor(
        None,
        lambda: list(stream_chat(
            messages=messages,
            model=state.model,
            backend=state.backend,
            base_url=base_url,
            system=prompt,
        ))
    )
    greeting_text = "".join(chunks).strip()

    # Generate TTS for the greeting
    voice = ctx.get("voice", load_voice_config().get("voice"))
    audio_bytes = await generate_tts(greeting_text, voice)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    return {
        "level": ctx["level"],
        "agent_name": ctx["agent_name"],
        "text": greeting_text,
        "audio_b64": audio_b64,
    }


@app.post("/api/voice/talk")
async def api_voice_talk(request: Request):
    """Process user text in the L5 voice conversation with action classification."""
    data = await request.json()
    user_text = data.get("text", "").strip()
    if not user_text:
        return {"error": "No text provided"}

    # Add user message to voice history
    add_voice_message("user", user_text)

    base_url = state.lmstudio_url if state.backend == "lmstudio" else state.ollama_url
    loop = asyncio.get_event_loop()

    # Step 1: Classify intent
    classify_messages = build_classify_prompt(user_text)
    classify_chunks = await loop.run_in_executor(
        None,
        lambda: list(stream_chat(
            messages=classify_messages[1:],  # user message only
            model=state.model,
            backend=state.backend,
            base_url=base_url,
            system=classify_messages[0]["content"],  # system prompt
        ))
    )
    intent = parse_action_intent("".join(classify_chunks))
    logger.info(f"Voice intent: {intent} for: {user_text[:60]}")

    action_result = None
    system_prompt = get_voice_system_prompt()

    # Step 2: Handle by intent
    if intent == "IDENTITY":
        # Extract and apply identity changes
        updates = extract_identity_updates(user_text, "")
        if updates:
            changes_summary = apply_identity_updates(updates)
            action_result = {"type": "identity_update", "changes": changes_summary}
            # Reload system prompt with new identity
            system_prompt = get_voice_system_prompt()
            # Add context hint so LLM knows what changed
            system_prompt += f"\n\nDu hast gerade deine Identität angepasst: {changes_summary}. Bestätige die Änderungen kurz."

    elif intent == "SYSTEM":
        # Gather system context and use enriched prompt
        sys_ctx = get_system_context()
        system_prompt = build_system_response_prompt(user_text, sys_ctx)
        action_result = {"type": "system_query", "context": sys_ctx}

    # Step 3: Generate response with conversation history
    history = get_voice_history()
    messages = [{"role": m["role"], "content": m["content"]} for m in history]

    response_chunks = await loop.run_in_executor(
        None,
        lambda: list(stream_chat(
            messages=messages,
            model=state.model,
            backend=state.backend,
            base_url=base_url,
            system=system_prompt,
        ))
    )
    response_text = "".join(response_chunks).strip()

    # Clean thinking tags from response
    if "</think>" in response_text:
        response_text = response_text.split("</think>")[-1].strip()

    # Step 4: Post-processing - extract system actions from response
    system_action = None
    if "[ACTION:" in response_text:
        import re
        action_match = re.search(r'\[ACTION:(\w+)\]', response_text)
        if action_match:
            system_action = action_match.group(1)
            response_text = re.sub(r'\s*\[ACTION:\w+\]\s*', ' ', response_text).strip()

    # Add assistant response to voice history
    add_voice_message("assistant", response_text)

    # Generate TTS audio (use potentially updated voice config)
    voice = load_voice_config().get("voice", "de-DE-KatjaNeural")
    audio_bytes = await generate_tts(response_text, voice)
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

    result = {
        "user_text": user_text,
        "text": response_text,
        "audio_b64": audio_b64,
        "intent": intent,
    }
    if action_result:
        result["action"] = action_result
    if system_action:
        result["system_action"] = system_action
    return result


@app.get("/api/voice/history")
async def api_voice_history():
    """Get the current voice conversation history."""
    return {"messages": get_voice_history()}


@app.post("/api/voice/clear")
async def api_voice_clear():
    """Clear voice conversation history."""
    clear_voice_history()
    return {"ok": True}
