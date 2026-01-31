"""Tests for new CLI parser (v1.1)."""
from __future__ import annotations

import pytest

from aifr.cli_parser import CliArgs, parse_cli_args, validate_args


class TestParseCliArgs:
    """Tests for parse_cli_args function."""

    def test_positional_prompt(self) -> None:
        """Test parsing positional prompt."""
        args = parse_cli_args(["What is Python?"])
        assert args.prompt == "What is Python?"
        assert args.file is None
        assert args.console is None
        assert args.reset is False
        assert args.stats is False

    def test_explicit_prompt_flag(self) -> None:
        """Test parsing with -p flag."""
        args = parse_cli_args(["-p", "What is Python?"])
        assert args.prompt == "What is Python?"

    def test_file_flag(self) -> None:
        """Test parsing with -f flag."""
        args = parse_cli_args(["Test", "-f", "readme.md"])
        assert args.prompt == "Test"
        assert args.file == ["readme.md"]

    def test_console_flag(self) -> None:
        """Test parsing with -c flag."""
        args = parse_cli_args(["Analyze", "-c", "ls -la"])
        assert args.prompt == "Analyze"
        assert args.console == "ls -la"

    def test_model_flag(self) -> None:
        """Test parsing with -m flag."""
        args = parse_cli_args(["Test", "-m", "gpt-4"])
        assert args.prompt == "Test"
        assert args.model == "gpt-4"

    def test_reset_flag(self) -> None:
        """Test parsing --reset flag."""
        args = parse_cli_args(["--reset", "New session"])
        assert args.reset is True
        assert args.prompt == "New session"

    def test_stats_flag(self) -> None:
        """Test parsing --stats flag."""
        args = parse_cli_args(["Test", "--stats"])
        assert args.stats is True

    def test_version_flag(self) -> None:
        """Test parsing --version flag."""
        args = parse_cli_args(["--version"])
        assert args.version is True

    def test_combined_flags(self) -> None:
        """Test parsing multiple flags together."""
        args = parse_cli_args([
            "Summarize",
            "-f", "doc.txt",
            "-m", "Bielik-11B",
            "--stats",
            "--context-limit", "8000"
        ])
        assert args.prompt == "Summarize"
        assert args.file == ["doc.txt"]
        assert args.model == "Bielik-11B"
        assert args.stats is True
        assert args.context_limit == 8000

    def test_prompt_flag_overrides_positional(self) -> None:
        """Test that -p flag takes precedence over positional."""
        args = parse_cli_args(["ignored", "-p", "actual prompt"])
        assert args.prompt == "actual prompt"


class TestValidateArgs:
    def test_valid_with_prompt(self):
        args = CliArgs(
            prompt="Hello",
            file=None,
            console=None,
            model=None,
            context_limit=None,
            reset=False,
            stats=False,
            version=False,
            interactive=False,
            list_models=False,
            agent=None,
            raw=False,
            rag=False,
            directory=".",
        )
        is_valid, _ = validate_args(args, has_stdin=False)
        assert is_valid

    def test_valid_with_stdin(self):
        args = CliArgs(
            prompt="Summarize this",  # Prompt required even with stdin
            file=None,
            console=None,
            model=None,
            context_limit=None,
            reset=False,
            stats=False,
            version=False,
            interactive=False,
            list_models=False,
            agent=None,
            raw=False,
            rag=False,
            directory=".",
        )
        is_valid, _ = validate_args(args, has_stdin=True)
        assert is_valid

    def test_invalid_no_prompt_no_stdin(self):
        args = CliArgs(
            prompt=None,
            file=None,
            console=None,
            model=None,
            context_limit=None,
            reset=False,
            stats=False,
            version=False,
            interactive=False,
            list_models=False,
            agent=None,
            raw=False,
            rag=False,
            directory=".",
        )
        is_valid, msg = validate_args(args, has_stdin=False)
        assert not is_valid
        assert "Error: prompt required" in msg

    def test_valid_reset_only(self):
        args = CliArgs(
            prompt=None,
            file=None,
            console=None,
            model=None,
            context_limit=None,
            reset=True,
            stats=False,
            version=False,
            interactive=False,
            list_models=False,
            agent=None,
            raw=False,
            rag=False,
            directory=".",
        )
        is_valid, _ = validate_args(args, has_stdin=False)
        assert is_valid

    def test_valid_version_only(self):
        args = CliArgs(
            prompt=None,
            file=None,
            console=None,
            model=None,
            context_limit=None,
            reset=False,
            stats=False,
            version=True,
            interactive=False,
            list_models=False,
            agent=None,
            raw=False,
            rag=False,
            directory=".",
        )
        is_valid, _ = validate_args(args, has_stdin=False)
        assert is_valid is True
