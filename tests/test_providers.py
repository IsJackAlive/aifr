"""Tests for API providers."""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from requests import Response

from aifr.providers import (
    ApiError,
    BraveProvider,
    ContextLengthError,
    LlmResponse,
    OpenAIProvider,
    OpenWebUIProvider,
    SherlockProvider,
    create_provider,
)


class TestSherlockProvider:
    """Tests for Sherlock API provider."""

    def test_successful_call(self) -> None:
        """Test successful API call."""
        provider = SherlockProvider(api_key="test-key")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "model": "Llama-3.1-8B",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        
        with patch("requests.post", return_value=mock_response):
            result = provider.call("Llama-3.1-8B", [{"role": "user", "content": "test"}])
        
        assert isinstance(result, LlmResponse)
        assert result.content == "Test response"
        assert result.model == "Llama-3.1-8B"
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20
        assert result.total_tokens == 30

    def test_context_length_error(self) -> None:
        """Test context length exceeded error."""
        provider = SherlockProvider(api_key="test-key")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = "maximum context length exceeded"
        
        with patch("requests.post", return_value=mock_response):
            with pytest.raises(ContextLengthError):
                provider.call("test-model", [{"role": "user", "content": "test"}])

    def test_api_error(self) -> None:
        """Test generic API error."""
        provider = SherlockProvider(api_key="test-key")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        
        with patch("requests.post", return_value=mock_response):
            with pytest.raises(ApiError, match="Sherlock API błąd 500"):
                provider.call("test-model", [{"role": "user", "content": "test"}])


class TestOpenAIProvider:
    """Tests for OpenAI API provider."""

    def test_successful_call(self) -> None:
        """Test successful API call."""
        provider = OpenAIProvider(api_key="sk-test-key")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "OpenAI response"}}],
            "model": "gpt-4",
            "usage": {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40},
        }
        
        with patch("requests.post", return_value=mock_response):
            result = provider.call("gpt-4", [{"role": "user", "content": "test"}])
        
        assert result.content == "OpenAI response"
        assert result.model == "gpt-4"
        assert result.prompt_tokens == 15
        assert result.completion_tokens == 25

    def test_context_length_exceeded(self) -> None:
        """Test OpenAI context_length_exceeded error."""
        provider = OpenAIProvider(api_key="sk-test-key")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"code": "context_length_exceeded", "message": "Too many tokens"}
        }
        mock_response.text = "Context length exceeded"
        
        with patch("requests.post", return_value=mock_response):
            with pytest.raises(ContextLengthError):
                provider.call("gpt-4", [{"role": "user", "content": "test"}])


class TestOpenWebUIProvider:
    """Tests for OpenWebUI provider."""

    def test_successful_call(self) -> None:
        """Test successful API call to OpenWebUI."""
        provider = OpenWebUIProvider(api_key="local-key", base_url="http://localhost:3000")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Local response"}}],
            "model": "granite3.1-dense:8b",
            "usage": {"prompt_tokens": 12, "completion_tokens": 18, "total_tokens": 30},
        }
        
        with patch("requests.post", return_value=mock_response):
            result = provider.call("granite3.1-dense:8b", [{"role": "user", "content": "test"}])
        
        assert result.content == "Local response"
        assert result.model == "granite3.1-dense:8b"
        assert result.prompt_tokens == 12

    def test_custom_base_url(self) -> None:
        """Test custom base URL is properly formatted."""
        provider = OpenWebUIProvider(api_key="key", base_url="http://custom:8080")
        assert provider.base_url == "http://custom:8080/api/chat/completions"
        
        # Test with trailing slash
        provider2 = OpenWebUIProvider(api_key="key", base_url="http://custom:8080/")
        assert provider2.base_url == "http://custom:8080/api/chat/completions"


class TestBraveProvider:
    """Tests for Brave Summarizer API provider."""

    def test_successful_call(self) -> None:
        """Test successful Brave API call."""
        provider = BraveProvider(api_key="brave-key")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "summarizer": {"summary": "This is a summary from Brave"}
        }
        
        with patch("requests.get", return_value=mock_response) as mock_get:
            messages = [{"role": "user", "content": "What is Python?"}]
            result = provider.call("brave-summarizer", messages)
        
        assert result.content == "This is a summary from Brave"
        assert result.model == "brave-summarizer"
        assert result.prompt_tokens is None  # Brave doesn't provide token counts
        assert result.completion_tokens is None
        
        # Verify correct API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["q"] == "What is Python?"
        assert call_args[1]["params"]["summary"] == "true"

    def test_no_query_error(self) -> None:
        """Test error when no user query is provided."""
        provider = BraveProvider(api_key="brave-key")
        
        with pytest.raises(ApiError, match="Brave API wymaga zapytania"):
            provider.call("brave-summarizer", [])

    def test_no_summary_in_response(self) -> None:
        """Test error when Brave API returns no summary."""
        provider = BraveProvider(api_key="brave-key")
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"summarizer": {}}
        
        with patch("requests.get", return_value=mock_response):
            with pytest.raises(ApiError, match="Brak podsumowania"):
                provider.call("brave-summarizer", [{"role": "user", "content": "test"}])


class TestCreateProvider:
    """Tests for provider factory function."""

    def test_create_sherlock_provider(self) -> None:
        """Test creating Sherlock provider."""
        provider = create_provider("sherlock", "test-key")
        assert isinstance(provider, SherlockProvider)
        assert provider.api_key == "test-key"

    def test_create_openai_provider(self) -> None:
        """Test creating OpenAI provider."""
        provider = create_provider("openai", "sk-key")
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "sk-key"

    def test_create_openwebui_provider(self) -> None:
        """Test creating OpenWebUI provider."""
        provider = create_provider("openwebui", "local-key", "http://localhost:3000")
        assert isinstance(provider, OpenWebUIProvider)
        assert provider.api_key == "local-key"

    def test_create_brave_provider(self) -> None:
        """Test creating Brave provider."""
        provider = create_provider("brave", "brave-key")
        assert isinstance(provider, BraveProvider)
        assert provider.api_key == "brave-key"

    def test_case_insensitive(self) -> None:
        """Test provider names are case-insensitive."""
        provider1 = create_provider("SHERLOCK", "key")
        assert isinstance(provider1, SherlockProvider)
        
        provider2 = create_provider("OpenAI", "key")
        assert isinstance(provider2, OpenAIProvider)

    def test_unknown_provider_error(self) -> None:
        """Test error on unknown provider."""
        with pytest.raises(ValueError, match="Nieznany provider: unknown"):
            create_provider("unknown", "key")
