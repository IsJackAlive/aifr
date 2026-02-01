# Instrukcje dla Agenta Developującego (Aifr Framework)

Ten dokument opisuje standardy i workflow dla agentów AI rozwijających projekt **Aifr**. Używamy podejścia **Iteracyjnego (Iterative Development)** oraz **TDD (Test-Driven Development)**.

## 📌 Zasady Naczelne

1.  **Zero Dependencies**: Rdzeń projektu i RAG nie mogą zależeć od ciężkich bibliotek (ML, LangChain). Używamy `Standard Library`.
2.  **Strict Typing**: Każda funkcja musi mieć poprawne type hinty. Weryfikujemy to za pomocą `mypy --strict`.
3.  **TDD First**: Zanim napiszesz kod nowej funkcji, stwórz test w `tests/`, który udowadnia jej potrzebę.
4.  **Minimalizm**: Aiferro to narzędzie CLI. Odpowiedzi LLM powinny być czytelne, a interfejs spójny (retro-style).

## 🔄 Cykl Iteracyjny

Każda nowa funkcjonalność powinna być realizowana w 4 krokach:

1.  **Planowanie**: Stwórz `implementation_plan.md` opisujący zmiany w `cli.py`, `executor.py` itp.
2.  **Testy**: Napisz testy jednostkowe (np. `tests/test_feature.py`).
3.  **Implementacja**: Napisz kod tak, aby testy przechodziły.
4.  **Weryfikacja & Dokumentacja**: Uruchom `./run_tests.sh`, zaktualizuj `CHANGELOG.md` i stwórz opisowy commit.

---

## 🚀 Proponowany Zakres Prac: Iteracja 7 (Session Management & Analytics)

**Cel**: Umożliwienie użytkownikowi zarządzania nazwanymi sesjami i śledzenia kosztów/użycia tokenów w czasie.

### 1. Nazwane Sesje (`--session <name>`)
- LLM powinien móc pracować w różnych kontekstach (np. projekt A, projekt B) bez mieszania historii.
- Ścieżka: `~/.cache/aifr/sessions/<name>.json`.

### 2. Analityka i Śledzenie Kosztów
- Dodanie modułu `aifr/analytics.py`.
- Zapisywanie sumarycznego zużycia tokenów dla każdego modelu.
- Flaga `--stats total` wyświetlająca podsumowanie ostatnich 7 dni (liczba promptów, total tokens).

### 3. Eksport sesji
- Funkcja eksportu historii do formatu `.md` lub `.json`, aby można było łatwo udostępnić logi z debugowania.

---

## 📝 Instrukcja dla Agenta (Prompt)

Jeśli chcesz zlecić mi (lub innemu agentowi) to zadanie, użyj poniższego hasła:

> "Działaj jako Senior Python Developer. Zaimplementuj Iterację 7 (Session Management) zgodnie z wytycznymi w `docs/guides/agent_development.md`. Rozpocznij od stworzenia planu w `implementation_plan.md`, a następnie przejdź do TDD."
