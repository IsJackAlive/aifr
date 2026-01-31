from __future__ import annotations

from typing import Iterable, Iterator, Optional
import sys

from .markdown_renderer import render_markdown



def should_colorize(raw_flag: bool = False) -> bool:
    """Check if output should be colorized (TTY and not raw mode)."""
    if raw_flag:
        return False
    return sys.stdout.isatty()


def print_chunks(text: str, chunk_size: int = 1200, raw_flag: bool = False) -> None:
    if not text:
        return
    
    if not should_colorize(raw_flag):
        # Raw output mode - flush immediately
        print(text, flush=True)
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


def _chunk(text: str, size: int) -> Iterator[str]:
    for idx in range(0, len(text), size):
        yield text[idx : idx + size]


def stream_display(generator: Iterable[str], raw_flag: bool = False) -> None:
    """Stream display chunks of text."""
    if raw_flag or not should_colorize(raw_flag):
        for chunk in generator:
            print(chunk, end="", flush=True)
    else:
        # Use buffered markdown renderer to prevent ANSI artifacts
        # Import here to avoid circular dependencies if any (though usually top-level is fine)
        from .markdown_renderer import StreamMarkdownRenderer
        renderer = StreamMarkdownRenderer()
        for chunk in generator:
            for rendered_part in renderer.process_chunk(chunk):
                print(rendered_part, end="", flush=True)
        
        # Flush remaining buffer
        remaining = renderer.flush()
        if remaining:
            print(remaining, end="", flush=True)

    print() # Newline at end
