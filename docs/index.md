# Aifr

Twój minimalistyczny most między terminalem a inteligencją LLM.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Keep a Changelog](https://img.shields.io/badge/changelog-Keep%20a%20Changelog-brightgreen)](CHANGELOG.md)

---

**Zasada Zero Konfiguracji**: Po ustawieniu klucza API (`export SHERLOCK_API_KEY="..."`), Aiferro działa natychmiast. Nie potrzebujesz skomplikowanych plików YAML ani baz danych – wszystko, co ważne, dzieje się w Twoim terminalu.

---

## 🚀 Szybki Start

Instalacja w sekundę:
```bash
pip install aifr && aifr --help
```

Lub wypróbuj bez instalacji (jeśli masz sklonowane repozytorium):
```bash
python3 -m aifr.cli "Cześć, co potrafisz?"
```

## ✨ Dlaczego Aifr?

- **Multi-Provider**: Obsługa Sherlock (PL), OpenAI, OpenWebUI oraz wyszukiwarki Brave.
- **Smart Context**: Inteligentne zarządzanie historią konwersacji (sliding window).
- **RAG & Context**: Bezpośrednie wstrzykiwanie plików (`-f`) i przeszukiwanie katalogów (`--rag`).
- **Plan & Execute**: Bezpieczne generowanie i uruchamianie poleceń shellowych (`--exec`).
- **Agentic Logic**: Automatyczny wybór profilu (Debugger, Summarizer, Coder) na podstawie Twojego pytania.

## 🛠 Przykłady

```bash
# Debug błędu w testach
pytest | aifr 'Dlaczego testy nie przechodzą?'

# Analiza kodu
aifr 'Dodaj obsługę błędów do tej funkcji' -f app.py

# Wykonanie zadania systemowego
aifr --exec 'Znajdź wszystkie pliki .log większe niż 50MB i skompresuj je'
```

## 📚 Dokumentacja

- [Główne funkcje](./features/index.md)
- [Konfiguracja providerów](./guides/configuration.md)
- [Tryb RAG i inteligentny kontekst](./features/rag.md)
- [Bezpieczeństwo i OS Integration](./features/security.md)
- [Release Notes](./releases/v1.3.0.md)

---
Poprawki, sugestie? Zapraszamy do [CHANGELOG.md](CHANGELOG.md).
