from __future__ import annotations

import sys
from typing import Optional

from .api import ApiError, ContextLengthError, LlmResponse, call_llm
from .command_parser import Command, CommandError, parse_command
from .config import DEFAULT_CONTEXT_LIMIT, SYSTEM_PROMPT, get_config
from .context import ContextManager
from .file_loader import FileTooLargeError, SensitiveFileError, UnsupportedFileError, load_file
from .model_selector import get_large_context_model, is_supported, select_model
from .output import print_chunks, print_usage_summary
from .session_store import clear_session, load_session, save_session
from .terminal_capture import get_console_context, read_stdin_early

__version__ = "1.0.0"


def build_user_message(command: Command, stdin_data: Optional[str] = None) -> str:
    parts = [f"Pytanie: {command.ask}"]
    
    if command.file:
        content, path = load_file(command.file)
        parts.append(f"\nTreść pliku {path.name}:\n===FILE_START===\n{content}\n===FILE_END===\n")
    
    if command.console is not None:
        # Console: "" = read from stdin, "cmd" = execute cmd
        if command.console == "":
            # Read from stdin
            console_content = stdin_data
        else:
            # Execute command
            console_content = get_console_context(command.console)
        
        if console_content:
            parts.append(f"\nOutput polecenia:\n===CONSOLE_START===\n{console_content}\n===CONSOLE_END===\n")
        else:
            parts.append("\n(Brak danych z konsoli - użyj $cons: \"polecenie\" lub przekieruj output przez pipe)\n")
    
    if len(parts) == 1:
        return command.ask
    return "\n".join(parts)


def process_command(raw: str, ctx: ContextManager, cfg_context_limit: int, cfg_model: Optional[str], api_key: str, stdin_data: Optional[str] = None) -> int:
    """Process a command and return exit code (0=success, 1=error)."""
    try:
        command = parse_command(raw)
    except CommandError as exc:
        sys.stderr.write(f"Błąd polecenia: {exc}\n")
        return 1

    try:
        user_message = build_user_message(command, stdin_data)
    except FileTooLargeError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    except UnsupportedFileError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    except SensitiveFileError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    except FileNotFoundError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    context_limit = command.context_limit or cfg_context_limit or DEFAULT_CONTEXT_LIMIT
    ctx.max_tokens = context_limit
    ctx.enforce_limit()

    model = select_model(command.ask, command.model or cfg_model, bool(command.file))
    if not is_supported(model):
        sys.stderr.write(f"Ostrzeżenie: model {model} nie jest na liście wspieranych, używam mimo to\n")

    messages = ctx.build_messages(SYSTEM_PROMPT, user_message)

    reply: LlmResponse
    try:
        reply = call_llm(api_key=api_key, model=model, messages=messages)
    except ContextLengthError as exc:
        # Fallback to large context model
        large_model = get_large_context_model()
        sys.stderr.write(f"⚠ Kontekst przekracza limit modelu {model}\n")
        sys.stderr.write(f"🔄 Przełączam na model {large_model} z większym oknem kontekstu...\n")
        try:
            reply = call_llm(api_key=api_key, model=large_model, messages=messages)
        except ApiError as retry_exc:
            sys.stderr.write(f"Błąd API nawet z dużym modelem: {retry_exc}\n")
            return 1
    except ApiError as exc:
        sys.stderr.write(f"Błąd API: {exc}\n")
        return 1

    print_chunks(reply.content)
    print_usage_summary(
        reply.model,
        reply.prompt_tokens,
        reply.completion_tokens,
        reply.total_tokens,
    )
    ctx.add_turn(user_message, reply.content)
    save_session(ctx.max_tokens, ctx.messages)
    return 0


def show_help() -> None:
    """Display help information."""
    help_text = """Aifr - Terminal LLM Assistant

Usage:
  aifr $ask: <pytanie>                    # Zadaj pytanie
  aifr $ask: <pytanie> $file: <ścieżka>   # Dołącz plik do kontekstu
  aifr $ask: <pytanie> $cons: <polecenie> # Wykonaj polecenie i dołącz output
  aifr $ask: <pytanie> $model: <nazwa>    # Wybierz konkretny model
  aifr --help                             # Wyświetl pomoc
  aifr --version                          # Wyświetl wersję
  aifr --reset-context                    # Wyczyść historię konwersacji

Examples:
  aifr $ask: Co to jest Python?
  aifr $ask: Podsumuj ten plik $file: README.md
  echo "some data" | aifr $ask: Przeanalizuj dane z pipe
  aifr $ask: Co jest nie tak? $cons: "pytest tests/"

Dokumentacja: https://github.com/IsJackAlive/aifr
"""
    print(help_text)


def main() -> None:
    # Handle --help and --version early
    argv = sys.argv[1:]
    
    if "--help" in argv or "-h" in argv:
        show_help()
        sys.exit(0)
    
    if "--version" in argv or "-v" in argv:
        print(f"aifr {__version__}")
        sys.exit(0)
    
    # Read stdin early if piped (before any input() calls)
    stdin_data = read_stdin_early()
    
    try:
        cfg = get_config()
    except RuntimeError as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(1)

    loaded_max, loaded_messages = load_session()
    ctx = ContextManager(loaded_max or cfg.context_limit, messages=loaded_messages)
    ctx.enforce_limit()

    if "--reset-context" in argv:
        clear_session()
        print("Kontekst wyczyszczony.")
        argv = [arg for arg in argv if arg != "--reset-context"]

    if argv:
        exit_code = process_command(" ".join(argv), ctx, cfg.context_limit, cfg.model, cfg.api_key, stdin_data)
        sys.exit(exit_code)

    print("Aifr assistant uruchomiony. Wpisz polecenie w formacie 'aifr $ask: <pytanie> $file: <ścieżka>' albo samo pytanie. 'exit' kończy.")
    while True:
        try:
            raw = input("aifr> ")
        except EOFError:
            break
        if not raw.strip():
            continue
        if raw.strip().lower() in {"exit", "quit"}:
            break
        # stdin_data only available on first command from pipe
        process_command(raw, ctx, cfg.context_limit, cfg.model, cfg.api_key, stdin_data)
        stdin_data = None  # Clear after first use
    
    sys.exit(0)

if __name__ == "__main__":
    main()
