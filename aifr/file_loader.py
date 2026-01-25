from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .config import MAX_FILE_BYTES, SUPPORTED_EXTENSIONS

# Security: Blacklist of sensitive files that should not be loaded
SENSITIVE_FILE_PATTERNS = {
    '.env',
    '.env.local',
    '.env.production',
    '.env.development',
    'id_rsa',
    'id_dsa',
    'id_ecdsa',
    'id_ed25519',
    '.pem',
    '.key',
    '.pfx',
    '.p12',
    'credentials',
    'secrets',
    '.password',
    '.vault'
}


class UnsupportedFileError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


class SensitiveFileError(Exception):
    pass


def is_sensitive_file(path: Path) -> bool:
    """Check if file matches sensitive file patterns."""
    filename_lower = path.name.lower()
    
    # Check exact matches and patterns
    for pattern in SENSITIVE_FILE_PATTERNS:
        if pattern in filename_lower:
            return True
    
    # Check if in .ssh directory
    if '.ssh' in [p.name for p in path.parents]:
        return True
    
    return False


def load_file(path_str: str) -> Tuple[str, Path]:
    path = Path(path_str).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {path_str}")
    
    # Security check
    if is_sensitive_file(path):
        raise SensitiveFileError(
            f"Plik {path.name} wygląda na wrażliwy (klucze, hasła, .env). "
            f"Jeśli na pewno chcesz go użyć, zmień nazwę pliku."
        )
    
    if path.stat().st_size > MAX_FILE_BYTES:
        raise FileTooLargeError(f"Plik {path.name} przekracza limit 5MB")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileError(f"Nieobsługiwany format: {path.suffix}")
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-8", errors="ignore")
    return content, path
