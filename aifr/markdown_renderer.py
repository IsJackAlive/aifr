"""Retro-styled markdown renderer for LLM output."""
from __future__ import annotations

import re
from typing import Optional


# Retro color palette (RGB hex values) - same as gradient_display
RETRO_COLORS = {
    'cyan': (0x68, 0xc7, 0xc1),      # Headers
    'yellow': (0xfa, 0xca, 0x78),    # Bold, links
    'coral': (0xf5, 0x7f, 0x5b),     # Code inline
    'red': (0xdd, 0x53, 0x41),       # Important/emphasis
    'brown': (0x79, 0x4a, 0x3a),     # Code blocks
}


def rgb_to_ansi(r: int, g: int, b: int) -> str:
    """Convert RGB to ANSI escape code for 24-bit color."""
    return f"\033[38;2;{r};{g};{b}m"


def rgb_to_ansi_bg(r: int, g: int, b: int) -> str:
    """Convert RGB to ANSI escape code for background color."""
    return f"\033[48;2;{r};{g};{b}m"


def reset_color() -> str:
    """Return ANSI reset code."""
    return "\033[0m"


def bold() -> str:
    """Return ANSI bold code."""
    return "\033[1m"


def italic() -> str:
    """Return ANSI italic code."""
    return "\033[3m"


def dim() -> str:
    """Return ANSI dim code."""
    return "\033[2m"


class MarkdownRenderer:
    """Render markdown with retro color scheme."""
    
    def __init__(self) -> None:
        self.in_code_block = False
        self.code_block_lang: Optional[str] = None
    
    def render(self, text: str) -> str:
        """
        Render markdown text with retro colors.
        
        Args:
            text: Markdown text to render
        
        Returns:
            Colored text with ANSI codes
        """
        lines = text.split('\n')
        rendered_lines = []
        
        for line in lines:
            rendered_line = self._render_line(line)
            rendered_lines.append(rendered_line)
        
        return '\n'.join(rendered_lines)
    
    def _render_line(self, line: str) -> str:
        """Render a single line of markdown."""
        # Code block detection
        if line.strip().startswith('```'):
            self.in_code_block = not self.in_code_block
            if self.in_code_block:
                self.code_block_lang = line.strip()[3:].strip() or None
                # Return styled code block marker
                brown = rgb_to_ansi(*RETRO_COLORS['brown'])
                return f"{dim()}{brown}┌─ {self.code_block_lang or 'code'} {reset_color()}"
            else:
                self.code_block_lang = None
                brown = rgb_to_ansi(*RETRO_COLORS['brown'])
                return f"{dim()}{brown}└─────{reset_color()}"
        
        # Inside code block
        if self.in_code_block:
            coral = rgb_to_ansi(*RETRO_COLORS['coral'])
            return f"{coral}{line}{reset_color()}"
        
        # Headers
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2)
            cyan = rgb_to_ansi(*RETRO_COLORS['cyan'])
            return f"{bold()}{cyan}{'#' * level} {text}{reset_color()}"
        
        # Apply inline formatting
        line = self._render_inline(line)
        
        return line
    
    def _render_inline(self, text: str) -> str:
        """Render inline markdown elements."""
        # Process in order: code first (to avoid conflicts with * in code),
        # then bold, then italic
        
        # Inline code - needs to escape special ANSI characters
        def replace_code(m: re.Match[str]) -> str:
            code = m.group(1)
            coral = rgb_to_ansi(*RETRO_COLORS['coral'])
            return f"{coral}`{code}`{reset_color()}"
        text = re.sub(r'`([^`]+)`', replace_code, text)
        
        # Bold (must use non-greedy match and check for **)
        def replace_bold(m: re.Match[str]) -> str:
            content = m.group(1)
            yellow = rgb_to_ansi(*RETRO_COLORS['yellow'])
            return f"{bold()}{yellow}{content}{reset_color()}"
        text = re.sub(r'\*\*(.+?)\*\*', replace_bold, text)
        
        # Italic/Emphasis (must come after bold to avoid conflicts)
        # Must not match ** pairs
        def replace_italic(m: re.Match[str]) -> str:
            content = m.group(1)
            red = rgb_to_ansi(*RETRO_COLORS['red'])
            return f"{italic()}{red}{content}{reset_color()}"
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', replace_italic, text)
        
        # Links [text](url)
        def replace_link(m: re.Match[str]) -> str:
            link_text = m.group(1)
            url = m.group(2)
            yellow = rgb_to_ansi(*RETRO_COLORS['yellow'])
            return f"{yellow}{link_text}{reset_color()}{dim()} ({url}){reset_color()}"
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, text)
        
        # Bullet points
        def replace_bullet(m: re.Match[str]) -> str:
            spaces = m.group(1)
            cyan = rgb_to_ansi(*RETRO_COLORS['cyan'])
            return f"{spaces}{cyan}• {reset_color()}"
        text = re.sub(r'^(\s*)[•\-\*]\s+', replace_bullet, text)
        
        return text


def render_markdown(text: str) -> str:
    """
    Render markdown text with retro colors.
    
    Args:
        text: Markdown text to render
    
    Returns:
        Colored text with ANSI codes
    """
    renderer = MarkdownRenderer()
    return renderer.render(text)
