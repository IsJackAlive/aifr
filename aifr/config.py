from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_DIR = Path.home() / ".config" / "aifr"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_CONTEXT_LIMIT = 6000  # approximate tokens/words budget
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5MB
SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".json", ".yaml", ".yml", ".csv", ".log", ".xml", ".ini", ".cfg", ".j2"}
SHERLOCK_ENDPOINT = "https://api-sherlock.cloudferro.com/openai/v1/chat/completions"

# System prompt for the LLM assistant
SYSTEM_PROMPT = (
    "Jesteś terminalowym asystentem. Odpowiadasz tylko tekstem, bez markdown "
    "i bez bloków kodu. Jeśli w wiadomości jest blok oznaczony "
    "===FILE_START=== ... ===FILE_END===, to jest pełna treść pliku; zawsze "
    "z niej korzystasz i nigdy nie piszesz, że plik nie został wklejony. "
    "Jeśli jest blok ===CONSOLE_START=== ... ===CONSOLE_END===, to jest "
    "zawartość terminala/konsoli użytkownika - analizujesz ją w kontekście pytania. "
    "Jeśli bloków nie ma, i tak odpowiadasz na pytanie na bazie dostępnego "
    "kontekstu. Nie prosisz o ponowne wklejenie pliku. Jeśli proszą o "
    "podsumowanie, po prostu je podaj. Wybierasz model LLM odpowiedni do "
    "zadania i zwracasz gotową odpowiedź."
)


@dataclass
class AppConfig:
    api_key: str
    context_limit: int = DEFAULT_CONTEXT_LIMIT
    model: Optional[str] = None
    provider: str = "sherlock"  # sherlock, openai, openwebui, brave
    base_url: Optional[str] = None  # For OpenWebUI custom endpoints
    model_aliases: Dict[str, str] = None
    custom_agents: Dict[str, Dict[str, str]] = None


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        data: Dict[str, Any] = json.loads(path.read_text())
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def load_config() -> Dict[str, Any]:
    # Check multiple env vars for different providers
    env_key = (
        os.getenv("SHERLOCK_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("BRAVE_API_KEY")
        or os.getenv("OPENWEBUI_API_KEY")
    )
    data: Dict[str, Any] = _read_json(CONFIG_FILE)
    if env_key:
        data["api_key"] = env_key
    return data


def get_config() -> AppConfig:
    data = load_config()
    api_key = data.get("api_key")
    if not api_key:
        raise RuntimeError(
            "Brak klucza API. Ustaw SHERLOCK_API_KEY/OPENAI_API_KEY/BRAVE_API_KEY "
            "lub dodaj api_key w ~/.config/aifr/config.json"
        )
    context_limit = _safe_int(data.get("context_limit"), DEFAULT_CONTEXT_LIMIT)
    model = data.get("model")
    provider = data.get("provider", "sherlock")  # Default to sherlock
    base_url = data.get("base_url")  # For OpenWebUI

    # Auto-detect provider from environment variables if not explicitly set
    if provider == "sherlock" and not data.get("provider"):
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("BRAVE_API_KEY"):
            provider = "brave"
        elif os.getenv("OPENWEBUI_API_KEY"):
            provider = "openwebui"

    return AppConfig(
        api_key=api_key,
        context_limit=context_limit,
        model=model,
        provider=provider,
        base_url=base_url,
        model_aliases=data.get("model_aliases", {}),
        custom_agents=data.get("custom_agents", {}),
    )


def persist_api_key(api_key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = _read_json(CONFIG_FILE)
    payload["api_key"] = api_key.strip()
    CONFIG_FILE.write_text(json.dumps(payload, indent=2))


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
