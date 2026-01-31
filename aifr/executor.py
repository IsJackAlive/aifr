"""
Shell execution module with safety guardrails.
"""
from __future__ import annotations

import re
import sys
import subprocess
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SafetyCheckResult:
    is_safe: bool
    warning: Optional[str] = None

class CommandParser:
    """Parses shell commands from LLM output."""
    
    def extract_commands(self, text: str) -> List[str]:
        """Extract content from ```bash or ```sh blocks."""
        # Regex to capture content between ```bash/sh and ```
        # Flags: dotall to match newlines
        pattern = re.compile(r"```(?:bash|sh|zsh)(.*?)```", re.DOTALL)
        
        matches = pattern.findall(text)
        cleaned_commands = []
        for match in matches:
            cmd = match.strip()
            if cmd:
                cleaned_commands.append(cmd)
                
        return cleaned_commands

class SafetyGuard:
    """Checks commands for dangerous patterns."""
    
    # Simple blacklist - can be expanded
    BLACKLIST = [
        r"rm\s+-[rRf]+\s+/",  # rm -rf /
        r"mkfs",              # formatting
        r"dd\s+if=",          # disk writing
        r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # fork bomb
        r">\s*/dev/sd[a-z]",  # writing to raw device
    ]
    
    def check(self, command: str) -> SafetyCheckResult:
        """Analyze command availability."""
        for pattern in self.BLACKLIST:
            if re.search(pattern, command):
                return SafetyCheckResult(False, f"Potentially dangerous command detected (pattern: {pattern})")
        return SafetyCheckResult(True)

class ShellExecutor:
    """Executes shell commands with confirmation."""
    
    def __init__(self) -> None:
        self.guard = SafetyGuard()
    
    def confirm_and_execute(self, commands: List[str]) -> None:
        """
        Interactive loop to confirm and execute commands.
        Requires TTY.
        """
        if not sys.stdout.isatty():
             # Fail silently or log? User requested TTY enforcement check in prompt.
             # "Pamiętaj o obsłudze TTY – jeśli stdout nie jest terminalem, tryb --exec powinien zostać zablokowany"
             sys.stderr.write("Error: Execution mode requires a TTY.\n")
             return

        for cmd in commands:
            self._process_command(cmd)

    def _process_command(self, cmd: str) -> None:
        """Handle single command flow."""
        # 1. Safety Check
        safety = self.guard.check(cmd)
        
        # 2. Display
        print(f"\n{self._format_box(cmd)}")
        if not safety.is_safe:
            # Coral/Red warning (retro style fallback)
            sys.stdout.write(f"\033[38;5;203m[WARNING] {safety.warning}\033[0m\n")
            
        # 3. Prompt
        try:
            choice = input("\nExecute this command? [Y/n/e] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return

        if choice == 'y' or choice == '':
            self.run_command(cmd)
        elif choice == 'e':
            # Simple edit simulation (prompt for new command)
            try:
                new_cmd = input("Enter modified command: ")
                if new_cmd.strip():
                    self._process_command(new_cmd)
            except (EOFError, KeyboardInterrupt):
                pass
        else:
            print("Skipped.")

    def run_command(self, cmd: str) -> int:
        """Run the command using subprocess."""
        print(f"Running: {cmd}\n---")
        try:
            result = subprocess.run(cmd, shell=True, text=True) # captured output is not requested by prompt ("Wynik w terminalu")
            # If prompt implied capturing for context ("send exit code back... if error"), 
            # we might want capture_output=True but print it manually to show user?
            # Prompt says "Wynik w terminalu" (Result in terminal).
            # subprocess.run(shell=True) naturally pipes to stdout/stderr unless redirected.
            # So this is safe and simplest.
            print(f"---\nExit code: {result.returncode}")
            return result.returncode
        except Exception as e:
            sys.stderr.write(f"Execution failed: {e}\n")
            return 1

    def _format_box(self, text: str) -> str:
        """Simple retro styling for command display."""
        border = "-" * 40
        return f"{border}\nPROPOSED COMMAND:\n{text}\n{border}"
