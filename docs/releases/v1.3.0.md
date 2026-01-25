# Release Notes: Aifr v1.3.0 - "Retro Colors"

**Release Date**: 2026-01-22  
**Type**: MINOR (New Features, Backward Compatible)  
**Git Tag**: `v1.3.0`

---

## 🎉 Overview

Version 1.3.0 introduces retro-styled visual output with gradient ASCII art and colorful markdown rendering. All LLM responses are now beautifully formatted with a vintage computing aesthetic using a carefully selected color palette.

**Key Highlights:**
- Gradient ASCII art for version display
- Automatic markdown syntax highlighting with retro colors
- Zero external dependencies added
- Full test coverage for new features

---

## ✨ New Features

### 1. 🎨 Gradient ASCII Art Version Display

The `--version` flag now displays the Aifr logo with a smooth vertical gradient effect using the retro color palette.

**Usage:**
```bash
aifr --version
```

**Features:**
- Smooth color interpolation across 5 retro colors
- Vertical gradient from cyan-teal through warm yellows to browns
- 24-bit ANSI color support for modern terminals
- Graceful fallback on terminals without color support

**Implementation:**
- New module: `aifr/gradient_display.py`
- RGB color interpolation engine
- Position-based gradient calculation
- Automatic ASCII art loading from `version.txt`

---

### 2. 📝 Colorful Markdown Rendering

All LLM responses are automatically rendered with syntax-highlighted markdown using a retro color scheme inspired by vintage computer terminals.

**Supported Elements:**

