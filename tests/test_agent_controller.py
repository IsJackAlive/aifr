"""Tests for agent_controller module."""
from __future__ import annotations

import pytest

from aifr.agent_controller import AgentType, detect_agent_type, get_agent_name, get_system_prompt


class TestDetectAgentType:
    """Tests for detect_agent_type function."""

    def test_default_agent(self) -> None:
        """Test default agent detection."""
        agent = detect_agent_type("What is Python?")
        assert agent == AgentType.DEFAULT

    def test_debugger_agent_error_keyword(self) -> None:
        """Test debugger agent with error keyword."""
        agent = detect_agent_type("Fix this error")
        assert agent == AgentType.DEBUGGER

    def test_debugger_agent_with_console(self) -> None:
        """Test debugger agent when console is used."""
        agent = detect_agent_type("What happened?", has_console=True)
        assert agent == AgentType.DEBUGGER

    def test_debugger_agent_traceback(self) -> None:
        """Test debugger agent with traceback keyword."""
        agent = detect_agent_type("Analyze this stack trace")
        assert agent == AgentType.DEBUGGER

    def test_creative_agent_story(self) -> None:
        """Test creative agent with story keyword."""
        agent = detect_agent_type("Napisz opowiadanie o kocie")
        assert agent == AgentType.CREATIVE

    def test_creative_agent_poem(self) -> None:
        """Test creative agent with poem keyword."""
        agent = detect_agent_type("Write me a poem")
        assert agent == AgentType.CREATIVE

    def test_summarizer_agent_explicit(self) -> None:
        """Test summarizer with explicit keyword."""
        agent = detect_agent_type("Podsumuj ten tekst")
        assert agent == AgentType.SUMMARIZER

    def test_summarizer_agent_short_prompt_with_file(self) -> None:
        """Test summarizer with short prompt and file."""
        agent = detect_agent_type("Co tu jest?", has_file=True)
        assert agent == AgentType.SUMMARIZER

    def test_summarizer_agent_large_file(self) -> None:
        """Test summarizer with large file."""
        agent = detect_agent_type("Analyze", has_file=True, file_size=5000)
        assert agent == AgentType.SUMMARIZER

    def test_coder_agent_with_file(self) -> None:
        """Test coder agent with code keyword and file."""
        agent = detect_agent_type("Review this kod", has_file=True)
        assert agent == AgentType.CODER

    def test_coder_agent_function(self) -> None:
        """Test coder agent with function keyword."""
        agent = detect_agent_type("Explain this funkcja", has_file=True)
        assert agent == AgentType.CODER

    def test_polish_keywords(self) -> None:
        """Test Polish language keyword detection."""
        # Debug
        assert detect_agent_type("Błąd w aplikacji") == AgentType.DEBUGGER
        
        # Creative
        assert detect_agent_type("Wymyśl historię") == AgentType.CREATIVE
        
        # Summarizer
        assert detect_agent_type("Streść dokument") == AgentType.SUMMARIZER


class TestGetSystemPrompt:
    """Tests for get_system_prompt function."""

    def test_get_default_prompt(self) -> None:
        """Test getting default system prompt."""
        prompt = get_system_prompt(AgentType.DEFAULT)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "asystentem" in prompt.lower()

    def test_get_debugger_prompt(self) -> None:
        """Test getting debugger system prompt."""
        prompt = get_system_prompt(AgentType.DEBUGGER)
        assert isinstance(prompt, str)
        assert "devops" in prompt.lower() or "błęd" in prompt.lower()

    def test_get_creative_prompt(self) -> None:
        """Test getting creative system prompt."""
        prompt = get_system_prompt(AgentType.CREATIVE)
        assert isinstance(prompt, str)
        assert "kreatywn" in prompt.lower() or "pisarz" in prompt.lower()

    def test_get_summarizer_prompt(self) -> None:
        """Test getting summarizer system prompt."""
        prompt = get_system_prompt(AgentType.SUMMARIZER)
        assert isinstance(prompt, str)
        assert "analizuj" in prompt.lower() or "punkt" in prompt.lower()

    def test_get_coder_prompt(self) -> None:
        """Test getting coder system prompt."""
        prompt = get_system_prompt(AgentType.CODER)
        assert isinstance(prompt, str)
        assert "kod" in prompt.lower() or "programow" in prompt.lower()


class TestGetAgentName:
    """Tests for get_agent_name function."""

    def test_all_agent_names(self) -> None:
        """Test getting names for all agent types."""
        names = {
            AgentType.DEFAULT: get_agent_name(AgentType.DEFAULT),
            AgentType.DEBUGGER: get_agent_name(AgentType.DEBUGGER),
            AgentType.CREATIVE: get_agent_name(AgentType.CREATIVE),
            AgentType.SUMMARIZER: get_agent_name(AgentType.SUMMARIZER),
            AgentType.CODER: get_agent_name(AgentType.CODER),
        }
        
        # All should return non-empty strings
        for agent_type, name in names.items():
            assert isinstance(name, str)
            assert len(name) > 0
        
        # All should be unique
        assert len(set(names.values())) == len(names)
