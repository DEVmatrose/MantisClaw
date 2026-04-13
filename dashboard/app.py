import asyncio
import json
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dashboard import db
from dashboard.chat import stream_chat, list_lmstudio_models, list_ollama_models

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
    working = PROJECT_ROOT / "WORKSPACE" / "WORKING"
    result = []
    if working.exists():
        for d in sorted(working.iterdir()):
            if d.is_dir():
                count = sum(1 for f in d.rglob("*") if f.is_file() and f.name != ".gitkeep")
                result.append({"name": d.name, "count": count})
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
        names.extend(["analyze", "summarize"])
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

    return templates.TemplateResponse("index.html", {
        "request": request,
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

    return templates.TemplateResponse("index.html", {
        "request": request,
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

    return templates.TemplateResponse("index.html", {
        "request": request,
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


# --- Runtime API ---
@app.get("/api/runtime")
async def runtime_status():
    """Get runtime state: tick count, health, registered tools, active session."""
    if not _runtime_instance:
        return {"running": False, "message": "Runtime not connected"}
    rt = _runtime_instance
    return {
        "running": rt.running,
        "tick_count": rt.tick_count,
        "health": rt.observer.health,
        "heartbeat": rt.heartbeat_interval,
        "tools": [{"name": t.name, "description": t.description, "level": t.security_level}
                  for t in rt.registry.list_available()],
        "session": {
            "workpaper": str(rt.session.workpaper_path) if rt.session.workpaper_path else None,
            "agent": rt.session.agent_name,
        },
    }


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
