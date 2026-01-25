from __future__ import annotations

import re
from typing import Optional

AVAILABLE_MODELS = {
    "Bielik-11B-v2.6-Instruct",
    "Bielik-11B-v2.3-Instruct",
    "openai/gpt-oss-120b",
    "CYFRAGOVPL/PLLuM-8x7B-chat",
    "Llama-3.1-8B-Instruct",
    "Llama-3.3-70B-Instruct",
    "DeepSeek-R1-Distill-Llama-70B",
}


def select_model(query: str, provided: Optional[str], has_file: bool) -> str:
    if provided:
        return provided
    
    normalized = query.lower()
    
    if has_file:
        return "Bielik-11B-v2.6-Instruct"
    
    # Bielik specjalnie dla polskiego
    bielik_keywords = r"\b(bielik|opowiedz)\b"
    if re.search(bielik_keywords, normalized):
        return "Bielik-11B-v2.6-Instruct"
    
    # Kreatywne zadania (np. opowiadania, poezja)
    creative_keywords = r"\b(twórz|zaplanuj|narracja|kreaty|oss|gpt|creative)\b"
    if re.search(creative_keywords, normalized):
        return "openai/gpt-oss-120b"
    
    # Dialog i rozmowa
    dialog_keywords = r"\b(pllum|rozmowa)\b"
    if re.search(dialog_keywords, normalized):
        return "CYFRAGOVPL/PLLuM-8x7B-chat"
    
    # Analiza i interpretacja
    analysis_keywords = r"\b(analiza|rozumowanie|think|deep)\b"
    if re.search(analysis_keywords, normalized):
        return "DeepSeek-R1-Distill-Llama-70B"
    
    # Zastosowanie ogólnego modelu Llama dla pozostałych przypadków
    return "Llama-3.1-8B-Instruct"


def is_supported(model: str) -> bool:
    return model in AVAILABLE_MODELS


def get_large_context_model() -> str:
    """Return the model with the largest context window for handling large prompts."""
    return "openai/gpt-oss-120b"


def get_all_models() -> list[str]:
    """Return a sorted list of all available models."""
    return sorted(AVAILABLE_MODELS)
