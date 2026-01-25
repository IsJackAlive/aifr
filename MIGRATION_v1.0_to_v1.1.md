# Migration Guide: v1.0 → v1.1

## Overview

Aifr v1.1 introduces a **breaking change** to the CLI interface. The custom `$` syntax has been replaced with standard argparse flags for better shell compatibility.

## Why This Change?

The old `$ask:`, `$file:`, `$cons:` syntax caused issues with Bash shell variable interpolation, requiring users to constantly escape with single quotes. The new syntax uses standard CLI flags that work naturally in all shells.

## Quick Reference

| Old (v1.0) | New (v1.1) |
|------------|------------|
| `$ask: <text>` | `<text>` (positional) or `-p <text>` |
| `$file: <path>` | `-f <path>` or `--file <path>` |
| `$cons: <cmd>` | `-c <cmd>` or `--console <cmd>` |
| `$model: <name>` | `-m <name>` or `--model <name>` |
| `$context_limit: <n>` | `--context-limit <n>` |
| `--reset-context` | `--reset` or `--new` |
| N/A | `--stats` or `--info` (new!) |

## Migration Examples

### Simple Question

**Old:**
```bash
aifr '$ask: What is Python?'
# or
aifr $ask: What is Python?  # Often failed due to shell expansion
```

**New:**
```bash
aifr 'What is Python?'
# or
aifr -p 'What is Python?'
```

### With File

**Old:**
```bash
aifr '$ask: Summarize this $file: README.md'
```

**New:**
```bash
aifr 'Summarize this' -f README.md
# or
aifr -f README.md 'Summarize this'  # Order doesn't matter
```

### With Console Command

**Old:**
```bash
aifr '$ask: What files are here? $cons: "ls -la"'
```

**New:**
```bash
aifr 'What files are here?' -c 'ls -la'
```

### Pipe Input

**Old:**
```bash
cat file.txt | aifr '$ask: Analyze $cons:'
```

**New:**
```bash
cat file.txt | aifr 'Analyze'
# Stdin is auto-detected, no special flag needed
```

### Model Selection

**Old:**
```bash
aifr '$ask: Complex task $model: gpt-4'
```

**New:**
```bash
aifr 'Complex task' -m gpt-4
```

### Reset Session

**Old:**
```bash
aifr --reset-context
```

**New:**
```bash
aifr --reset
# or
aifr --new
```

### Combined Flags

**Old:**
```bash
aifr '$ask: Debug this $file: app.py $cons: "python app.py" $model: gpt-4'
```

**New:**
```bash
aifr 'Debug this' -f app.py -c 'python app.py' -m gpt-4
```

## New Features in v1.1

### 1. Statistics Flag

Show detailed metadata about the request:

```bash
aifr 'What is AI?' --stats
```

Output includes:
- Agent type used (Debugger, Summarizer, Creative, etc.)
- Model name
- Token usage (input/output/total)
- Context window size

### 2. Agentic Behavior

The system now automatically selects specialized "agents" based on your query:

- **Debugger Agent**: Triggered by error keywords or `-c` flag
  ```bash
  aifr 'Fix this błąd' -c 'pytest'  # Uses Debugger agent
  ```

- **Summarizer Agent**: Triggered by "podsumuj", "streść" or large files
  ```bash
  aifr 'Podsumuj' -f large-doc.md  # Uses Summarizer agent
  ```

- **Creative Agent**: Triggered by "opowiadanie", "wiersz", etc.
  ```bash
  aifr 'Napisz opowiadanie o kocie'  # Uses Creative agent
  ```

- **Coder Agent**: Triggered by code keywords + file
  ```bash
  aifr 'Review this code' -f script.py  # Uses Coder agent
  ```

### 3. Improved Context Management

- **Sliding Window**: Keeps only last 5 conversation turns (configurable)
- Prevents context overflow on long conversations
- More predictable token usage

## Updating Scripts

If you have shell scripts using aifr v1.0 syntax, here's a sed-based migration:

```bash
# Simple replacement (basic cases)
sed -i "s/\$ask: //" your_script.sh
sed -i "s/\$file: /-f /" your_script.sh
sed -i "s/\$cons: /-c /" your_script.sh
sed -i "s/\$model: /-m /" your_script.sh
sed -i "s/--reset-context/--reset/" your_script.sh
```

**Note**: Complex cases with multiple parameters will need manual review.

## Interactive Mode

Interactive mode now has improved UX:

**Old:**
```
aifr> $ask: What is this?
```

**New:**
```
aifr> What is this?
```

Just type your question directly - no `$ask:` prefix needed!

## Backward Compatibility

**There is NO backward compatibility layer.** The old syntax will produce errors:

```bash
$ aifr '$ask: test'
Error: prompt required (provide as argument or use -p/--prompt)
```

You **must** update to the new syntax.

## Help & Documentation

Get help anytime:

```bash
aifr --help    # Full usage guide
aifr --version # Check version (should be 1.1.0+)
```

## Troubleshooting

### Error: "prompt required"

**Cause**: Using old `$ask:` syntax

**Fix**: Remove `$ask:` and use positional argument or `-p` flag

### Shell still interpreting variables

**Cause**: Not quoting arguments properly

**Fix**: Always quote multi-word arguments:
```bash
aifr 'My question with spaces'  # Good
aifr My question with spaces     # Bad (treated as separate args)
```

### Flags not recognized

**Cause**: Mixing old and new syntax

**Fix**: Use only new flag syntax, don't mix `$` markers with flags

## Getting Support

- Check `aifr --help` for syntax
- Run `aifr --version` to verify you're on v1.1+
- Test with simple commands first: `aifr 'test'`
- Use `--stats` to debug agent/model selection

## Summary

✅ **DO:**
- Use positional arguments or `-p` for prompts
- Use `-f`, `-c`, `-m` flags for options
- Quote arguments with spaces
- Use `--stats` to debug

❌ **DON'T:**
- Use old `$ask:`, `$file:`, `$cons:` syntax
- Mix old and new syntax
- Forget to quote multi-word arguments

---

**Questions?** Open an issue on GitHub or check the updated README.md
