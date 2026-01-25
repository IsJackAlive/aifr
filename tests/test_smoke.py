"""Unit tests should pass successfully."""
from aifr.command_parser import parse_command

def test_basic_parsing() -> None:
    """Smoke test to verify tests can run."""
    cmd = parse_command("$ask: Test question")
    assert cmd.ask == "Test question"
    assert cmd.file is None
