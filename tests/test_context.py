"""Tests for context management with sliding window."""
from __future__ import annotations

import pytest

from aifr.context import ContextManager, Message


class TestContextManagerSlidingWindow:
    """Tests for sliding window functionality."""

    def test_sliding_window_limits_turns(self) -> None:
        """Test that sliding window limits conversation turns."""
        ctx = ContextManager(max_tokens=10000, max_turns=3)
        
        # Add 5 turns (10 messages)
        for i in range(5):
            ctx.add_turn(f"User message {i}", f"Assistant response {i}")
        
        # Should keep only last 3 turns (6 messages)
        assert len(ctx.messages) == 6
        
        # Verify it's the most recent messages
        assert "User message 2" in ctx.messages[0].content
        assert "Assistant response 4" in ctx.messages[-1].content

    def test_sliding_window_preserves_recent_messages(self) -> None:
        """Test that sliding window keeps most recent messages."""
        ctx = ContextManager(max_tokens=10000, max_turns=2)
        
        ctx.add_turn("First user", "First assistant")
        ctx.add_turn("Second user", "Second assistant")
        ctx.add_turn("Third user", "Third assistant")
        
        # Should have only last 2 turns (4 messages)
        assert len(ctx.messages) == 4
        assert "Second user" in ctx.messages[0].content
        assert "Third assistant" in ctx.messages[-1].content
        assert not any("First" in m.content for m in ctx.messages)

    def test_clear_removes_all_messages(self) -> None:
        """Test that clear() removes all messages."""
        ctx = ContextManager(max_tokens=10000)
        
        ctx.add_turn("User 1", "Assistant 1")
        ctx.add_turn("User 2", "Assistant 2")
        assert len(ctx.messages) > 0
        
        ctx.clear()
        assert len(ctx.messages) == 0

    def test_enforce_limit_applies_sliding_window(self) -> None:
        """Test that enforce_limit applies sliding window."""
        ctx = ContextManager(max_tokens=10000, max_turns=2)
        
        # Add messages directly (bypass sliding window initially)
        for i in range(10):
            ctx.messages.append(Message(role="user", content=f"Message {i}"))
        
        assert len(ctx.messages) == 10
        
        # Enforce limit should apply sliding window
        ctx.enforce_limit()
        
        # Should keep only 2 turns worth = 4 messages
        assert len(ctx.messages) == 4

    def test_token_pruning_still_works(self) -> None:
        """Test that token-based pruning still works as fallback."""
        # Create context with low token limit
        ctx = ContextManager(max_tokens=50, max_turns=10)
        
        # Add messages with many words
        ctx.add_turn("word " * 100, "response " * 100)  # Exceeds token limit
        ctx.add_turn("User 2", "Assistant 2")
        
        # Token-based pruning should kick in
        token_count = ctx._token_count()
        assert token_count <= 50

    def test_default_max_turns(self) -> None:
        """Test default max_turns value."""
        ctx = ContextManager(max_tokens=10000)
        assert ctx.max_turns == 5  # DEFAULT_MAX_TURNS

    def test_build_messages_includes_system_and_current(self) -> None:
        """Test that build_messages includes system prompt and current message."""
        ctx = ContextManager(max_tokens=10000, max_turns=2)
        ctx.add_turn("Old user", "Old assistant")
        
        messages = ctx.build_messages("System prompt", "New user message")
        
        # Should have: system + old turn (2 msgs) + new user message
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System prompt"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "New user message"
