"""Tests for gradient_display module."""
from __future__ import annotations

import pytest

from aifr.gradient_display import (
    RETRO_COLORS,
    get_gradient_color,
    interpolate_color,
    load_version_ascii,
    print_gradient_ascii,
    print_version_banner,
    reset_color,
    rgb_to_ansi,
)


def test_rgb_to_ansi() -> None:
    """Test RGB to ANSI conversion."""
    result = rgb_to_ansi(255, 128, 64)
    assert result == "\033[38;2;255;128;64m"


def test_reset_color() -> None:
    """Test ANSI reset code."""
    assert reset_color() == "\033[0m"


def test_interpolate_color() -> None:
    """Test color interpolation."""
    color1 = (0, 0, 0)
    color2 = (100, 100, 100)
    
    # At t=0, should return color1
    result = interpolate_color(color1, color2, 0.0)
    assert result == (0, 0, 0)
    
    # At t=1, should return color2
    result = interpolate_color(color1, color2, 1.0)
    assert result == (100, 100, 100)
    
    # At t=0.5, should return midpoint
    result = interpolate_color(color1, color2, 0.5)
    assert result == (50, 50, 50)


def test_get_gradient_color_single_color() -> None:
    """Test gradient with single color."""
    colors = [(255, 0, 0)]
    result = get_gradient_color(0.0, colors)
    assert result == (255, 0, 0)
    
    result = get_gradient_color(1.0, colors)
    assert result == (255, 0, 0)


def test_get_gradient_color_two_colors() -> None:
    """Test gradient with two colors."""
    colors = [(0, 0, 0), (100, 100, 100)]
    
    # Start should be first color
    result = get_gradient_color(0.0, colors)
    assert result == (0, 0, 0)
    
    # End should be second color
    result = get_gradient_color(1.0, colors)
    assert result == (100, 100, 100)
    
    # Middle should be interpolated
    result = get_gradient_color(0.5, colors)
    assert result == (50, 50, 50)


def test_get_gradient_color_multiple_colors() -> None:
    """Test gradient with multiple colors."""
    colors = [(0, 0, 0), (100, 100, 100), (200, 200, 200)]
    
    # Test positions
    result = get_gradient_color(0.0, colors)
    assert result == (0, 0, 0)
    
    result = get_gradient_color(1.0, colors)
    assert result == (200, 200, 200)
    
    # Middle of first segment (0 to 0.5)
    result = get_gradient_color(0.25, colors)
    assert result == (50, 50, 50)


def test_get_gradient_color_clamping() -> None:
    """Test that position is clamped to [0, 1]."""
    colors = [(0, 0, 0), (100, 100, 100)]
    
    # Position < 0 should be clamped to 0
    result = get_gradient_color(-0.5, colors)
    assert result == (0, 0, 0)
    
    # Position > 1 should be clamped to 1
    result = get_gradient_color(1.5, colors)
    assert result == (100, 100, 100)


def test_print_gradient_ascii(capsys: pytest.CaptureFixture) -> None:
    """Test ASCII art printing with gradient."""
    ascii_art = "Line 1\nLine 2\nLine 3"
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    
    print_gradient_ascii(ascii_art, colors)
    
    captured = capsys.readouterr()
    # Should contain ANSI codes and the text
    assert "Line 1" in captured.out
    assert "Line 2" in captured.out
    assert "Line 3" in captured.out
    assert "\033[38;2" in captured.out  # ANSI color code present
    assert "\033[0m" in captured.out  # Reset code present


def test_load_version_ascii() -> None:
    """Test loading version ASCII art."""
    ascii_art = load_version_ascii()
    
    # Should return some text
    assert len(ascii_art) > 0
    
    # Should be multi-line
    assert '\n' in ascii_art or len(ascii_art) > 10


def test_print_version_banner(capsys: pytest.CaptureFixture) -> None:
    """Test version banner printing."""
    print_version_banner("1.2.0")
    
    captured = capsys.readouterr()
    
    # Should contain version number
    assert "1.2.0" in captured.out
    
    # Should contain ANSI codes
    assert "\033[" in captured.out


def test_retro_colors_defined() -> None:
    """Test that retro colors are properly defined."""
    assert len(RETRO_COLORS) == 5
    
    # Check that all are RGB tuples
    for color in RETRO_COLORS:
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)
