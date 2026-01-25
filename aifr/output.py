from __future__ import annotations

from typing import Iterable, Optional

from .markdown_renderer import render_markdown


def print_chunks(text: str, chunk_size: int = 1200) -> None:
    if not text:
        return
    
    # Render markdown with retro colors
    rendered_text = render_markdown(text)
    
    for chunk in _chunk(rendered_text, chunk_size):
        print(chunk)


def print_usage_summary(
    model: str,
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
    total_tokens: Optional[int],
) -> None:
    tokens: list[str] = []
    if prompt_tokens is not None:
        tokens.append(f"wejście tokeny: {prompt_tokens}")
    if completion_tokens is not None:
        tokens.append(f"wyjście tokeny: {completion_tokens}")
    if total_tokens is not None:
        tokens.append(f"razem: {total_tokens}")
    if not tokens:
        tokens.append("brak danych o tokenach")
    print(" | ".join([f"Model: {model}", *tokens]))


def _chunk(text: str, size: int) -> Iterable[str]:
    for idx in range(0, len(text), size):
        yield text[idx : idx + size]
