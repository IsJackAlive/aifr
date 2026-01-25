# Release Notes: Aifr v1.2.0 - "Multi-Provider"

**Release Date**: 2025-01-21  
**Type**: MINOR (New Features, Backward Compatible)  
**Git Tag**: `v1.2.0`

---

## 🎉 Overview

Version 1.2.0 adds support for multiple LLM API providers, allowing Aifr to work with OpenAI, OpenWebUI (local), Brave Summarizer, and the default Sherlock API.

**Key Highlight:** Provider-agnostic architecture with automatic provider detection based on API keys.

---

## ✨ New Features

### 1. Multi-Provider Support

Aifr now supports 4 different LLM providers:

#### 🔵 **Sherlock API** (Default)
- Original provider, fully compatible
- No configuration changes needed for existing users
- Endpoint: `https://api-sherlock.cloudferro.com/openai/v1/chat/completions`

**Configuration:**
```json
{
  "api_key": "your-sherlock-key",
  "provider": "sherlock"
}
```

**Environment variable:**
```bash
export SHERLOCK_API_KEY="your-key"
```

---

#### 🟢 **OpenAI API**
- Direct OpenAI API support (gpt-4, gpt-3.5-turbo, gpt-4-turbo, etc.)
- Full context length error handling
- Standard OpenAI response format

**Configuration:**
```json
{
  "api_key": "sk-...",
  "provider": "openai",
  "model": "gpt-4"
}
```

**Environment variable:**
```bash
export OPENAI_API_KEY="sk-..."
aifr 'What is AI?' -m gpt-4
```

**Auto-detection:** If `OPENAI_API_KEY` is set and no explicit provider configured, Aifr automatically uses OpenAI.

---

#### 🟠 **OpenWebUI** (Local Installation)
- Support for self-hosted OpenWebUI instances
- Compatible with Ollama models (granite3.1-dense:8b, llama, etc.)
- Custom base URL support

**Configuration:**
```json
{
  "api_key": "your-local-token",
  "provider": "openwebui",
  "base_url": "http://localhost:3000",
  "model": "granite3.1-dense:8b"
}
```

**Environment variable:**
```bash
export OPENWEBUI_API_KEY="your-token"
aifr 'Test local model' -m granite3.1-dense:8b
```

**Custom endpoints:**
```json
{
  "provider": "openwebui",
  "base_url": "http://my-server:8080"
}
```

---

