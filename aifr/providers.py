"""API Providers for different LLM services.

Supports:
- Sherlock API (default)
- OpenAI API
- OpenWebUI (local)
- Brave Summarizer API
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Iterator, Union

import requests
from requests import Response


class ApiError(Exception):
    """Base exception for API errors."""
    pass


class ContextLengthError(ApiError):
    """Raised when the prompt exceeds the model's context length."""
    pass


@dataclass
class LlmResponse:
    """Standard response from any LLM provider."""
    content: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class LlmProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def call(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        stream: bool = False,
    ) -> Union[LlmResponse, Iterator[LlmResponse]]:
        """Call the LLM API and return standardized response."""
        pass

    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _stream_sse(self, resp: Response, model: str) -> Iterator[LlmResponse]:
        """Shared SSE parser for OpenAI-compatible streams."""
        import json
        for line in resp.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8").strip()
            if not line_str.startswith("data: "):
                continue
            
            data_str = line_str[6:]
            if data_str == "[DONE]":
                break
                
            try:
                data = json.loads(data_str)
                choices = data.get("choices", [])
                if not choices:
                    continue
                    
                delta = choices[0].get("delta", {})
                content_chunk = delta.get("content", "")
                
                usage = data.get("usage", {})
                
                yield LlmResponse(
                    content=content_chunk,
                    model=model,
                    prompt_tokens=self._safe_int(usage.get("prompt_tokens")),
                    completion_tokens=self._safe_int(usage.get("completion_tokens")),
                    total_tokens=self._safe_int(usage.get("total_tokens")),
                )
            except json.JSONDecodeError:
                continue


class SherlockProvider(LlmProvider):
    """Provider for Sherlock API (default)."""

    def __init__(self, api_key: str) -> None:
        super().__init__(
            api_key=api_key,
            base_url="https://api-sherlock.cloudferro.com/openai/v1/chat/completions"
        )

    def call(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        stream: bool = False,
    ) -> Union[LlmResponse, Iterator[LlmResponse]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        try:
            resp: Response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=60, stream=stream
            )
        except requests.RequestException as exc:
            raise ApiError(f"Błąd połączenia z Sherlock API: {exc}") from exc

        if resp.status_code >= 300:
            error_text = resp.text
            # Detect context length exceeded error
            if resp.status_code == 400 and (
                "maximum context length" in error_text.lower()
                or "tokens in the messages" in error_text.lower()
            ):
                raise ContextLengthError(
                    f"Model przekroczył limit kontekstu: {error_text}"
                )
            raise ApiError(f"Sherlock API błąd {resp.status_code}: {error_text}")

        if stream:
            return self._stream_sse(resp, model)

        try:
            data = resp.json()
        except ValueError as exc:
            raise ApiError("Niepoprawna odpowiedź JSON z Sherlock API") from exc

        choices = data.get("choices") or []
        if not choices:
            raise ApiError("Brak odpowiedzi z modelu")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            raise ApiError("Pusta odpowiedź z modelu")

        usage = data.get("usage") or {}
        resolved_model = data.get("model") or model

        return LlmResponse(
            content=content,
            model=resolved_model,
            prompt_tokens=self._safe_int(usage.get("prompt_tokens")),
            completion_tokens=self._safe_int(usage.get("completion_tokens")),
            total_tokens=self._safe_int(usage.get("total_tokens")),
        )


class OpenAIProvider(LlmProvider):
    """Provider for OpenAI API."""

    def __init__(self, api_key: str) -> None:
        super().__init__(
            api_key=api_key,
            base_url="https://api.openai.com/v1/chat/completions"
        )

    def call(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        stream: bool = False,
    ) -> Union[LlmResponse, Iterator[LlmResponse]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        try:
            resp: Response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=60, stream=stream
            )
        except requests.RequestException as exc:
            raise ApiError(f"Błąd połączenia z OpenAI API: {exc}") from exc

        if resp.status_code >= 300:
            error_text = resp.text
            if resp.status_code == 400:
                try:
                    error_data = resp.json()
                    error_code = error_data.get("error", {}).get("code")
                    if error_code == "context_length_exceeded":
                        raise ContextLengthError(
                            f"OpenAI: Context length exceeded: {error_text}"
                        )
                except ValueError:
                    pass
            raise ApiError(f"OpenAI API błąd {resp.status_code}: {error_text}")

        if stream:
            return self._stream_sse(resp, model)

        try:
            data = resp.json()
        except ValueError as exc:
            raise ApiError("Niepoprawna odpowiedź JSON z OpenAI API") from exc

        choices = data.get("choices") or []
        if not choices:
            raise ApiError("Brak odpowiedzi z modelu OpenAI")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            raise ApiError("Pusta odpowiedź z modelu OpenAI")

        usage = data.get("usage") or {}
        resolved_model = data.get("model") or model

        return LlmResponse(
            content=content,
            model=resolved_model,
            prompt_tokens=self._safe_int(usage.get("prompt_tokens")),
            completion_tokens=self._safe_int(usage.get("completion_tokens")),
            total_tokens=self._safe_int(usage.get("total_tokens")),
        )


