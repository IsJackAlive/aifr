"""Legacy API module - now delegates to providers.

This module maintains backward compatibility while using the new provider system.
"""
from __future__ import annotations

from typing import Optional

from .providers import (
    ApiError,
    ContextLengthError,
    LlmResponse,
    create_provider,
)

# Re-export for backward compatibility
__all__ = ["ApiError", "ContextLengthError", "LlmResponse", "call_llm"]


def call_llm(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    provider_name: str = "sherlock",
    base_url: Optional[str] = None,
) -> LlmResponse:
    """
    Call LLM API using specified provider.

    Args:
        api_key: API key for authentication
        model: Model name to use
        messages: List of message dicts with 'role' and 'content'
        temperature: Sampling temperature (default 0.2)
        provider_name: Provider to use ('sherlock', 'openai', 'openwebui', 'brave')
        base_url: Override base URL (for OpenWebUI)

    Returns:
        LlmResponse with content and metadata

    Raises:
        ApiError: On API errors
        ContextLengthError: When context limit exceeded
    """
    provider = create_provider(provider_name, api_key, base_url)
    return provider.call(model, messages, temperature)

