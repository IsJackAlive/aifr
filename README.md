# Aifr Terminal Assistant

> Napisane przez: GPT-5.1-Codex-max -> Claude Sonnet 4.5

**Wersja 1.2.0 - Multi-Provider** 🌐

Profesjonalny asystent terminalowy w Pythonie z wsparciem dla wielu dostawców API (Sherlock, OpenAI, OpenWebUI, Brave) i inteligentną selekcją agentów.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---
<div align="center">

> **🌟 NEW in v1.2.0: Multi-Provider Support!**  
> Aifr now works with OpenAI, OpenWebUI (local), Brave Summarizer, and Sherlock API.  
> See [RELEASE_v1.2.0.md](RELEASE_v1.2.0.md) for details.

![aifr image](images/img.png)

</div>
---

## ✨ Features

- 🌐 **Multi-provider** - Sherlock, OpenAI, OpenWebUI, Brave API support
- 🤖 **Agentic behavior** - 5 specialized agents (Debugger, Summarizer, Creative, Coder, Default)
- 🪟 **Sliding window context** - Inteligentne zarządzanie historią (5 ostatnich tur)
- 🔒 **Production-grade** - Pełne type hints, 71 testów jednostkowych, mypy validation
- 🛡️ **Security** - Automatyczna detekcja wrażliwych plików (.env, klucze SSH)
- 🔄 **Pipe-friendly** - Poprawna obsługa STDERR/STDOUT dla bash pipelines
- 📦 **Easy install** - Dostępne przez `pip install aifr`
- 🎯 **Smart model selection** - Automatyczny wybór odpowiedniego modelu LLM
- 💬 **Context memory** - Zapamiętywanie historii konwersacji między wywołaniami
- 📊 **Stats flag** - Podgląd metadanych (agent, tokeny, model)

## 📦 Instalacja

### Ze standardowego PyPI:
```bash
pip install aifr
```

### Dla developerów:
```bash
git clone https://github.com/IsJackAlive/aifr.git
cd aifr
pip install -e ".[dev]"  # instaluje z pytest, mypy, etc.
```

## ⚙️ Konfiguracja

### Wybór Providera

Aifr wspiera 4 dostawców API:
- **Sherlock** (domyślny) - Polish LLM models
- **OpenAI** - GPT-4, GPT-3.5-turbo
- **OpenWebUI** - Self-hosted, local models (Ollama)
- **Brave** - Web search summarizer

### Opcja 1: Zmienne środowiskowe (preferowane)

```bash
# Sherlock (default)
export SHERLOCK_API_KEY="<twój_klucz>"

# OpenAI
export OPENAI_API_KEY="sk-..."

# OpenWebUI (local)
export OPENWEBUI_API_KEY="<token>"

# Brave Summarizer
export BRAVE_API_KEY="<klucz>"
```

### Opcja 2: Plik konfiguracyjny

**Sherlock:**
```bash
mkdir -p ~/.config/aifr
cat > ~/.config/aifr/config.json << EOF
{
  "api_key": "<twój_klucz>",
  "provider": "sherlock",
  "model": "Llama-3.1-8B-Instruct",
  "context_limit": 6000
}
EOF
```

**OpenAI:**
```json
{
  "api_key": "sk-...",
  "provider": "openai",
  "model": "gpt-4",
  "context_limit": 8000
}
```

**OpenWebUI (local):**
```json
{
  "api_key": "your-token",
  "provider": "openwebui",
  "base_url": "http://localhost:3000",
  "model": "llama3:8b"
}
```

**Brave:**
```json
{
  "api_key": "brave-key",
  "provider": "brave"
}
```

Zobacz [config.json.example](config.json.example) dla więcej przykładów.

## 🚀 Użycie

### Proste pytanie
```bash
aifr 'Co to jest Python?'
# lub z flagą
aifr -p 'Co to jest Python?'
```

### Z plikiem
```bash
aifr 'Podsumuj ten plik' -f README.md
aifr 'Co jest w pliku?' --file ~/Documents/notatka.md
# Kolejność flag nie ma znaczenia
aifr -f README.md 'Podsumuj ten plik'
```

### Z poleceniem shell
```bash
# Wykonaj polecenie i przeanalizuj jego output
aifr 'Wyjaśnij co jest w tym katalogu' -c 'ls -la /tmp'
aifr 'Dlaczego testy nie przechodzą?' --console 'pytest tests/'
```

### Z pipe
```bash
# Przechwytuje output poprzedniego polecenia (stdin auto-detect)
grep -r "error" /var/log 2>&1 | aifr 'Przeanalizuj te błędy'
echo "some data" | aifr 'Sprawdź te dane'
cat file.txt | aifr 'Przetłumacz na angielski'
```