#### 🟡 **Brave Summarizer API**
- Web search + AI summarization
- Automatically extracts query from user messages
- No token counts (Brave doesn't provide them)

**Configuration:**
```json
{
  "api_key": "your-brave-key",
  "provider": "brave"
}
```

**Environment variable:**
```bash
export BRAVE_API_KEY="your-brave-key"
aifr 'What are the latest AI developments?'
```

**Note:** Brave provider is best for summarizing web search results, not for general conversation.

---

### 2. Provider Auto-Detection

Aifr automatically detects the provider based on environment variables:

**Priority order:**
1. Explicit `provider` in config.json
2. `OPENAI_API_KEY` → openai
3. `BRAVE_API_KEY` → brave
4. `OPENWEBUI_API_KEY` → openwebui
5. `SHERLOCK_API_KEY` / `AIFERRO_API_KEY` → sherlock (default)

**Example:**
```bash
# Set OpenAI key
export OPENAI_API_KEY="sk-..."
# Aifr automatically uses OpenAI provider
aifr 'Test' -m gpt-4
```

---

### 3. Provider Architecture

New modular architecture with:
- **Abstract base class**: `LlmProvider` (providers.py)
- **Concrete implementations**: `SherlockProvider`, `OpenAIProvider`, `OpenWebUIProvider`, `BraveProvider`
- **Factory pattern**: `create_provider()` function
- **Backward compatibility**: Existing `call_llm()` API unchanged

**For developers:**
```python
from aifr.providers import create_provider

provider = create_provider("openai", api_key="sk-...")
response = provider.call(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.content)
```

---

## 🔧 Configuration Examples

### Multi-Provider Setup

**Scenario 1: Use OpenAI for most tasks, Sherlock for Polish models**

```json
{
  "api_key": "sk-...",
  "provider": "openai",
  "model": "gpt-4"
}
```

Override per-command:
```bash
export SHERLOCK_API_KEY="sherlock-key"
aifr 'Pytanie po polsku' -m Bielik-11B-v2.6
```

---

**Scenario 2: Local OpenWebUI for privacy**

```json
{
  "api_key": "local-token",
  "provider": "openwebui",
  "base_url": "http://localhost:3000",
  "model": "llama3:8b"
}
```

---

**Scenario 3: Brave for web research**

```bash
export BRAVE_API_KEY="brave-key"
cat << EOF > ~/.config/aifr/config.json
{
  "api_key": "$BRAVE_API_KEY",
  "provider": "brave"
}
EOF

aifr 'What is the latest news about AI?'
```

---

## 🛠️ Technical Changes

### New Modules

1. **`aifr/providers.py`** (NEW)
   - Abstract base class `LlmProvider`
   - 4 concrete provider implementations
   - Factory function `create_provider()`
   - Standardized error handling
   - ~350 lines

### Modified Modules

1. **`aifr/api.py`** (REFACTORED)
   - Now delegates to `providers.py`
   - Maintains backward compatibility
   - Added `provider_name` and `base_url` parameters to `call_llm()`
   - Re-exports `ApiError`, `ContextLengthError`, `LlmResponse`

2. **`aifr/config.py`** (ENHANCED)
   - Added `provider: str` field to `AppConfig`
   - Added `base_url: Optional[str]` field
   - Auto-detection logic for provider based on env vars
   - Supports `OPENAI_API_KEY`, `BRAVE_API_KEY`, `OPENWEBUI_API_KEY`

3. **`aifr/cli.py`** (UPDATED)
   - Passes `provider` and `base_url` to `call_llm()`
   - Updated `process_request()` signature
   - Version bump to 1.2.0

### Testing

**New Test Suite:**
- `tests/test_providers.py` - 16 tests
  - SherlockProvider: 3 tests
  - OpenAIProvider: 2 tests
  - OpenWebUIProvider: 2 tests
  - BraveProvider: 3 tests
  - Factory function: 6 tests

**Total Coverage:**
- **71 tests** (55 from v1.1 + 16 new)
- 100% pass rate
- All providers mocked (no real API calls in tests)

---

## 📦 Installation & Upgrade

### Fresh Install
```bash
pip install aifr==1.2.0
```

### Upgrade from v1.1
```bash
pip install --upgrade aifr
aifr --version  # Should show 1.2.0
```

**Post-upgrade:**
- No configuration changes required
- Existing Sherlock users: Everything works as before
- New users: Set `provider` in config.json or use environment variables

---

## 🔄 Migration Guide

### From v1.1 to v1.2

**No breaking changes!** All existing configurations work without modification.

**To use new providers:**

1. **OpenAI:**
   ```bash
   export OPENAI_API_KEY="sk-..."
   aifr 'Test' -m gpt-4
   ```

2. **OpenWebUI:**
   ```json
   {
     "api_key": "token",
     "provider": "openwebui",
     "base_url": "http://localhost:3000"
   }
   ```

3. **Brave:**
   ```bash
   export BRAVE_API_KEY="key"
   # Aifr auto-detects
   aifr 'Web search query'
   ```

---

## 🐛 Bug Fixes

- Fixed: Better error messages for API failures (now include provider name)
- Fixed: Proper handling of missing usage data (Brave API)
- Fixed: URL formatting for OpenWebUI endpoints

---

## 📚 Documentation

**Updated Files:**
- `README.md` - Added provider configuration examples
- `RELEASE_v1.2.0.md` - This file
- `config.json.example` - Multi-provider examples

**New Examples:**
```bash
# OpenAI example
aifr 'Explain quantum computing' -m gpt-4 --stats

# OpenWebUI local example
aifr 'Test local model' -m llama3:8b -f document.md

# Brave summarizer example
aifr 'Latest AI news' --provider brave
```

---

## 🔗 Provider Comparison

| Provider | Models | Context | Token Counts | Best For |
|----------|--------|---------|--------------|----------|
| **Sherlock** | Bielik, PLLuM, Llama, DeepSeek | Varies | ✅ Yes | Polish language, default |
| **OpenAI** | GPT-4, GPT-3.5 | Large | ✅ Yes | High-quality responses |
| **OpenWebUI** | Ollama models | Varies | ✅ Yes | Privacy, local hosting |
| **Brave** | Summarizer | N/A | ❌ No | Web search + summarization |

---

## 🎯 Use Cases

### OpenAI for Production
```bash
export OPENAI_API_KEY="sk-..."
aifr 'Write production-ready code' -m gpt-4 -f app.py --stats
```

### OpenWebUI for Privacy
```bash
# Self-hosted, no data leaves your network
aifr 'Sensitive business analysis' -f confidential.txt
```

### Brave for Research
```bash
# Combines web search + AI summarization
aifr 'What are the top AI companies in 2025?'
```

### Sherlock for Polish
```bash
# Best for Polish language tasks
export SHERLOCK_API_KEY="key"
aifr 'Podsumuj ten dokument' -f raport.md -m Bielik-11B-v2.6
```

---

## 🔮 What's Next (v1.3 Roadmap)

Potential features:
- [ ] Azure OpenAI support
- [ ] Anthropic Claude API support
- [ ] Google Gemini API support
- [ ] Streaming responses
- [ ] Provider-specific model recommendations
- [ ] Cost tracking per provider

---

## ⚠️ Known Limitations

1. **Brave API**: Only supports summarization, not full conversation
2. **Token counts**: Brave provider returns `None` for all token fields
3. **Model validation**: No automatic check if model exists for provider
4. **OpenWebUI**: Requires manual base_url configuration

---

## 📝 Full Changelog

### Added
- ✨ Support for OpenAI API
- ✨ Support for OpenWebUI (local)
- ✨ Support for Brave Summarizer API
- ✨ `providers.py` module with abstract provider architecture
- ✨ Auto-detection of provider from environment variables
- ✨ `provider` and `base_url` fields in config
- ✨ 16 new tests for providers

### Changed
- 🔄 `api.py` refactored to use provider system
- 🔄 `config.py` supports multiple API key env vars
- 🔄 `call_llm()` now accepts `provider_name` and `base_url` parameters
- 🔄 Version bumped to 1.2.0

### Fixed
- 🐛 Better error messages with provider context
- 🐛 Proper handling of APIs without token counts

---

## 🙏 Credits

- **Provider Architecture**: Inspired by LangChain's provider pattern
- **OpenWebUI**: Compatible with OpenWebUI project
- **Brave API**: Integration with Brave Search Summarizer

---

**Enjoy multi-provider support!** 🎉

For questions or issues, open a GitHub issue or check the documentation.
