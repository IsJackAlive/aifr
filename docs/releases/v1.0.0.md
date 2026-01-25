# Release Notes v1.0.0

## Aifr - Production-Ready Release

Data wydania: 21 stycznia 2026

---

## 🎉 Główne zmiany

### A. Jakość Kodu i Standardy (Code Quality)

✅ **Obsługa błędów przez STDERR**
- Wszystkie błędy i ostrzeżenia są teraz wysyłane na `sys.stderr` zamiast `print()`
- Poprawne działanie w potokach bash (`|` pipes)
- Kompatybilność ze skryptami automatyzacyjnymi

✅ **Type Hinting & Mypy**
- Wszystkie funkcje mają pełne adnotacje typów
- Konfiguracja mypy w `pyproject.toml` z rygorystycznymi ustawieniami
- Wszystkie pliki przechodzą walidację mypy bez błędów

✅ **Poprawne Exit Codes**
- `sys.exit(0)` dla sukcesu
- `sys.exit(1)` dla błędów
- Umożliwia łączenie z innymi komendami: `aifr ... && echo "Success"`

### B. Pakietyzacja (Packaging)

✅ **Kompletny pyproject.toml**
- Zablokowane wersje zależności (`requests==2.31.0`)
- Pełne metadane projektu (author, license, keywords, classifiers)
- Opcjonalne dev dependencies (`pytest`, `mypy`, `pytest-mock`)
- Konfiguracja pytest i mypy w jednym pliku

✅ **Professional Package Structure**
- `LICENSE` (MIT)
- `MANIFEST.in` dla poprawnego pakowania
- `.gitignore` z pełną konfiguracją
- `Makefile` z komendami development

### C. Testy (Testing)

✅ **Kompleksowy test suite**
- 36 testów jednostkowych napisanych w pytest
- Testy dla `parse_command`, `build_user_message`, `load_file`
- Mockowanie funkcji nie wymagających API
- Wszystkie testy przechodzą (100% success rate)

📦 **Test coverage:**
- `command_parser.py` - 22 testy
- `cli.py` - 7 testów
- `file_loader.py` - 14 testów

### D. User Experience (UX)

✅ **Help & Version**
- `aifr --help` - wyświetla pełną pomoc z przykładami
- `aifr --version` - wyświetla aktualną wersję (1.0.0)
- `aifr -h` i `aifr -v` - aliasy dla wygody

✅ **Ulepszona obsługa błędów**
- Czytelne komunikaty błędów
- Kontekst błędu dla użytkownika
- Rozróżnienie między ostrzeżeniami a błędami krytycznymi

### E. Bezpieczeństwo

✅ **Ochrona przed wrażliwymi plikami**
- Czarna lista wrażliwych plików (`.env`, klucze SSH, `.pem`, etc.)
- Automatyczne wykrywanie plików w katalogu `.ssh`
- Przyjazne komunikaty ostrzegawcze

✅ **UTF-8 Encoding**
- Poprawna obsługa UTF-8 w stdin (również na Windows)
- Graceful handling dla błędów dekodowania
- Fallback na `errors='replace'` dla niepoprawnych znaków

### F. Konfiguracja

✅ **Lepsze zarządzanie konfiguracją**
- `SYSTEM_PROMPT` przeniesiony z kodu do `config.py`
- Łatwiejsza modyfikacja bez edycji logiki aplikacji
- Centralne miejsce dla wszystkich stałych

---

## 📋 Pełna lista zmian technicznych

### Pliki zmienione:
1. **cli.py**
   - Zamiana `print()` na `sys.stderr.write()` dla błędów
   - Dodanie `show_help()` i obsługi `--help/--version`
   - Poprawne exit codes (`return 0/1`, `sys.exit()`)
   - Import `SYSTEM_PROMPT` z config
   - Dodanie adnotacji wersji `__version__ = "1.0.0"`

2. **config.py**
   - Dodanie `SYSTEM_PROMPT` jako stała konfiguracyjna
   - Poprawione type hints dla funkcji `_read_json()`

3. **file_loader.py**
   - Nowa klasa `SensitiveFileError`
   - Funkcja `is_sensitive_file()` do wykrywania wrażliwych plików
   - Lista `SENSITIVE_FILE_PATTERNS` z czarną listą
   - Sprawdzanie plików przed wczytaniem

4. **terminal_capture.py**
   - Poprawiona obsługa UTF-8 w `read_stdin_early()`
   - Użycie `sys.stdin.buffer` dla surowych bajtów
   - Dekodowanie z `errors='replace'` fallback

5. **command_parser.py**
   - Poprawione type hints dla zgodności z mypy
   - Bezpieczne rzutowanie typów w zwracanym `Command`

6. **api.py**
   - Dodanie adnotacji typu dla parametru `messages`
   - Poprawiona funkcja `_safe_int()` z proper type handling

7. **pyproject.toml**
   - Wersja 1.0.0
   - Zablokowane wersje dependencies
   - Dev dependencies (pytest, mypy)
   - Konfiguracja mypy i pytest
   - Pełne metadane projektu

### Nowe pliki:
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_command_parser.py` (22 testy)
- `tests/test_cli.py` (7 testów)
- `tests/test_file_loader.py` (14 testów)
- `LICENSE` (MIT)
- `MANIFEST.in`
- `.gitignore`
- `Makefile`

---

## 🚀 Instalacja i użycie

### Instalacja standardowa:
```bash
pip install aifr
```

### Instalacja dla developerów:
```bash
git clone https://github.com/IsJackAlive/aifr.git
cd aifr
make install-dev  # lub: pip install -e ".[dev]"
```

### Uruchamianie testów:
```bash
make test        # pytest
make type-check  # mypy
make lint        # syntax check
```

### Budowanie pakietu:
```bash
make build       # tworzy dist/
make upload      # publikuje na PyPI
```

---

## 📚 Dokumentacja

Pełna dokumentacja dostępna w README.md

### Podstawowe użycie:
```bash
# Proste pytanie
aifr $ask: Co to jest Python?

# Z plikiem
aifr $ask: Podsumuj ten plik $file: README.md

# Z pipe
echo "dane" | aifr $ask: Przeanalizuj

# Z poleceniem konsoli
aifr $ask: Co jest nie tak? $cons: "pytest tests/"
```

---

## 🎯 Następne kroki (Post-v1.0.0)

Rozważane features dla przyszłych wersji:
- Integracja z biblioteką `rich` dla kolorowego outputu
- Support dla większej ilości formatów plików (.py, .json, .yaml)
- Lokalne cachowanie odpowiedzi
- Progress bar dla długich operacji
- Configuration profiles

---

## 📝 Licencja

MIT License - zobacz plik LICENSE

---

## 👥 Autorzy

Aifr Team

---

## 🙏 Podziękowania

Dziękujemy społeczności open-source za feedback i wsparcie!