### Kombinacje flag
```bash
# Łącz pliki z poleceniami
aifr 'Dlaczego ten skrypt zawodzi?' -f script.py -c 'python script.py'
# Z wyborem modelu
aifr 'Skomplikowane zadanie' -f data.csv -m gpt-4
```

### Tryb interaktywny
```bash
aifr
# następnie wpisuj pytania, np.:
# > Streść dokument -f ./readme.md
# > Co jeszcze mogę dodać?
# > exit
```

### Statystyki i debugging
```bash
# Podgląd użytych metadanych
aifr 'Test' --stats
# Output:
# [Agent: DEFAULT | Model: Llama-3.1-8B | Tokens: 15/42/57]
```

### Flagi specjalne
```bash
aifr --help              # Wyświetl pełną pomoc
aifr --version           # Wyświetl wersję
aifr --reset             # Wyczyść historię konwersacji
aifr --new               # Alias dla --reset
aifr --stats             # Włącz tryb statystyk
aifr --info              # Alias dla --stats
aifr --list-models       # Wyświetl dostępne modele
```

### Parametry (flagi)

- **Positional argument / `-p` / `--prompt`** - Pytanie do asystenta (wymagane)
  ```bash
  aifr 'My question'       # Positional
  aifr -p 'My question'    # Flag
  ```

- **`-f` / `--file`** - Ścieżka do pliku (max 5MB)
  - Zawartość automatycznie wstrzykiwana między `===FILE_START===` i `===FILE_END===`
  - Model nie musi "otwierać" pliku
  - **Blokowane wrażliwe pliki**: `.env`, klucze SSH, `.pem`, etc.
  ```bash
  aifr 'Analyze' -f script.py
  ```

- **`-c` / `--console`** - Polecenie shell do wykonania
  - Output (stdout+stderr) dodawany do kontekstu
  - Stdin jest auto-wykrywany (pipe detection)
  ```bash
  aifr 'Debug' -c 'python app.py'
  cat log.txt | aifr 'Analyze'  # stdin auto-detected
  ```

- **`-m` / `--model`** - Wybór konkretnego modelu (domyślnie: automatyczny)
  ```bash
  aifr 'Complex task' -m gpt-4
  ```

- **`--context-limit`** - Limit kontekstu w tokenach (domyślnie: 6000)
  ```bash
  aifr 'Question' --context-limit 10000
  ```

- **`--reset` / `--new`** - Wyczyść historię konwersacji
  ```bash
  aifr --reset
  ```

- **`--stats` / `--info`** - Wyświetl metadane zapytania
  ```bash
  aifr 'Test' --stats
  ```

## 🤖 Inteligentna selekcja agentów

Aifr v1.1 automatycznie wybiera specjalistycznego "agenta" na podstawie kontekstu zapytania:

### 🐛 Debugger Agent
**Wykrywany przez**: błędy, problemy, debug, -c flag, stderr w stdin
```bash
aifr 'Fix this error' -c 'pytest'      # Auto: Debugger
aifr 'Dlaczego to nie działa?' -f app.py  # Auto: Debugger
```
**Zachowanie**: Analityczny, skupiony na przyczynach błędów, sugeruje konkretne poprawki

### 📝 Summarizer Agent
**Wykrywany przez**: "podsumuj", "streść", "wytłumacz", duże pliki
```bash
aifr 'Podsumuj' -f documentation.md    # Auto: Summarizer
aifr 'Streść w 3 punktach' -f report.txt
```
**Zachowanie**: Zwięzły, hierarchiczny, wyciąga kluczowe informacje

### 🎨 Creative Agent
**Wykrywany przez**: "opowiadanie", "wiersz", "story", "poem", "create"
```bash
aifr 'Napisz opowiadanie o kocie'     # Auto: Creative
aifr 'Generate a poem about AI'
```
**Zachowanie**: Ekspresyjny, kreatywny, storytelling

### 💻 Coder Agent
**Wykrywany przez**: "kod", "function", "refactor" + plik
```bash
aifr 'Review this code' -f script.py   # Auto: Coder
aifr 'Add error handling' -f app.py
```
**Zachowanie**: Techniczny, best practices, code examples

### 🔵 Default Agent
**Gdy brak dopasowania**
```bash
aifr 'What is the capital of Poland?'  # Auto: Default
```
**Zachowanie**: Uniwersalny, przyjazny, ogólne zagadnienia

**Podgląd użytego agenta**: Użyj flagi `--stats`
```bash
aifr 'Debug this' -c 'pytest' --stats
# [Agent: DEBUGGER | Model: DeepSeek-R1-Distill-Llama-70B | Tokens: 120/450/570]
```

## 🔍 Przykłady użycia

### Debug kodu
```bash
# Sprawdź błąd w logach (auto-detect: Debugger agent)
aifr 'Co powoduje ten błąd?' -c 'python app.py 2>&1'

# Analiza testów
pytest -v | aifr 'Które testy fallują i dlaczego?'
```

