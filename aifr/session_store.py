from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Tuple

from .config import DEFAULT_CONTEXT_LIMIT
from .context import Message

CACHE_DIR = Path.home() / ".cache" / "aifr"
SESSION_FILE = CACHE_DIR / "session.json"
SESSION_TTL_SECONDS = 2 * 60 * 60  # 2h
MAX_HISTORY_TURNS = 5  # Trzymamy tylko 5 ostatnich wymian zdań (oszczędność tokenów)


def load_session() -> Tuple[int, List[Message]]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not SESSION_FILE.exists():
        return DEFAULT_CONTEXT_LIMIT, []
    try:
        data = json.loads(SESSION_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return DEFAULT_CONTEXT_LIMIT, []
    ts = data.get("timestamp")
    if not isinstance(ts, (int, float)) or time.time() - ts > SESSION_TTL_SECONDS:
        return DEFAULT_CONTEXT_LIMIT, []
    max_tokens = data.get("max_tokens", DEFAULT_CONTEXT_LIMIT)
    raw_messages = data.get("messages") or []
    messages: List[Message] = []
    for item in raw_messages:
        role = item.get("role")
        content = item.get("content")
        if isinstance(role, str) and isinstance(content, str):
            messages.append(Message(role=role, content=content))
    return max_tokens, messages

def prune_messages(messages: List[Message]) -> List[Message]:
    """Zostawia system prompt (jeśli jest) i ostatnie N wiadomości."""
    if len(messages) <= MAX_HISTORY_TURNS * 2:
        return messages
    
    # Zakładamy, że kontekst może mieć instrukcję systemową na początku, 
    # której nie chcemy usuwać (jeśli byśmy ją tam zapisywali), 
    # ale w Aifr system prompt jest dodawany dynamicznie w cli.py.
    # Więc po prostu ucinamy najstarsze:
    return messages[-(MAX_HISTORY_TURNS * 2):]

def save_session(max_tokens: int, messages: List[Message]) -> None:
    # OPTYMALIZACJA: Zapisz tylko 'chunky' - ostatnie fragmenty rozmowy
    pruned_messages = prune_messages(messages)
    
    payload = {
        "timestamp": time.time(),
        "max_tokens": max_tokens,
        "messages": [{"role": m.role, "content": m.content} for m in pruned_messages],
    }
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(payload))


def clear_session() -> None:
    try:
        SESSION_FILE.unlink()
    except FileNotFoundError:
        pass
