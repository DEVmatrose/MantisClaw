import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger("mantisclaw.dashboard.chat")


def list_lmstudio_models(base_url: str = "http://localhost:1234/v1") -> list[str]:
    try:
        req = Request(f"{base_url}/models")
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return [m["id"] for m in data.get("data", [])]
    except Exception:
        return []


def list_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    try:
        req = Request(f"{base_url}/api/tags")
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def stream_chat(messages: list[dict], model: str, backend: str = "lmstudio",
                base_url: str | None = None, system: str | None = None):
    """Generator that yields content chunks from LLM streaming response."""

    if backend == "lmstudio":
        url = f"{base_url or 'http://localhost:1234/v1'}/chat/completions"
    elif backend == "ollama":
        url = f"{base_url or 'http://localhost:11434'}/api/chat"
    else:
        raise ValueError(f"Streaming not supported for backend: {backend}")

    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    if backend == "ollama":
        payload = {
            "model": model,
            "messages": full_messages,
            "stream": True,
        }
    else:
        payload = {
            "model": model,
            "messages": full_messages,
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": True,
        }

    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    try:
        resp = urlopen(req, timeout=120)
    except URLError as e:
        yield f"[ERROR] Kann {backend} nicht erreichen: {e}"
        return

    buffer = b""
    for chunk in iter(lambda: resp.read(1), b""):
        buffer += chunk
        if chunk == b"\n":
            line = buffer.decode("utf-8").strip()
            buffer = b""

            if not line:
                continue

            if backend == "ollama":
                try:
                    obj = json.loads(line)
                    content = obj.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if obj.get("done"):
                        return
                except json.JSONDecodeError:
                    continue
            else:
                # OpenAI SSE format: data: {...}
                if line.startswith("data: "):
                    line = line[6:]
                if line == "[DONE]":
                    return
                try:
                    obj = json.loads(line)
                    delta = obj.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    resp.close()
