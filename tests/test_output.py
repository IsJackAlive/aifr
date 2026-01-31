import sys
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from aifr.output import should_colorize, print_chunks

class TestOutput(unittest.TestCase):
    def test_should_colorize_tty_no_raw(self):
        """Should return True if TTY and not raw."""
        with patch("sys.stdout.isatty", return_value=True):
            self.assertTrue(should_colorize(raw_flag=False))

    def test_should_colorize_tty_raw(self):
        """Should return False if TTY but raw flag is True."""
        with patch("sys.stdout.isatty", return_value=True):
            self.assertFalse(should_colorize(raw_flag=True))

    def test_should_colorize_no_tty(self):
        """Should return False if not TTY."""
        with patch("sys.stdout.isatty", return_value=False):
            self.assertFalse(should_colorize(raw_flag=False))

    @patch("aifr.output.render_markdown")
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_chunks_raw(self, mock_stdout, mock_render):
        """Verify raw output skips markdown rendering."""
        # Setup: return 'Rendered' if called, but we expect it NOT to be called or ignored
        mock_render.return_value = "Rendered"
        
        with patch("sys.stdout.isatty", return_value=True):
            # enforce raw via flag
            print_chunks("Original", raw_flag=True)
            
        output = mock_stdout.getvalue()
        self.assertIn("Original", output)
        self.assertNotIn("Rendered", output)
        # Verify render_markdown was NOT called (optimization) or at least output is raw
        # Current implementation: checks should_colorize at start.
        mock_render.assert_not_called()

if __name__ == "__main__":
    unittest.main()
