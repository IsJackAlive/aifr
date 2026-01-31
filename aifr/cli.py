"""Main CLI entry point for Aifr v1.1 with modern argparse."""
from __future__ import annotations

import sys
from typing import Iterator, Optional, Union

from .agent_controller import AgentType, detect_agent_type, get_agent_name, get_system_prompt
from .api import ApiError, ContextLengthError, LlmResponse, call_llm
from .cli_parser import CliArgs, parse_cli_args, validate_args
from .config import DEFAULT_CONTEXT_LIMIT, get_config
from .context import ContextManager
from .file_loader import FileTooLargeError, SensitiveFileError, UnsupportedFileError, load_file
from .gradient_display import print_version_banner
from .model_selector import get_all_models, get_large_context_model, is_supported, select_model
from .output import print_chunks, print_usage_summary, should_colorize, stream_display
from .session_store import clear_session, load_session, save_session
from .terminal_capture import get_console_context, read_stdin_early
from .rag import RAGEngine
import time
from pathlib import Path

__version__ = "1.3.0"



def resolve_model_alias(model_name: str, aliases: dict[str, str]) -> tuple[str, Optional[str]]:
    """
    Resolve model alias and detect provider override.
    
    Returns:
        (resolved_model_name, detected_provider)
        detected_provider is None if not found/overridden.
    """
    # 1. Check aliases
    if model_name in aliases:
        model_name = aliases[model_name]
    
    # 2. Check for provider prefix (e.g. "openai/gpt-4")
    if "/" in model_name:
        parts = model_name.split("/", 1)
        return parts[1], parts[0]
        
    return model_name, None


def resolve_agent_config(
    agent_name: Optional[str],
    custom_agents: Optional[dict[str, dict[str, str]]],
    default_provider: str,
    default_model: Optional[str],
    default_system_prompt: str
) -> tuple[str, Optional[str], str]:
    """
    Resolve effective provider, model, and system prompt based on agent configuration.
    
    Returns:
        (provider, model, system_prompt)
    """
    if not agent_name:
        return default_provider, default_model, default_system_prompt
        
    cfg = (custom_agents or {}).get(agent_name)
    if not cfg:
        sys.stderr.write(f"Warning: Custom agent '{agent_name}' not found in config. Using defaults.\n")
        return default_provider, default_model, default_system_prompt
        
    # Override values
    provider = cfg.get("provider", default_provider)
    model = cfg.get("model", default_model) # Can remain None if not set
    system_prompt = cfg.get("system_prompt", default_system_prompt)
    
    return provider, model, system_prompt


def build_user_message(
    prompt: str,
    file_paths: Optional[list[str]] = None,
    console_cmd: Optional[str] = None,
    stdin_data: Optional[str] = None,
) -> tuple[str, int]:
    """
    Build complete user message with context.
    
    Returns:
        (message, total_file_content_length) tuple
    """
    parts = [f"Pytanie: {prompt}"]
    total_len = 0
    
    if file_paths:
        for fpath in file_paths:
            content, path = load_file(fpath)
            total_len += len(content)
            parts.append(f"\nTreść pliku {path.name}:\n===FILE_START===\n{content}\n===FILE_END===\n")
    
    
    # Handle console command or stdin
    if console_cmd is not None or stdin_data:
        if console_cmd:
            # Execute command
            console_content = get_console_context(console_cmd)
        else:
            # Use stdin data
            console_content = stdin_data
        
        if console_content:
            parts.append(f"\nOutput polecenia:\n===CONSOLE_START===\n{console_content}\n===CONSOLE_END===\n")
        else:
            parts.append("\n(Brak danych z konsoli)\n")
    
    if len(parts) == 1:
        return prompt, total_len
    return "\n".join(parts), total_len


