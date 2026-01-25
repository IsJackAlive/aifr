"""Tests for file_loader module."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from aifr.file_loader import (
    FileTooLargeError,
    SensitiveFileError,
    UnsupportedFileError,
    is_sensitive_file,
    load_file,
)


class TestIsSensitiveFile:
    """Tests for is_sensitive_file function."""

    def test_env_file_is_sensitive(self) -> None:
        """Test that .env files are detected as sensitive."""
        path = Path("/home/user/.env")
        assert is_sensitive_file(path) is True

    def test_env_local_is_sensitive(self) -> None:
        """Test that .env.local files are detected as sensitive."""
        path = Path("/home/user/.env.local")
        assert is_sensitive_file(path) is True

    def test_ssh_key_is_sensitive(self) -> None:
        """Test that SSH keys are detected as sensitive."""
        assert is_sensitive_file(Path("/home/user/id_rsa")) is True
        assert is_sensitive_file(Path("/home/user/id_ed25519")) is True

    def test_pem_key_is_sensitive(self) -> None:
        """Test that .pem files are detected as sensitive."""
        path = Path("/home/user/certificate.pem")
        assert is_sensitive_file(path) is True

    def test_ssh_directory_is_sensitive(self) -> None:
        """Test that files in .ssh directory are sensitive."""
        path = Path("/home/user/.ssh/config")
        assert is_sensitive_file(path) is True

    def test_regular_file_not_sensitive(self) -> None:
        """Test that regular files are not sensitive."""
        path = Path("/home/user/README.md")
        assert is_sensitive_file(path) is False

    def test_credentials_file_is_sensitive(self) -> None:
        """Test that credentials files are detected as sensitive."""
        path = Path("/home/user/credentials.txt")
        assert is_sensitive_file(path) is True

    def test_case_insensitive_detection(self) -> None:
        """Test that detection is case-insensitive."""
        path = Path("/home/user/ID_RSA")
        assert is_sensitive_file(path) is True


class TestLoadFile:
    """Tests for load_file function."""

    @patch("aifr.file_loader.Path")
    def test_file_not_found(self, mock_path_class: Mock) -> None:
        """Test loading non-existent file raises FileNotFoundError."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = False
        mock_path_class.return_value.expanduser.return_value = mock_path

        with pytest.raises(FileNotFoundError, match="Nie znaleziono pliku"):
            load_file("nonexistent.txt")

    @patch("aifr.file_loader.Path")
    def test_sensitive_file_rejected(self, mock_path_class: Mock) -> None:
        """Test loading sensitive file raises SensitiveFileError."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.name = ".env"
        mock_path.parents = []
        mock_path_class.return_value.expanduser.return_value = mock_path

        with pytest.raises(SensitiveFileError, match="wygląda na wrażliwy"):
            load_file(".env")

    @patch("aifr.file_loader.Path")
    def test_file_too_large(self, mock_path_class: Mock) -> None:
        """Test loading file exceeding size limit raises FileTooLargeError."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.name = "large.txt"
        mock_path.suffix = ".txt"
        mock_path.parents = []
        
        mock_stat = Mock()
        mock_stat.st_size = 10 * 1024 * 1024  # 10MB
        mock_path.stat.return_value = mock_stat
        
        mock_path_class.return_value.expanduser.return_value = mock_path

        with pytest.raises(FileTooLargeError, match="przekracza limit"):
            load_file("large.txt")

    @patch("aifr.file_loader.Path")
    def test_unsupported_extension(self, mock_path_class: Mock) -> None:
        """Test loading file with unsupported extension raises UnsupportedFileError."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.name = "file.pdf"
        mock_path.suffix = ".pdf"
        mock_path.parents = []
        
        mock_stat = Mock()
        mock_stat.st_size = 1024  # 1KB
        mock_path.stat.return_value = mock_stat
        
        mock_path_class.return_value.expanduser.return_value = mock_path

        with pytest.raises(UnsupportedFileError, match="Nieobsługiwany format"):
            load_file("file.pdf")

    @patch("aifr.file_loader.Path")
    def test_load_valid_file(self, mock_path_class: Mock) -> None:
        """Test loading valid file returns content and path."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.name = "test.txt"
        mock_path.suffix = ".txt"
        mock_path.parents = []
        
        mock_stat = Mock()
        mock_stat.st_size = 100
        mock_path.stat.return_value = mock_stat
        mock_path.read_text.return_value = "file content"
        
        mock_path_class.return_value.expanduser.return_value = mock_path

        content, path = load_file("test.txt")
        
        assert content == "file content"
        assert path == mock_path
        mock_path.read_text.assert_called_once_with(encoding="utf-8")

    @patch("aifr.file_loader.Path")
    def test_load_file_with_unicode_errors(self, mock_path_class: Mock) -> None:
        """Test loading file with unicode errors uses error handler."""
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.name = "test.txt"
        mock_path.suffix = ".txt"
        mock_path.parents = []
        
        mock_stat = Mock()
        mock_stat.st_size = 100
        mock_path.stat.return_value = mock_stat
        
        # First call raises UnicodeDecodeError, second succeeds
        mock_path.read_text.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
            "content with errors ignored",
        ]
        
        mock_path_class.return_value.expanduser.return_value = mock_path

        content, path = load_file("test.txt")
        
        assert content == "content with errors ignored"
        assert mock_path.read_text.call_count == 2
