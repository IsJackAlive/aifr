# Aifr - Konfiguracja

Aifr można konfigurować na dwa główne sposoby:
1. Przez plik konfiguracyjny `config.json` (zalecane)
2. Przez zmienne środowiskowe (dla szybkiej zmiany ustawień)

## Lokalizacja pliku konfiguracji

Plik konfiguracyjny powinien znajdować się w katalogu domowym użytkownika:

- **Linux/Mac**: `~/.config/aifr/config.json`
- **Windows**: `%USERPROFILE%\.config\aifr\config.json`

Jeżeli katalog nie istnieje, należy go utworzyć:
```bash
mkdir -p ~/.config/aifr
```

## Przykłady konfiguracji

Poniżej znajdziesz gotowe szablony dla różnych dostawców AI.

### 1. Sherlock API (Domyślny)

To jest domyślny provider. Wymaga tylko klucza API.

```json
{
  "api_key": "twoj-klucz-sherlock",
  "provider": "sherlock",
  "model": "Llama-3.1-8B-Instruct",
  "context_limit": 6000
}
```

### 2. OpenAI (ChatGPT)

Użyj tej konfiguracji, jeśli posiadasz klucz do API OpenAI.

```json
{
  "api_key": "sk-twoj-klucz-openai",
  "provider": "openai",
  "model": "gpt-4",
  "context_limit": 8000
}
```

**Dostępne modele:** `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`.

### 3. OpenWebUI (Lokalne AI)

Idealne rozwiązanie, jeśli używasz lokalnych modeli przez OpenWebUI lub Ollama.

```json
{
  "api_key": "twoj-lokalny-token",
  "provider": "openwebui",
  "base_url": "http://localhost:3000",
  "model": "gemma3:4b-it-qat",
  "context_limit": 4000
}
```

> **Uwaga:** Upewnij się, że `base_url` wskazuje na Twój serwer (np. `http://192.168.1.8:3000`).

### 4. Brave Summarizer

Służy tylko do podsumowywania treści z internetu.

```json
{
  "api_key": "twoj-klucz-brave",
  "provider": "brave"
}
```

## Zmienne środowiskowe

Możesz także używać zmiennych środowiskowych, aby nadpisać konfigurację bez edycji pliku. Aifr automatycznie wykryje providera na podstawie ustawionej zmiennej.

| Zmienna | Provider | Przykład |
|---------|----------|----------|
| `SHERLOCK_API_KEY` | sherlock | `export SHERLOCK_API_KEY="key..."` |
| `OPENAI_API_KEY` | openai | `export OPENAI_API_KEY="sk-..."` |
| `OPENWEBUI_API_KEY`| openwebui| `export OPENWEBUI_API_KEY="token"` |
| `BRAVE_API_KEY` | brave | `export BRAVE_API_KEY="key..."` |

### Przykład użycia w terminalu:

```bash
# Szybkie przełączenie na OpenAI
export OPENAI_API_KEY="sk-..."
aifr "Co to jest Python?" -m gpt-4
```
