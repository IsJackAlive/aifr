"""Modern CLI argument parser using argparse for Aifr v1.1."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class CliArgs:
    """Structured CLI arguments."""
    prompt: Optional[str]
    file: Optional[list[str]]
    console: Optional[str]
    model: Optional[str]
    context_limit: Optional[int]
    reset: bool
    stats: bool
    version: bool
    interactive: bool
    list_models: bool
    agent: Optional[str]
    raw: bool
    rag: bool
    directory: str
    exec_mode: bool


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="aifr",
        description="Aifr - Terminal LLM Assistant",
        epilog="Examples:\n"
               "  aifr 'What is Python?'\n"
               "  aifr -f README.md 'Summarize this file'\n"
               "  aifr -c 'ls -la' 'What files are here?'\n"
               "  cat file.txt | aifr 'Analyze this'\n"
               "  aifr --reset 'Start fresh conversation'\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Positional argument for prompt (optional)
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Question/prompt for the LLM (can also use -p/--prompt)",
    )
    
    # File input
    # File input
    parser.add_argument(
        "--rag",
        action="store_true",
        help="Enable Retrieval-Augmented Generation for context",
    )
    
    parser.add_argument(
        "-d", "--directory",
        metavar="PATH",
        default=".",
        help="Root directory for RAG scanning (default: .)",
    )

    parser.add_argument(
        "--exec",
        action="store_true",
        help="Execute shell commands from response (implies --interactive)",
    )

    parser.add_argument(
        "-f", "--file",
        metavar="PATH",
        action="append",
        help="Path to file(s) to include in context (.txt/.md, max 5MB)",
    )
    
    # Console/shell command execution
    parser.add_argument(
        "-c", "--console", "--cmd",
        metavar="COMMAND",
        help="Shell command to execute and analyze output",
    )
    
    # Explicit prompt flag (alternative to positional)
    parser.add_argument(
        "-p", "--prompt-flag", "--ask",
        dest="prompt_flag",
        metavar="TEXT",
        help="Explicit prompt text (alternative to positional argument)",
    )
    
    # Model selection
    parser.add_argument(
        "-m", "--model",
        metavar="NAME",
        help="Force specific model (e.g., 'gpt-4', 'Bielik-11B-v2.6')",
    )
    
    # Context limit
    parser.add_argument(
        "--context-limit",
        type=int,
        metavar="N",
        help="Maximum context window size in tokens",
    )
    
    # Session management
    parser.add_argument(
        "--reset", "--new",
        action="store_true",
        help="Clear session history and start fresh conversation",
    )
    
    # Observability
    parser.add_argument(
        "--stats", "--info",
        action="store_true",
        help="Show model, tokens, and usage statistics (on stderr)",
    )
    
    # Version
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version and exit",
    )
    
    # List models
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Show all available models and exit",
    )
    
    # Custom Agent
    parser.add_argument(
        "--agent",
        metavar="NAME",
        help="Activate custom agent from config (e.g. 'code', 'docs')",
    )

    # Raw Output
    parser.add_argument(
        "--raw", "-r",
        action="store_true",
        help="Force raw output (no markdown/colors)",
    )
    
    # Interactive mode flag (internal)
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help=argparse.SUPPRESS,  # Hidden flag
    )
    
    return parser


def parse_cli_args(argv: Optional[list[str]] = None) -> CliArgs:
    """
    Parse CLI arguments into structured format.
    
    Args:
        argv: Arguments to parse (defaults to sys.argv[1:])
        
    Returns:
        CliArgs object with parsed arguments
        
    Raises:
        SystemExit: If arguments are invalid (argparse default behavior)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Combine positional prompt with flag prompt
    prompt = args.prompt_flag or args.prompt
    
    return CliArgs(
        prompt=prompt,
        file=args.file,
        console=args.console,
        model=args.model,
        context_limit=args.context_limit,
        reset=args.reset,
        stats=args.stats,
        version=args.version,
        interactive=args.interactive,
        list_models=args.list_models,
        agent=args.agent,
        raw=args.raw,
        rag=args.rag,
        directory=args.directory,
        exec_mode=args.exec,
    )


def validate_args(args: CliArgs, has_stdin: bool) -> tuple[bool, Optional[str]]:
    """
    Validate parsed arguments.
    
    Args:
        args: Parsed CLI arguments
        has_stdin: Whether stdin data is available
        
    Returns:
        (is_valid, error_message) tuple
    """
    # If no prompt and no stdin, we need prompt in interactive mode
    if not args.prompt and not has_stdin and not args.interactive:
        # Allow if it's just --reset, --version, or --list-models
        if args.reset or args.version or args.list_models:
            return (True, None)
        return (False, "Error: prompt required (provide as argument or use -p/--prompt)")
    
    return (True, None)