class OpenWebUIProvider(LlmProvider):
    """Provider for OpenWebUI (local installation)."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:3000") -> None:
        # OpenWebUI uses /api/chat/completions endpoint
        full_url = f"{base_url.rstrip('/')}/api/chat/completions"
        super().__init__(api_key=api_key, base_url=full_url)

    def call(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        stream: bool = False,
    ) -> Union[LlmResponse, Iterator[LlmResponse]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        try:
            resp: Response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=60
            )
        except requests.RequestException as exc:
            raise ApiError(f"Błąd połączenia z OpenWebUI: {exc}") from exc

        if resp.status_code >= 300:
            error_text = resp.text
            raise ApiError(f"OpenWebUI błąd {resp.status_code}: {error_text}")

        if stream:
            return self._stream_sse(resp, model)

        try:
            data = resp.json()
        except ValueError as exc:
            raise ApiError("Niepoprawna odpowiedź JSON z OpenWebUI") from exc

        choices = data.get("choices") or []
        if not choices:
            raise ApiError("Brak odpowiedzi z OpenWebUI")

        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            raise ApiError("Pusta odpowiedź z OpenWebUI")

        usage = data.get("usage") or {}
        resolved_model = data.get("model") or model

        return LlmResponse(
            content=content,
            model=resolved_model,
            prompt_tokens=self._safe_int(usage.get("prompt_tokens")),
            completion_tokens=self._safe_int(usage.get("completion_tokens")),
            total_tokens=self._safe_int(usage.get("total_tokens")),
        )


class BraveProvider(LlmProvider):
    """Provider for Brave Search Summarizer API."""

    def __init__(self, api_key: str) -> None:
        super().__init__(
            api_key=api_key,
            base_url="https://api.search.brave.com/res/v1/summarizer/search"
        )

    def call(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        stream: bool = False,
    ) -> Union[LlmResponse, Iterator[LlmResponse]]:
        """
        Brave API uses a different format - extracts query from messages
        and returns summarized search results.
        """
        # Extract user query from messages
        query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                query = msg.get("content", "")
                break

        if not query:
            raise ApiError("Brave API wymaga zapytania użytkownika")

        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept": "application/json",
        }
        params = {
            "q": query,
            "summary": "true",
        }

        try:
            resp: Response = requests.get(
                self.base_url, headers=headers, params=params, timeout=60
            )
        except requests.RequestException as exc:
            raise ApiError(f"Błąd połączenia z Brave API: {exc}") from exc

        if resp.status_code >= 300:
            error_text = resp.text
            raise ApiError(f"Brave API błąd {resp.status_code}: {error_text}")

        try:
            data = resp.json()
        except ValueError as exc:
            raise ApiError("Niepoprawna odpowiedź JSON z Brave API") from exc

        # Brave API returns summary in different format
        summary = data.get("summarizer", {}).get("summary")
        if not summary:
            raise ApiError("Brak podsumowania z Brave API")

        # Brave doesn't provide token counts
        return LlmResponse(
            content=summary,
            model="brave-summarizer",
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
        )


def create_provider(
    provider_name: str,
    api_key: str,
    base_url: Optional[str] = None,
) -> LlmProvider:
    """Factory function to create the appropriate provider."""
    provider_name_lower = provider_name.lower()

    if provider_name_lower == "sherlock":
        return SherlockProvider(api_key)
    elif provider_name_lower == "openai":
        return OpenAIProvider(api_key)
    elif provider_name_lower == "openwebui":
        return OpenWebUIProvider(api_key, base_url or "http://localhost:3000")
    elif provider_name_lower == "brave":
        return BraveProvider(api_key)
    else:
        raise ValueError(
            f"Nieznany provider: {provider_name}. "
            f"Wspierane: sherlock, openai, openwebui, brave"
        )