def process_request(
    args: CliArgs,
    ctx: ContextManager,
    cfg_context_limit: int,
    cfg_model: Optional[str],
    api_key: str,
    provider: str = "sherlock",
    base_url: Optional[str] = None,
    stdin_data: Optional[str] = None,
    model_aliases: Optional[dict[str, str]] = None,
    custom_agents: Optional[dict[str, dict[str, str]]] = None,
) -> int:
    """
    Process a single user request.
    
    Returns:
        Exit code (0=success, 1=error)
    """
    if not args.prompt:
        sys.stderr.write("Error: Prompt is required\n")
        return 1
    
    # RAG Context retrieval
    rag_context = ""
    rag_duration_ms = 0.0
    
    if args.rag:
        try:
            start_t = time.perf_counter()
            if args.directory == "." or not args.directory:
                scan_dir = Path(".")
            else:
                scan_dir = Path(args.directory)
            
            sys.stderr.write(f"[*] Scanning context in {scan_dir}...\n")
            engine = RAGEngine()
            engine.index_files(scan_dir)
            results = engine.search(args.prompt, k=3)
            
            if results:
                rag_parts = []
                for res in results:
                    # Compress content logic is inside RAGEngine or separate?
                    # RAGEngine uses ContextCompressor internally? No, RAGEngine has one.
                    # RAGEngine search returns DocumentChunk. which has full content.
                    # We should compress it here or use engine helper.
                    # The plan said "Append compressed top-3 results".
                    # Let's compress here using engine's compressor if public, or create one.
                    # engine.compressor is public in my implementation.
                    compressed = engine.compressor.compress(res.content, res.file_path)
                    rag_parts.append(f"--- {res.file_path} ---\n{compressed}")
                
                rag_context = "\n".join(rag_parts)
                sys.stderr.write(f"[*] Found {len(results)} relevant fragments.\n")
            
            rag_duration_ms = (time.perf_counter() - start_t) * 1000
        except Exception as e:
            sys.stderr.write(f"Warning: RAG failed: {e}\n")

    # Build user message
    try:
        user_message, file_content_length = build_user_message(
            prompt=args.prompt,
            file_paths=args.file,
            console_cmd=args.console,
            stdin_data=stdin_data,
        )
        
        if rag_context:
            user_message = (
                f"Use the following code context to answer the question:\n\n"
                f"{rag_context}\n\n"
                f"Question:\n{user_message}"
            )
            # Adjust length estimation if needed, though mostly for file warnings
            if file_content_length is None:
                file_content_length = len(rag_context)
            else:
                file_content_length += len(rag_context)
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
    
    # Update context limit if specified
    context_limit = args.context_limit or cfg_context_limit or DEFAULT_CONTEXT_LIMIT
    ctx.max_tokens = context_limit
    ctx.enforce_limit()
    
    # Detect agent type and get appropriate system prompt
    agent_type = detect_agent_type(
        prompt=args.prompt,
        has_console=bool(args.console or stdin_data),
        has_file=bool(args.file),
        file_size=file_content_length,
    )
    system_prompt = get_system_prompt(agent_type)
    
    # Select model
    # 0. Custom Agent Override
    provider, args.model, system_prompt = resolve_agent_config(
        args.agent,
        custom_agents,
        provider,
        args.model or cfg_model, # Initial model candidate
        system_prompt
    )
    # Update cfg_model to reflect potential change if args.model was updated (for logic below)
    # Actually args.model is what matters for select_model
    requested_model = args.model
    
    # 2. Resolve alias/provider if model is requested
    if requested_model:
        requested_model, detected_provider = resolve_model_alias(requested_model, model_aliases or {})
        if detected_provider:
             provider = detected_provider
    
    # 3. Final selection logic (handles auto-selection if requested_model is None)
    model = select_model(args.prompt, requested_model, bool(args.file))
    
    if not is_supported(model) and not requested_model: # Warn only if auto-selected unsuppported (unlikely)
         pass # Actually we trust select_model, but if user provided custom model we skip check
    
    if requested_model and not is_supported(model):
        # Allow custom models via flag/alias without warning
        pass
    elif not is_supported(model):
        sys.stderr.write(f"Ostrzeżenie: model {model} nie jest na liście wspieranych, używam mimo to\n")
    
    # Build messages for API
    messages = ctx.build_messages(system_prompt, user_message)
    
    # Call LLM API
    reply_or_iter: Union[LlmResponse, Iterator[LlmResponse]]
    try:
        reply_or_iter = call_llm(
            api_key=api_key,
            model=model,
            messages=messages,
            provider_name=provider,
            base_url=base_url,
            stream=True,
        )
    except ContextLengthError as exc:
        # Fallback to large context model
        large_model = get_large_context_model()
        sys.stderr.write(f"Kontekst przekracza limit modelu {model}\n")
        sys.stderr.write(f"Przełączam na model {large_model} z większym oknem kontekstu...\n")
        try:
            reply_or_iter = call_llm(
                api_key=api_key,
                model=large_model,
                messages=messages,
                provider_name=provider,
                base_url=base_url,
                stream=True,
            )
        except ApiError as retry_exc:
            sys.stderr.write(f"Błąd API nawet z dużym modelem: {retry_exc}\n")
            return 1
    except ApiError as exc:
        sys.stderr.write(f"Błąd API: {exc}\n")
        return 1
    
    # Process response (Stream or Single)
    final_content = ""
    # Use default model/stats, allowing override from stream
    final_model = model
    final_prompt_tokens = None
    final_completion_tokens = None
    final_total_tokens = None

    if isinstance(reply_or_iter, Iterator):
        # Generator for stream_display
        def content_generator() -> Iterator[str]:
            nonlocal final_content, final_model, final_prompt_tokens, final_completion_tokens, final_total_tokens
            for chunk in reply_or_iter:
                # Update metadata if present
                if chunk.model:
                    final_model = chunk.model
                if chunk.prompt_tokens is not None:
                    final_prompt_tokens = chunk.prompt_tokens
                if chunk.completion_tokens is not None:
                    final_completion_tokens = chunk.completion_tokens
                if chunk.total_tokens is not None:
                    final_total_tokens = chunk.total_tokens
                
                # Yield content
                if chunk.content:
                    final_content += chunk.content
                    yield chunk.content
        
        stream_display(content_generator(), raw_flag=args.raw)
    else:
        # Single response
        final_content = reply_or_iter.content
        final_model = reply_or_iter.model
        final_prompt_tokens = reply_or_iter.prompt_tokens
        final_completion_tokens = reply_or_iter.completion_tokens
        final_total_tokens = reply_or_iter.total_tokens
        print_chunks(final_content, raw_flag=args.raw)
    
    # Show stats if requested
    if args.stats:
        sys.stderr.write(f"\n--- Statistics ---\n")
        sys.stderr.write(f"Agent: {get_agent_name(agent_type)}\n")
        sys.stderr.write(f"Model: {final_model}\n")
        sys.stderr.write(f"Tokens: {final_prompt_tokens} in / {final_completion_tokens} out / {final_total_tokens} total\n")
        if rag_duration_ms > 0:
            sys.stderr.write(f"RAG search time: {rag_duration_ms:.2f}ms\n")
        sys.stderr.write(f"Context window: {len(ctx.messages)} messages, {ctx.max_turns} max turns\n")
    else:
        # Default: just show model and tokens (legacy behavior)
        print_usage_summary(
            final_model,
            final_prompt_tokens,
            final_completion_tokens,
            final_total_tokens,
        )
    
    # Save context
    ctx.add_turn(user_message, final_content)
    save_session(ctx.max_tokens, ctx.messages)
    
    return 0


