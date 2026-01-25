from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# Sliding window configuration
DEFAULT_MAX_TURNS = 5  # Keep last N conversation turns (1 turn = user + assistant)


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ContextManager:
    max_tokens: int
    messages: List[Message] = field(default_factory=list)
    max_turns: int = DEFAULT_MAX_TURNS  # New: limit conversation history

    def add_turn(self, user_message: str, assistant_message: str) -> None:
        self.messages.append(Message(role="user", content=user_message))
        self.messages.append(Message(role="assistant", content=assistant_message))
        self._apply_sliding_window()
        self._prune_by_tokens()

    def build_messages(self, system_prompt: str, user_message: str) -> List[Dict[str, str]]:
        payload: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        payload.extend({"role": m.role, "content": m.content} for m in self.messages)
        payload.append({"role": "user", "content": user_message})
        return payload

    def enforce_limit(self) -> None:
        """Enforce both sliding window and token limits."""
        self._apply_sliding_window()
        self._prune_by_tokens()

    def _apply_sliding_window(self) -> None:
        """
        Keep only the last N turns (sliding window).
        Each turn = 1 user message + 1 assistant message = 2 messages.
        This prevents unbounded context growth.
        """
        max_messages = self.max_turns * 2  # Each turn has 2 messages
        if len(self.messages) > max_messages:
            # Keep only the most recent messages
            self.messages = self.messages[-max_messages:]

    def _prune_by_tokens(self) -> None:
        """
        Additional pruning based on token count (legacy behavior).
        Only kicks in if sliding window isn't enough.
        """
        while self._token_count() > self.max_tokens and len(self.messages) > 2:
            # Remove oldest turn (2 messages at a time)
            self.messages.pop(0)
            self.messages.pop(0)

    def _token_count(self) -> int:
        """Approximate token count by word count."""
        return sum(len(m.content.split()) for m in self.messages)

    def clear(self) -> None:
        """Clear all conversation history."""
        self.messages.clear()
