from __future__ import annotations

import subprocess
import sys
from typing import Optional


class CommandExecutionError(Exception):
    pass


def execute_command(command: str, timeout: int = 30) -> str:
    """
    Execute a shell command and capture its output (stdout + stderr).
    
    Args:
        command: Shell command to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        String containing command output
        
    Raises:
        CommandExecutionError: If command execution fails
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        # Combine stdout and stderr
        output_parts = []
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr}")
        
        output = "\n\n".join(output_parts) if output_parts else "(polecenie nie zwróciło żadnego outputu)"
        
        if result.returncode != 0:
            output = f"Exit code: {result.returncode}\n\n{output}"
        
        return output
            
    except subprocess.TimeoutExpired:
        raise CommandExecutionError(f"Polecenie przekroczyło limit czasu ({timeout}s)")
    except Exception as exc:
        raise CommandExecutionError(f"Błąd podczas wykonywania polecenia: {exc}")


def read_stdin_early() -> Optional[str]:
    """
    Read input from stdin if available (pipe input).
    MUST be called early, before any input() or other stdin operations.
    Returns None if stdin is a terminal (no pipe).
    """
    if sys.stdin.isatty():
        # stdin is a terminal, not a pipe
        return None
    
    try:
        # Ensure UTF-8 encoding for stdin
        if hasattr(sys.stdin, 'buffer'):
            # Read raw bytes and decode as UTF-8
            content = sys.stdin.buffer.read().decode('utf-8', errors='replace')
        else:
            # Fallback for systems without buffer attribute
            content = sys.stdin.read()
        return content.strip() if content.strip() else None
    except Exception:
        return None


def get_console_context(command: str) -> Optional[str]:
    """
    Execute a shell command and capture its output.
    
    Args:
        command: Shell command to execute
        
    Returns:
        Command output or error message
    """
    try:
        return execute_command(command)
    except CommandExecutionError as exc:
        return f"Błąd wykonania polecenia: {exc}"