def main() -> None:
    """Main entry point."""
    # Read stdin early (before argparse potentially reads it)
    stdin_data = read_stdin_early()
    has_stdin = stdin_data is not None
    
    # Parse arguments
    try:
        args = parse_cli_args()
    except SystemExit as e:
        # argparse calls sys.exit on error or --help
        sys.exit(e.code if e.code is not None else 0)
    
    # Handle version flag
    if args.version:
        if should_colorize(args.raw):
            print_version_banner(__version__)
        else:
            print(f"Aifr v{__version__}")
        sys.exit(0)
    
    # Handle list-models flag
    if args.list_models:
        print("Dostępne modele:")
        for model in get_all_models():
            print(f"  - {model}")
        sys.exit(0)
    
    # Validate arguments
    is_valid, error_msg = validate_args(args, has_stdin)
    if not is_valid:
        sys.stderr.write(f"{error_msg}\n")
        sys.exit(1)
    
    # Load config
    try:
        cfg = get_config()
    except RuntimeError as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(1)
    
    # Handle session reset
    if args.reset:
        clear_session()
        sys.stderr.write("✓ Session cleared\n")
        # If only --reset was specified, exit
        if not args.prompt and not stdin_data:
            sys.exit(0)
    
    # Load or create context manager
    loaded_max, loaded_messages = load_session()
    ctx = ContextManager(loaded_max or cfg.context_limit, messages=loaded_messages)
    ctx.enforce_limit()
    
    # Interactive mode
    if args.interactive or (not args.prompt and not stdin_data):
        sys.stderr.write("Aifr - Interactive mode (type 'exit' or Ctrl+D to quit)\n")
        sys.stderr.write("New syntax: Just type your question (no $ask: needed)\n")
        sys.stderr.write("Flags: Use -f file.txt, -c 'command', --reset, --stats\n\n")
        
        while True:
            try:
                prompt = input("aifr> ")
            except (EOFError, KeyboardInterrupt):
                print()  # Newline
                break
            
            if not prompt.strip():
                continue
            if prompt.strip().lower() in {"exit", "quit"}:
                break
            
            # Create args for this interactive command
            interactive_args = CliArgs(
                prompt=prompt,
                file=None,
                console=None,
                model=args.model,
                context_limit=args.context_limit,
                reset=False,
                stats=args.stats,
                version=False,
                interactive=True,
                list_models=False,
                agent=None,
                raw=False,
                rag=args.rag,
                directory=args.directory,
            )
            
            process_request(
                interactive_args,
                ctx,
                cfg.context_limit,
                cfg.model,
                cfg.api_key,
                cfg.provider,
                cfg.base_url,
                None,
                model_aliases=cfg.model_aliases,
                custom_agents=cfg.custom_agents,
            )
        
        sys.exit(0)
    
    # Single command mode
    # If we have stdin but no explicit prompt, treat stdin as context with prompt from args
    if stdin_data and not args.prompt:
        sys.stderr.write("Error: When piping data, you must provide a prompt\n")
        sys.exit(1)
    
    exit_code = process_request(
        args,
        ctx,
        cfg.context_limit,
        cfg.model,
        cfg.api_key,
        cfg.provider,
        cfg.base_url,
        stdin_data,
        model_aliases=cfg.model_aliases,
        custom_agents=cfg.custom_agents,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
