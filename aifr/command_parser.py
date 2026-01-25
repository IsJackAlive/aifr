from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Command:
    ask: str
    file: Optional[str]
    model: Optional[str]
    context_limit: Optional[int]
    console: Optional[str]  # None = no console, "" = read from stdin, "cmd" = execute cmd


class CommandError(Exception):
    pass


def parse_command(raw: str) -> Command:
    text = raw.strip()
    if text.startswith("aifr"):
        text = text[4:].lstrip(" -")

    if not text:
        raise CommandError("Brak polecenia")

    parts = re.split(r"\$(ask|file|model|context_limit|cons(?:ole)?):", text, flags=re.IGNORECASE)
    parsed: dict[str, Optional[str | int]] = {"ask": None, "file": None, "model": None, "context_limit": None, "console": None}

    if len(parts) == 1:
        parsed["ask"] = parts[0].strip()
    else:
        prefix = parts[0].strip()
        for idx in range(1, len(parts), 2):
            key = parts[idx].lower()
            # Normalize console/cons to console
            if key in ("cons", "console"):
                key = "console"
            value = parts[idx + 1].strip() if idx + 1 < len(parts) else ""
            if key == "context_limit":
                parsed[key] = _safe_int(value)
            elif key == "console":
                # For console: empty string means read from stdin, otherwise it's a command
                parsed[key] = value  # Keep empty string, don't convert to None
            else:
                parsed[key] = value if value else None
        if prefix and not parsed["ask"]:
            parsed["ask"] = prefix

    ask = parsed.get("ask")
    if not ask:
        raise CommandError("Polecenie wymaga $ask: <pytanie>")

    # Extract context_limit with proper type checking
    context_limit_val = parsed.get("context_limit")
    context_limit: Optional[int] = None
    if isinstance(context_limit_val, int):
        context_limit = context_limit_val

    return Command(
        ask=str(ask),
        file=str(parsed.get("file")) if parsed.get("file") else None,
        model=str(parsed.get("model")) if parsed.get("model") else None,
        context_limit=context_limit,
        console=str(parsed.get("console")) if parsed.get("console") is not None else None,
    )


def _safe_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
