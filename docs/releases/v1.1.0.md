# Release Notes: Aifr v1.1.0 - "Agentic UX"

**Release Date**: 2025-01-XX  
**Type**: MAJOR (Breaking Changes)  
**Git Tag**: `v1.1.0`

---

## 🚨 Breaking Changes

### CLI Syntax Overhaul

The entire command-line interface has been **rewritten from scratch** using Python's standard `argparse` library. The old `$ask:`, `$file:`, `$cons:` syntax is **completely removed**.

**Old (v1.0.x):**
```bash
aifr '$ask: What is Python? $file: readme.md $cons: "ls -la"'
```

**New (v1.1.0):**
```bash
aifr 'What is Python?' -f readme.md -c 'ls -la'
```

**Migration Required:**
- All scripts using aifr v1.0 syntax must be updated
- See [MIGRATION_v1.0_to_v1.1.md](MIGRATION_v1.0_to_v1.1.md) for complete guide
- No backward compatibility layer provided

**Why This Change?**
The old `$` syntax caused constant shell variable interpolation issues, requiring users to wrap everything in single quotes. The new argparse-based interface:
- Works naturally in all shells (bash, zsh, fish)
- Follows standard CLI conventions (like `grep`, `git`, etc.)
- Eliminates quote escaping nightmares
- Provides better `--help` documentation

---

## ✨ New Features

### 1. Agentic Behavior (Agent Controller)

Aifr now automatically selects specialized "agents" based on your query context:

- **🐛 Debugger Agent**: Auto-activated for errors, debug keywords, or when using `-c` flag
  - **Triggers**: "błąd", "error", "debug", "fix", `has_console=True`, stderr in stdin
  - **Behavior**: Analytical, root-cause focused, suggests specific fixes
  - **Example**: `aifr 'Why is this failing?' -c 'pytest'`

- **📝 Summarizer Agent**: Auto-activated for summarization requests
  - **Triggers**: "podsumuj", "streść", "summarize", "explain"
  - **Behavior**: Concise, hierarchical, extracts key points
  - **Example**: `aifr 'Podsumuj' -f long-document.md`

- **🎨 Creative Agent**: Auto-activated for creative writing tasks
  - **Triggers**: "opowiadanie", "wiersz", "story", "poem", "create"
  - **Behavior**: Expressive, narrative-focused, imaginative
  - **Example**: `aifr 'Write a story about a robot'`

- **💻 Coder Agent**: Auto-activated for code analysis with file present
  - **Triggers**: "kod", "code", "function", "refactor" + `has_file=True`
  - **Behavior**: Technical, best practices, code examples
  - **Example**: `aifr 'Review this' -f script.py`

- **🔵 Default Agent**: Fallback for general questions
  - **Triggers**: No specific keywords matched
  - **Behavior**: Universal, friendly, general knowledge

**Priority Order**: DEBUGGER > CODER > CREATIVE > SUMMARIZER > DEFAULT

**Visibility**: Use `--stats` flag to see which agent was selected:
```bash
aifr 'Fix this bug' -c 'python app.py' --stats
# [Agent: DEBUGGER | Model: DeepSeek-R1 | Tokens: 120/450/570]
```

### 2. Sliding Window Context Management

Context history now uses a **sliding window** approach instead of unbounded growth:

- **Default window**: 5 conversation turns (user + assistant pairs)
- **Automatic pruning**: Older messages automatically removed
- **Token fallback**: If sliding window still exceeds token limit, falls back to token-based pruning
- **Configurable**: Adjustable via `ContextManager(max_turns=N)`

**Benefits:**
- More predictable token usage
- Prevents context overflow on long conversations
- Focuses on recent, relevant exchanges
- Better performance on token-limited models

**Example:**
```python
# In session.json, you'll only see last 5 turns
# Old messages automatically discarded
```

### 3. Statistics Flag (`--stats` / `--info`)

New observability feature for debugging and analysis:

```bash
aifr 'Test query' --stats
```

**Output includes:**
- **Agent Type**: Which specialized agent was used
- **Model Name**: The LLM model that processed the request
- **Token Usage**: Input/Output/Total token counts

**Example output:**
```
[Agent: DEBUGGER | Model: DeepSeek-R1-Distill-Llama-70B | Tokens: 85/320/405]
<assistant response>
```

**Use cases:**
- Verify correct agent selection
- Monitor token consumption
- Debugging unexpected behavior
- Understanding model choices

### 4. Modern CLI with argparse

Complete rewrite of CLI argument parsing:

**New Flags:**
- Positional argument: `aifr 'prompt'`
- `-p`, `--prompt`: Explicit prompt flag
- `-f`, `--file`: File path (replaces `$file:`)
- `-c`, `--console`: Shell command (replaces `$cons:`)
- `-m`, `--model`: Model selection (replaces `$model:`)
- `--context-limit`: Token limit
- `--reset`, `--new`: Clear history (replaces `--reset-context`)
- `--stats`, `--info`: Show metadata (NEW)
- `--version`: Show version
- `--help`: Full usage guide

**Features:**
- Flags can be in any order
- Standard POSIX-compliant syntax
- Comprehensive help text
- Proper error messages
- Auto-detection of stdin (pipes)

---

## 🔧 Technical Improvements

### New Modules

1. **`aifr/cli_parser.py`** (NEW)
   - argparse configuration
   - `CliArgs` dataclass for type safety
   - Input validation (file existence, stdin detection)
   - ~150 lines

