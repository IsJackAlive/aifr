"""Dynamic system prompt selection based on user intent (Agentic behavior)."""
from __future__ import annotations

from enum import Enum
from typing import Optional


class AgentType(Enum):
    """Available agent types with different capabilities."""
    DEFAULT = "default"
    DEBUGGER = "debugger"
    CREATIVE = "creative"
    SUMMARIZER = "summarizer"
    CODER = "coder"


# Registry of system prompts for each agent type
AGENT_PROMPTS = {
    AgentType.DEFAULT: (
        "Jesteś terminalowym asystentem. Odpowiadasz tylko tekstem, bez markdown "
        "i bez bloków kodu. Jeśli w wiadomości jest blok oznaczony "
        "===FILE_START=== ... ===FILE_END===, to jest pełna treść pliku; zawsze "
        "z niej korzystasz i nigdy nie piszesz, że plik nie został wklejony. "
        "Jeśli jest blok ===CONSOLE_START=== ... ===CONSOLE_END===, to jest "
        "zawartość terminala/konsoli użytkownika - analizujesz ją w kontekście pytania. "
        "Jeśli bloków nie ma, i tak odpowiadasz na pytanie na bazie dostępnego "
        "kontekstu. Nie prosisz o ponowne wklejenie pliku. Jeśli proszą o "
        "podsumowanie, po prostu je podaj. Wybierasz model LLM odpowiedni do "
        "zadania i zwracasz gotową odpowiedź."
    ),
    
    AgentType.DEBUGGER: (
        "Jesteś ekspertem DevOps i Python. Analizujesz logi błędów, stack traces, "
        "i kod źródłowy. Twoja odpowiedź powinna:\n"
        "1. Zidentyfikować główną przyczynę błędu\n"
        "2. Wyjaśnić co poszło nie tak\n"
        "3. Zaproponować konkretne rozwiązanie\n"
        "Bądź zwięzły i techniczny. Nie używaj markdown. Jeśli widzisz kod lub logi "
        "między ===CONSOLE_START=== i ===CONSOLE_END===, to jest output polecenia."
    ),
    
    AgentType.CREATIVE: (
        "Jesteś kreatywnym pisarzem. Używasz bogatego słownictwa, metafor, "
        "i rozbudowanych opisów. Twoje odpowiedzi powinny być barwne i innowacyjne. "
        "Nie ograniczaj się do suchych faktów - dodawaj kontekst, emocje, i szczegóły. "
        "Pisz płynnie i angażująco. Nie używaj markdown ani bloków kodu."
    ),
    
    AgentType.SUMMARIZER: (
        "Jesteś analitykiem treści. Twoim zadaniem jest ekstrakcja najważniejszych "
        "informacji z dostarczonego tekstu. Odpowiadasz w formie:\n"
        "- Krótkich punktów wypunktowanych (używaj - nie *)\n"
        "- Zwięzłych stwierdzeń bez zbędnych detali\n"
        "- Hierarchii ważności informacji\n"
        "Jeśli tekst jest między ===FILE_START=== i ===FILE_END===, to pełna treść "
        "do analizy. Nie używaj markdown."
    ),
    
    AgentType.CODER: (
        "Jesteś ekspertem programowania. Analizujesz kod, proponujesz usprawnienia, "
        "wyjaśniasz działanie funkcji i algorytmów. Gdy widzisz kod:\n"
        "1. Oceń jego jakość i poprawność\n"
        "2. Wskaż potencjalne problemy\n"
        "3. Zasugeruj best practices\n"
        "Bądź konkretny i techniczny. Nie używaj markdown ani bloków kodu w odpowiedzi."
    ),
}


def detect_agent_type(
    prompt: str,
    has_console: bool = False,
    has_file: bool = False,
    file_size: Optional[int] = None,
) -> AgentType:
    """
    Determine which agent type to use based on context.
    
    Args:
        prompt: User's question/prompt
        has_console: Whether console command output is included
        has_file: Whether file is attached
        file_size: Size of attached file in characters (for large docs)
        
    Returns:
        AgentType enum value
    """
    prompt_lower = prompt.lower()
    
    # Debug/Error keywords (highest priority for errors)
    debug_keywords = [
        "błąd", "error", "exception", "traceback", "failed", "fail",
        "nie działa", "crash", "bug", "debug", "fix", "napraw",
        "stack trace", "warning"
    ]
    if any(kw in prompt_lower for kw in debug_keywords) or has_console:
        return AgentType.DEBUGGER
    
    # Code analysis keywords (check before summarizer to prioritize code review)
    code_keywords = [
        "kod", "code", "function", "funkcja", "class", "klasa",
        "algorithm", "algorytm", "review", "refactor"
    ]
    if any(kw in prompt_lower for kw in code_keywords) and has_file:
        return AgentType.CODER
    
    # Creative writing keywords
    creative_keywords = [
        "opowiadanie", "wiersz", "poem", "story", "list", "napisz",
        "wymyśl", "kreaty", "kreatywn", "historia", "bajka"
    ]
    if any(kw in prompt_lower for kw in creative_keywords):
        return AgentType.CREATIVE
    
    # Summarization keywords or large file
    summary_keywords = [
        "streść", "streszcz", "podsumuj", "summarize", "skrót",
        "najważniejsze", "główne punkty", "tldr", "w skrócie"
    ]
    # Treat as summary if: explicit keywords OR (has file AND short prompt)
    if any(kw in prompt_lower for kw in summary_keywords):
        return AgentType.SUMMARIZER
    if has_file and len(prompt) < 50:
        return AgentType.SUMMARIZER
    if file_size and file_size > 2000:  # Large file -> likely needs summary
        return AgentType.SUMMARIZER
    
    # Default assistant
    return AgentType.DEFAULT


def get_system_prompt(agent_type: AgentType) -> str:
    """
    Get system prompt for given agent type.
    
    Args:
        agent_type: Type of agent to use
        
    Returns:
        System prompt string
    """
    return AGENT_PROMPTS.get(agent_type, AGENT_PROMPTS[AgentType.DEFAULT])


def get_agent_name(agent_type: AgentType) -> str:
    """
    Get human-readable agent name for display.
    
    Args:
        agent_type: Type of agent
        
    Returns:
        Display name string
    """
    names = {
        AgentType.DEFAULT: "General Assistant",
        AgentType.DEBUGGER: "Debugger/DevOps",
        AgentType.CREATIVE: "Creative Writer",
        AgentType.SUMMARIZER: "Summarizer",
        AgentType.CODER: "Code Analyst",
    }
    return names.get(agent_type, "Unknown")