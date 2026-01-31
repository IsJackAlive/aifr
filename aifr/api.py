"""Legacy API module - now delegates to providers.

This module maintains backward compatibility while using the new provider system.
"""
from __future__ import annotations

from typing import Iterator, Optional, Union

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
    provider_name: str = "sherlock",
    temperature: float = 0.2,
    base_url: Optional[str] = None,
    stream: bool = False,
) -> Union[LlmResponse, Iterator[LlmResponse]]:
    """
    Unified function to call any supported LLM provider.
    
    Args:
        api_key: API key for the provider
        model: Model name/identifier
        messages: List of message dicts (role, content)
        provider_name: 'sherlock', 'openai', 'openwebui', or 'brave'
        temperature: Model creativity (0.0 - 1.0)
        base_url: Optional base URL for OpenWebUI
        stream: Whether to stream the response

    Returns:
        LlmResponse with content and metadata (or Iterator[LlmResponse] if streaming)

    Raises:
        ApiError: On API errors
        ContextLengthError: When context limit exceeded
    """
    provider = create_provider(provider_name, api_key, base_url)
    return provider.call(model, messages, temperature)

