"""Gradient ASCII art display with retro colors."""
from __future__ import annotations

from pathlib import Path
from typing import Optional


# Retro color palette (RGB hex values)
RETRO_COLORS = [
    (0x68, 0xc7, 0xc1),  # Cyan-teal
    (0xfa, 0xca, 0x78),  # Warm yellow
    (0xf5, 0x7f, 0x5b),  # Coral
    (0xdd, 0x53, 0x41),  # Red-orange
    (0x79, 0x4a, 0x3a),  # Brown
]


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB to ANSI escape code for 24-bit color."""
    return f"\033[38;2;{r};{g};{b}m"


def reset_color() -> str:
    """Return ANSI reset code."""
    return "\033[0m"


def interpolate_color(color1: tuple[int, int, int], color2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """
    Interpolate between two RGB colors.
    
    Args:
        color1: First RGB color tuple
        color2: Second RGB color tuple
        t: Interpolation factor (0.0 to 1.0)
    
    Returns:
        Interpolated RGB color tuple
    """
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return (r, g, b)


def get_gradient_color(position: float, colors: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    """
    Get color from gradient at given position.
    
    Args:
        position: Position in gradient (0.0 to 1.0)
        colors: List of RGB color tuples
    
    Returns:
        RGB color tuple at position
    """
    if not colors:
        return (255, 255, 255)
    if len(colors) == 1:
        return colors[0]
    
    # Clamp position
    position = max(0.0, min(1.0, position))
    
    # Calculate segment
    segment_count = len(colors) - 1
    segment_position = position * segment_count
    segment_index = int(segment_position)
    
    # Handle edge case
    if segment_index >= segment_count:
        return colors[-1]
    
    # Interpolate within segment
    local_t = segment_position - segment_index
    return interpolate_color(colors[segment_index], colors[segment_index + 1], local_t)


def print_gradient_ascii(ascii_art: str, colors: Optional[list[tuple[int, int, int]]] = None) -> None:
    """
    Print ASCII art with vertical gradient.
    
    Args:
        ascii_art: Multi-line ASCII art string
        colors: Optional list of RGB color tuples (uses RETRO_COLORS if None)
    """
    if colors is None:
        colors = RETRO_COLORS
    
    lines = ascii_art.strip().split('\n')
    total_lines = len(lines)
    
    for i, line in enumerate(lines):
        # Calculate position in gradient (0.0 at top, 1.0 at bottom)
        position = i / (total_lines - 1) if total_lines > 1 else 0.0
        color = get_gradient_color(position, colors)
        
        # Print line with color
        print(f"{rgb_to_ansi(*color)}{line}{reset_color()}")


def load_version_ascii() -> str:
    """
    Load ASCII art from version.txt file.
    
    Returns:
        ASCII art string
    """
    # Get path to version.txt (relative to this module)
    module_dir = Path(__file__).parent.parent
    version_file = module_dir / "version.txt"
    
    try:
        return version_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        # Fallback ASCII art
        return """`        d8b  .d888         
         Y8P d88P"          
             888            
 8888b.  888 888888 888d888 
    "88b 888 888    888P"   
.d888888 888 888    888     
888  888 888 888    888     
"Y888888 888 888    888"""


def print_version_banner(version: str) -> None:
    """
    Print version banner with gradient ASCII art.
    
    Args:
        version: Version string to display
    """
    ascii_art = load_version_ascii()
    print_gradient_ascii(ascii_art)
    
    # Print version number with matching color scheme
    version_color = RETRO_COLORS[2]  # Use coral color for version
    print(f"{rgb_to_ansi(*version_color)}v{version}{reset_color()}")