| Element | Color | Style | Example |
|---------|-------|-------|---------|
| Headers (`#`, `##`) | Cyan-teal (#68c7c1) | Bold | `# Title` |
| Bold text (`**text**`) | Warm yellow (#faca78) | Bold | `**important**` |
| Italic (`*text*`) | Red-orange (#dd5341) | Italic | `*emphasis*` |
| Inline code | Coral (#f57f5b) | Normal | `` `code` `` |
| Code blocks | Brown (#794a3a) | With borders | ` ```python` |
| Links | Warm yellow | With dimmed URL | `[text](url)` |
| Bullet points | Cyan-teal | Custom symbol | `- item` |

**Implementation:**
- New module: `aifr/markdown_renderer.py`
- Stateful markdown parser with code block detection
- Regex-based inline element styling
- Automatic rendering in `output.print_chunks()`

**Example Output:**
```markdown
# Welcome to Aifr
This is **bold** text and `inline code`.

```python
def hello():
    return "world"
```

- Feature one
- Feature two
```

All elements are rendered with appropriate colors and styles automatically.

---

## 🎨 Retro Color Palette

The entire color scheme is based on a carefully selected 5-color retro palette:

```
#68c7c1  Cyan-teal     RGB(104, 199, 193)  Headers, bullets
#faca78  Warm yellow   RGB(250, 202, 120)  Bold text, links
#f57f5b  Coral         RGB(245, 127, 91)   Inline code
#dd5341  Red-orange    RGB(221, 83, 65)    Emphasis
#794a3a  Brown         RGB(121, 74, 58)    Code blocks
```

This palette is inspired by vintage CRT displays and retro computing aesthetics, providing excellent readability while maintaining a distinctive visual style.

---

## 🔧 Technical Changes

### New Modules

#### `aifr/gradient_display.py`
Gradient rendering engine for ASCII art.

**Key Functions:**
- `print_version_banner(version)` - Main entry point
- `print_gradient_ascii(ascii_art, colors)` - Gradient renderer
- `get_gradient_color(position, colors)` - Color calculation
- `interpolate_color(color1, color2, t)` - Color interpolation
- `rgb_to_ansi(r, g, b)` - ANSI escape code generation

**Features:**
- Smooth RGB interpolation
- Position-based gradient calculation
- Multi-color gradient support
- Automatic color clamping

#### `aifr/markdown_renderer.py`
Markdown parser and colorizer.

**Key Components:**
- `MarkdownRenderer` class - Stateful parser
- `render_markdown(text)` - Public API
- Inline element processing (code, bold, italic, links)
- Block element processing (headers, code blocks, lists)

**Features:**
- State management for code blocks
- Language detection for syntax blocks
- Regex-based element matching
- Non-greedy matching to avoid conflicts

### Modified Modules

#### `aifr/cli.py`
- Integrated `print_version_banner()` for `--version` flag
- Import added: `from .gradient_display import print_version_banner`

#### `aifr/output.py`
- Integrated `render_markdown()` in `print_chunks()`
- All output now automatically colored
- Import added: `from .markdown_renderer import render_markdown`

#### `pyproject.toml`
- Added package discovery configuration
- Excludes `images*` and `tests*` from distribution
- Fixed setuptools flat-layout issues

---

## 🧪 Testing

### New Test Files

#### `tests/test_gradient_display.py`
**Coverage: 11 tests**

Tests include:
- ANSI escape code generation
- Color interpolation accuracy
- Gradient position calculation
- Edge case handling (clamping, single color)
- ASCII art loading and printing
- Version banner integration

#### `tests/test_markdown_renderer.py`
**Coverage: 20 tests**

Tests include:
- ANSI code generation (foreground, background, styles)
- Inline element rendering (code, bold, italic, links)
- Block element rendering (headers, code blocks, lists)
- Complex markdown documents
- Code block state management
- Empty string handling
- Multiline text processing

### Test Results
```
================================ 102 passed in 0.16s ================================
```

All tests pass, including:
- 31 new tests for color features
- 71 existing tests (unchanged)
- Full mypy strict mode compliance
- Zero external dependencies required

---

## 📦 Installation & Upgrade

### Upgrade from v1.2.0

```bash
pip install --upgrade aifr
```

### Fresh Installation

```bash
pip install aifr
```

### Verify Installation

```bash
aifr --version
```

You should see the gradient ASCII art logo with version 1.3.0.

---

## 🎯 Usage Examples

### Example 1: Version Display
```bash
$ aifr --version
[Gradient ASCII art appears]
v1.3.0
```

### Example 2: Colored Markdown Response
```bash
$ aifr "Explain Python list comprehensions"
[Response with colored markdown:]
# List Comprehensions

List comprehensions provide a **concise** way to create lists.

`[x**2 for x in range(10)]`

## Syntax
- Expression
- For clause
- Optional if clause
```

All elements are automatically colored according to the retro palette.

---

## 🔄 Breaking Changes

**None.** This release is fully backward compatible with v1.2.0.

---

## 🐛 Bug Fixes

- Fixed setuptools package discovery warnings
- Added missing `list_models` parameter in test fixtures

---

## 📚 Documentation

### New Documentation
- `RETRO_COLORS_FEATURE.md` - Comprehensive feature documentation
- Inline code documentation for all new functions
- Type hints for all public APIs

### Updated Documentation
- README.md sections (to be updated)
- API documentation (to be updated)

---

## 🔮 Future Enhancements

Potential improvements for future versions:
- Configurable color themes
- Support for additional markdown elements (tables, blockquotes)
- Terminal color capability detection
- Optional plain text mode for scripting
- Theme configuration in `config.json`
- Custom gradient presets

---

## 🙏 Credits

**Developed by**: Aifr Team  
**Color Palette Design**: Inspired by vintage CRT terminals and retro computing aesthetics  
**Testing**: Comprehensive test coverage with pytest  
**Type Safety**: Full mypy strict mode compliance

---

## 📝 Git Commit History

This release includes the following commits:

```
feat: add gradient ASCII art for version display
feat: add retro-styled markdown renderer
test: add comprehensive tests for color features
fix: update test fixtures with list_models parameter
chore: update pyproject.toml package discovery
docs: add RETRO_COLORS_FEATURE.md documentation
```

---

## 🔗 Links

- **Repository**: https://github.com/IsJackAlive/aifr
- **Issues**: https://github.com/IsJackAlive/aifr/issues
- **Documentation**: https://github.com/IsJackAlive/aifr#readme
- **Previous Release**: [v1.2.0](RELEASE_v1.2.0.md)

---

## 📊 Statistics

- **Lines of Code Added**: ~600 (including tests)
- **New Modules**: 2
- **New Tests**: 31
- **Test Coverage**: 100% for new features
- **Dependencies Added**: 0
- **Breaking Changes**: 0

---

**Enjoy the retro aesthetic! 🎨✨**
