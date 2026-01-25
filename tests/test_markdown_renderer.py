"""Tests for markdown_renderer module."""
from __future__ import annotations

import pytest

from aifr.markdown_renderer import (
    RETRO_COLORS,
    MarkdownRenderer,
    bold,
    dim,
    italic,
    render_markdown,
    reset_color,
    rgb_to_ansi,
    rgb_to_ansi_bg,
)


def test_rgb_to_ansi() -> None:
    """Test RGB to ANSI foreground conversion."""
    result = rgb_to_ansi(255, 128, 64)
    assert result == "\033[38;2;255;128;64m"


def test_rgb_to_ansi_bg() -> None:
    """Test RGB to ANSI background conversion."""
    result = rgb_to_ansi_bg(255, 128, 64)
    assert result == "\033[48;2;255;128;64m"


def test_reset_color() -> None:
    """Test ANSI reset code."""
    assert reset_color() == "\033[0m"


def test_bold() -> None:
    """Test ANSI bold code."""
    assert bold() == "\033[1m"


def test_italic() -> None:
    """Test ANSI italic code."""
    assert italic() == "\033[3m"


def test_dim() -> None:
    """Test ANSI dim code."""
    assert dim() == "\033[2m"


def test_retro_colors_defined() -> None:
    """Test that retro colors are properly defined."""
    required_keys = ['cyan', 'yellow', 'coral', 'red', 'brown']
    
    for key in required_keys:
        assert key in RETRO_COLORS
        color = RETRO_COLORS[key]
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)


def test_markdown_renderer_init() -> None:
    """Test MarkdownRenderer initialization."""
    renderer = MarkdownRenderer()
    assert renderer.in_code_block is False
    assert renderer.code_block_lang is None


def test_render_inline_code() -> None:
    """Test inline code rendering."""
    text = "Here is some `code` inline."
    result = render_markdown(text)
    
    # Should contain ANSI codes
    assert "\033[38;2" in result
    assert "\033[0m" in result
    # Should still contain the original text (minus backticks)
    assert "code" in result


def test_render_bold() -> None:
    """Test bold text rendering."""
    text = "This is **bold** text."
    result = render_markdown(text)
    
    # Should contain bold ANSI code
    assert "\033[1m" in result
    # Should contain color code
    assert "\033[38;2" in result
    # Should contain reset
    assert "\033[0m" in result
    assert "bold" in result


def test_render_italic() -> None:
    """Test italic text rendering."""
    text = "This is *italic* text."
    result = render_markdown(text)
    
    # Should contain italic ANSI code
    assert "\033[3m" in result
    # Should contain color code
    assert "\033[38;2" in result
    assert "italic" in result


def test_render_link() -> None:
    """Test link rendering."""
    text = "Check out [this link](https://example.com)."
    result = render_markdown(text)
    
    # Should contain both link text and URL
    assert "this link" in result
    assert "https://example.com" in result
    # Should contain ANSI codes
    assert "\033[" in result


def test_render_header() -> None:
    """Test header rendering."""
    text = "# Header Level 1"
    result = render_markdown(text)
    
    # Should contain bold and color codes
    assert "\033[1m" in result
    assert "\033[38;2" in result
    assert "Header Level 1" in result
    
    # Test different levels
    text = "## Header Level 2"
    result = render_markdown(text)
    assert "Header Level 2" in result


def test_render_bullet_point() -> None:
    """Test bullet point rendering."""
    text = "- Item one\n• Item two\n* Item three"
    result = render_markdown(text)
    
    # Should contain bullet symbol
    assert "•" in result
    # Should contain items
    assert "Item one" in result
    assert "Item two" in result
    assert "Item three" in result


def test_render_code_block() -> None:
    """Test code block rendering."""
    text = "```python\ndef hello():\n    print('Hi')\n```"
    result = render_markdown(text)
    
    # Should contain code block markers (Unicode box drawing)
    assert "┌─" in result or "└─" in result
    # Should contain the code
    assert "def hello():" in result
    assert "print('Hi')" in result
    # Should indicate language
    assert "python" in result


def test_render_code_block_no_language() -> None:
    """Test code block without language specification."""
    text = "```\nsome code\n```"
    result = render_markdown(text)
    
    # Should still render
    assert "some code" in result
    assert "code" in result  # Default label


def test_render_multiline() -> None:
    """Test rendering multiple lines."""
    text = "Line 1\nLine 2\nLine 3"
    result = render_markdown(text)
    
    # All lines should be present
    assert "Line 1" in result
    assert "Line 2" in result
    assert "Line 3" in result


def test_render_empty_string() -> None:
    """Test rendering empty string."""
    result = render_markdown("")
    assert result == ""


def test_render_complex_markdown() -> None:
    """Test rendering complex markdown with multiple elements."""
    text = """
# Title

This has **bold** and *italic* and `code`.

## Subsection

- Item 1
- Item 2

```python
def test():
    pass
```

[Link](http://example.com)
"""
    result = render_markdown(text)
    
    # Should contain all elements
    assert "Title" in result
    assert "bold" in result
    assert "italic" in result
    assert "code" in result
    assert "Subsection" in result
    assert "Item 1" in result
    assert "Item 2" in result
    assert "def test():" in result
    assert "Link" in result
    assert "http://example.com" in result
    
    # Should have ANSI codes
    assert "\033[" in result


def test_code_block_state_management() -> None:
    """Test that code block state is managed correctly."""
    renderer = MarkdownRenderer()
    
    # Initially not in code block
    assert renderer.in_code_block is False
    
    # After opening code block
    renderer._render_line("```python")
    assert renderer.in_code_block is True
    assert renderer.code_block_lang == "python"
    
    # After closing code block
    renderer._render_line("```")
    assert renderer.in_code_block is False
    assert renderer.code_block_lang is None