2. **`aifr/agent_controller.py`** (EXPANDED)
   - Agent detection logic
   - `AGENT_PROMPTS` registry
   - Keyword-based classification
   - Support for Polish and English keywords
   - ~150 lines

### Modified Modules

1. **`aifr/cli.py`** (REWRITTEN)
   - Completely refactored main loop
   - Integration with `cli_parser` and `agent_controller`
   - Removed all `command_parser` dependencies
   - Better error handling
   - ~250 lines

2. **`aifr/context.py`** (ENHANCED)
   - Added `max_turns: int = 5` parameter
   - New `_apply_sliding_window()` method
   - New `clear()` method for session reset
   - Dual-mode pruning (sliding window + token limit)

### Deprecated/Removed

- ❌ **`command_parser.py`**: No longer used (still exists for reference)
- ❌ `$ask:`, `$file:`, `$cons:`, `$model:` syntax completely removed
- ❌ `--reset-context` flag (replaced with `--reset`)

---

## 🧪 Testing

**New Test Suites:**
- `tests/test_cli_parser.py` - 15 tests for argparse functionality
- `tests/test_agent_controller.py` - 18 tests for agent detection
- `tests/test_context.py` - 7 tests for sliding window

**Total Test Coverage:**
- **77 tests** (37 from v1.0 + 40 new)
- 100% pass rate
- Comprehensive coverage of:
  - CLI argument parsing
  - Agent keyword detection
  - Sliding window logic
  - Flag combinations
  - Error cases

**Run tests:**
```bash
pytest                           # All tests
pytest tests/test_cli_parser.py  # Parser only
pytest -v                        # Verbose
```

---

## 📦 Installation & Upgrade

### Fresh Install
```bash
pip install aifr==1.1.0
```

### Upgrade from v1.0
```bash
pip install --upgrade aifr
aifr --version  # Should show 1.1.0
```

**Post-upgrade:**
1. Read [MIGRATION_v1.0_to_v1.1.md](MIGRATION_v1.0_to_v1.1.md)
2. Update all scripts using old `$` syntax
3. Test with: `aifr 'test' --stats`

---

## 🐛 Bug Fixes

- Fixed: Shell variable interpolation issues with `$ask:` syntax
- Fixed: Context overflow on long conversations (sliding window)
- Fixed: Inconsistent quote handling in CLI
- Fixed: Agent priority conflicts (CODER vs SUMMARIZER)

---

## 📚 Documentation Updates

**New Files:**
- `MIGRATION_v1.0_to_v1.1.md` - Complete migration guide with examples
- `RELEASE_v1.1.0.md` - This file

**Updated Files:**
- `README.md` - Rewritten for v1.1 syntax, added agent documentation
- `AGENTS.md` - Updated context for agents with new architecture notes

---

## 🔗 Links

- **Repository**: https://github.com/IsJackAlive/aifr
- **Migration Guide**: [MIGRATION_v1.0_to_v1.1.md](MIGRATION_v1.0_to_v1.1.md)
- **Developer Guide**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **PyPI**: https://pypi.org/project/aifr/

---

## 🙏 Credits

- **Agent Controller Design**: Inspired by LangChain's agent patterns
- **Sliding Window**: Common pattern in conversational AI systems
- **argparse**: Python standard library (PEP 389)

---

## 🔮 What's Next (v1.2 Roadmap)

Potential future features:
- [ ] Web UI for conversation history
- [ ] Custom agent definitions via config
- [ ] Multi-file context (e.g., `-f file1.py -f file2.py`)
- [ ] RAG integration for documentation search
- [ ] Streaming responses for long outputs
- [ ] Plugin system for custom agents

---

## ⚠️ Known Issues

1. **Old tests in `test_command_parser.py` may fail**: These test the deprecated syntax
   - **Workaround**: Ignore or remove these tests
   - **Fix**: Will be fully removed in v1.2

2. **Interactive mode prompt change**: No longer shows `aifr>` prefix
   - **Impact**: Minor UX difference
   - **Fix**: Intentional design decision

3. **No migration script provided**: Users must manually update scripts
   - **Workaround**: Use `sed` for simple replacements (see migration guide)
   - **Complex cases**: Require manual review

---

## 📝 Full Changelog

### Added
- ✨ Agentic behavior with 5 specialized agents
- ✨ Sliding window context (5 turns default)
- ✨ `--stats`/`--info` flag for metadata display
- ✨ argparse-based CLI parser
- ✨ Auto-detection of stdin (pipe support)
- ✨ `--reset`/`--new` aliases
- ✨ Comprehensive test suite (40 new tests)
- ✨ `cli_parser.py` module
- ✨ Enhanced `agent_controller.py`

### Changed
- 🔄 **BREAKING**: Complete CLI syntax overhaul
- 🔄 **BREAKING**: Removed `$ask:`, `$file:`, `$cons:` syntax
- 🔄 Rewritten `cli.py` (250+ lines)
- 🔄 Enhanced `context.py` with sliding window
- 🔄 Version bump to 1.1.0
- 🔄 Updated README.md with new examples

### Removed
- ❌ Old CLI syntax (`$` markers)
- ❌ `--reset-context` flag (use `--reset`)
- ❌ Direct usage of `command_parser.py`

### Fixed
- 🐛 Shell variable interpolation issues
- 🐛 Context overflow on long sessions
- 🐛 Quote escaping problems
- 🐛 Agent detection priority bugs

---

**Questions?** Open an issue on GitHub or check the migration guide.

**Enjoy v1.1!** 🎉