### Analiza plików
```bash
# Podsumowanie dokumentacji (auto-detect: Summarizer agent)
aifr 'Podsumuj w 3 punktach' -f RELEASE_v1.1.0.md

# Code review (auto-detect: Coder agent)
aifr 'Czy są tu problemy z bezpieczeństwem?' -f cli.py
```

### Automatyzacja
```bash
# W skrypcie bash
if aifr 'Czy wszystkie testy przeszły?' -c 'npm test' | grep -q "tak"; then
  echo "Deployment OK"
fi
```

### Kreatywne zastosowania
```bash
# Generowanie treści (auto-detect: Creative agent)
aifr 'Napisz krótkie opowiadanie o robocie który nauczył się śmiać'

# Analiza logów z wieloma kontekstami
aifr 'Explain these patterns' -f error.log -c 'tail -n 50 /var/log/syslog'
```

## 🛡️ Bezpieczeństwo

**Automatyczna ochrona przed wrażliwymi plikami:**
- ❌ Blokowane pliki: `.env`, `.env.local`, klucze SSH (`id_rsa`, `id_ed25519`), certyfikaty (`.pem`, `.key`), `credentials`, `secrets`
- 🔒 Pliki w katalogu `.ssh/` są automatycznie odrzucane
- ⚠️ Przyjazny komunikat ostrzegawczy przy próbie użycia wrażliwego pliku

**Exit codes dla skryptów:**
- `0` - sukces
- `1` - błąd (używaj w warunkach: `aifr ... && next_command`)

**Obsługa błędów:**
- Wszystkie błędy idą na STDERR (nie psują pipelines)
- STDOUT zawiera tylko odpowiedzi modelu
- Poprawna obsługa UTF-8 na wszystkich platformach

## 🤖 Modele LLM

**Automatyczny wybór modelu:**
- Dokumenty → `Bielik-11B-v2.6`
- Kreatywne/"kreaty" → `openai/gpt-oss-120b`
- Dialog → `PLLuM-8x7B-chat`
- Analiza → `DeepSeek-R1-Distill-Llama-70B`
- Domyślnie → `Llama-3.1-8B-Instruct`

**Automatyczne przełączanie:**
- Gdy kontekst przekracza limit modelu, system automatycznie przełącza się na `openai/gpt-oss-120b` (większe okno)

## 💾 Kontekst i sesje

**Nowe w v1.1: Sliding Window Context**
- Domyślnie przechowuje ostatnie **5 tur** konwersacji (user + assistant)
- Starsza historia jest automatycznie przycinana
- Kontekst zapisywany w `~/.cache/aifr/session.json` (TTL 4h)
- Współdzielony między wywołaniami CLI
- `aifr --reset` - wyczyść historię i zacznij od nowa
- Automatyczne przełączanie na większy model przy przekroczeniu limitu tokenów

**Dlaczego sliding window?**
- Zapobiega przeciążeniu kontekstu w długich sesjach
- Bardziej przewidywalne zużycie tokenów
- Koncentracja na ostatnich, najbardziej relevantnych wymianiach

## 📊 Output

- Tylko czysty tekst (bez Markdown, bez bloków kodu w odpowiedzi LLM)
- Długie odpowiedzi dzielone na segmenty
- Flaga `--stats`: Podsumowanie użycia (agent, model, tokeny in/out/total)

**Przykład z --stats:**
```bash
$ aifr 'Test' --stats
[Agent: DEFAULT | Model: Llama-3.1-8B-Instruct | Tokens: 15/42/57]
<odpowiedź asystenta>
```

## 🔧 Development

Dla developerów zainteresowanych rozwijaniem projektu:

```bash
# Setup
git clone https://github.com/IsJackAlive/aifr.git
cd aifr
pip install -e ".[dev]"

# Testy (77 tests)
pytest                 # Wszystkie testy
pytest tests/test_cli_parser.py  # Tylko parser
pytest tests/test_agent_controller.py  # Tylko agenty
pytest -v              # Verbose mode

# Type checking
mypy aifr/

# Build
python -m build
```

Zobacz [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) dla szczegółów.

## 📝 Wskazówki CLI (Bash)

### ✅ Poprawne użycie (v1.1)
```bash
# Pojedyncze cudzysłowy dla zapytań ze spacjami
aifr 'Co to jest Python?'

# Flagi w dowolnej kolejności
aifr -f script.py 'Analyze this'
aifr 'Analyze this' -f script.py  # Identyczne

# Z pipe
cat file.txt | aifr 'Przeanalizuj to'

# Kombinacja flag
aifr 'Debug this' -f app.py -c 'python app.py' --stats
```

**Migration:** Zobacz [MIGRATION_v1.0_to_v1.1.md](MIGRATION_v1.0_to_v1.1.md) dla pełnego przewodnika aktualizacji.

## 🧪 Testowanie
