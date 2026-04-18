# L0: LLM-Backend-Abstraction
"""
Abstraktion über LLM-Provider. Local-first.

Priorität:
  1. lmstudio  — OpenAI-kompatible API auf localhost (DEFAULT)
  2. ollama    — Ollama REST-API auf localhost
  3. openai    — Cloud (optional)
  4. anthropic — Cloud (optional)

Backend wird über config/default.yaml + .env konfiguriert.
"""

import asyncio
import os
import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

logger = logging.getLogger("mantisclaw.llm")

# Default-Endpunkte für lokale Backends
DEFAULTS = {
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "model": "local-model",
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "llama3",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "model": "claude-sonnet-4-20250514",
    },
}


def _post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 120) -> dict:
    """Simple HTTP POST without external dependencies."""
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=hdrs, method="POST")
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class LLMBackend:
    """Unified interface to LLM providers. Local-first."""

    # Shared lock — serializes all LLM access (Loop-Mode + Chat-Mode)
    _lock = asyncio.Lock()

    def __init__(self, config: dict):
        self.backend = config.get("backend", "lmstudio")
        defaults = DEFAULTS.get(self.backend, {})
        self.base_url = config.get("base_url", defaults.get("base_url", ""))
        self.model = config.get("model", defaults.get("model", ""))
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 4096)

        logger.info(f"LLM Backend: {self.backend} | Model: {self.model} | URL: {self.base_url}")

    def _is_local(self) -> bool:
        return self.backend in ("lmstudio", "ollama")

    def _get_auth_header(self) -> dict:
        if self.backend == "lmstudio":
            return {}  # LM Studio braucht keinen API-Key
        elif self.backend == "ollama":
            return {}  # Ollama braucht keinen API-Key
        elif self.backend == "openai":
            key = os.getenv("OPENAI_API_KEY", "")
            if not key:
                raise RuntimeError("OPENAI_API_KEY nicht gesetzt in .env")
            return {"Authorization": f"Bearer {key}"}
        elif self.backend == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY", "")
            if not key:
                raise RuntimeError("ANTHROPIC_API_KEY nicht gesetzt in .env")
            return {
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            }
        return {}

    async def complete(self, messages: list[dict], system: str | None = None) -> str:
        async with self._lock:
            if self.backend in ("lmstudio", "ollama", "openai"):
                return self._complete_openai_compat(messages, system)
            elif self.backend == "anthropic":
                return self._complete_anthropic(messages, system)
            else:
                raise ValueError(f"Unknown LLM backend: {self.backend}")

    def _complete_openai_compat(self, messages: list[dict], system: str | None) -> str:
        """OpenAI-kompatible API — funktioniert für LM Studio, Ollama und OpenAI."""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        # Ollama nutzt /api/chat, LM Studio + OpenAI nutzen /v1/chat/completions
        if self.backend == "ollama":
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model,
                "messages": full_messages,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            }
        else:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": full_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

        try:
            resp = _post_json(url, payload, headers=self._get_auth_header())
        except URLError as e:
            raise ConnectionError(
                f"Kann {self.backend} nicht erreichen unter {url}. "
                f"Läuft der Server? Error: {e}"
            )

        # Ollama-Format vs. OpenAI-Format
        if self.backend == "ollama":
            return resp.get("message", {}).get("content", "")
        else:
            return resp["choices"][0]["message"]["content"]

    def _complete_anthropic(self, messages: list[dict], system: str | None) -> str:
        """Anthropic Messages API."""
        url = f"{self.base_url}/v1/messages"
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system:
            payload["system"] = system

        try:
            resp = _post_json(url, payload, headers=self._get_auth_header())
        except URLError as e:
            raise ConnectionError(f"Kann Anthropic API nicht erreichen: {e}")

        return resp["content"][0]["text"]

    async def complete_simple(self, prompt: str, system: str | None = None, max_tokens: int | None = None) -> str:
        old_max = self.max_tokens
        if max_tokens is not None:
            self.max_tokens = max_tokens
        try:
            return await self.complete(
                messages=[{"role": "user", "content": prompt}],
                system=system,
            )
        finally:
            self.max_tokens = old_max

    def check_connection(self) -> bool:
        """Prüft ob das Backend erreichbar ist."""
        try:
            if self.backend == "lmstudio":
                url = f"{self.base_url}/models"
            elif self.backend == "ollama":
                url = f"{self.base_url}/api/tags"
            else:
                return True  # Cloud-Backends nicht vorprüfen

            req = Request(url)
            with urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False
