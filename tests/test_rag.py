
import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
from pathlib import Path

# Import will fail until we implement the module, which is expected in TDD
# from aifr.rag import SmartChunker, RAGEngine, ContextCompressor

# Identifying placeholder for the module we are about to write
try:
    from aifr.rag import SmartChunker, RAGEngine, ContextCompressor
except ImportError:
    # Defining mocks/placeholders so tests can be reviewed before implementation exists
    # or so we can write the test file first.
    pass

class TestSmartChunker:
    """Tests for the SmartChunker."""

    def test_chunk_python_functions(self):
        """Test splitting Python code by function/class."""
        code = """
import os

def func_one():
    return 1

class MyClass:
    def method_a(self):
        pass

def func_two():
    print("hello")
"""
        chunker = SmartChunker()
        chunks = chunker.chunk(code, "test.py")
        
        # Expecting chunks for: imports/top-level, func_one, MyClass, func_two
        # or at least func_one, MyClass, func_two
        assert len(chunks) >= 3
        assert any("def func_one" in c.content for c in chunks)
        assert any("class MyClass" in c.content for c in chunks)
        assert any("def func_two" in c.content for c in chunks)

    def test_chunk_markdown_headers(self):
        """Test splitting Markdown by headers."""
        text = """
# Header 1
Content 1

## Header 2
Content 2
"""
        chunker = SmartChunker()
        chunks = chunker.chunk(text, "doc.md")
        
        # Expecting splitting roughly by headers
        assert len(chunks) >= 2
        assert any("Header 1" in c.content for c in chunks)
        assert any("Header 2" in c.content for c in chunks)

class TestRAGEngine:
    """Tests for the RAGEngine."""

    def test_tokenize(self):
        engine = RAGEngine()
        text = "Hello, World! This is a Test."
        tokens = engine._tokenize(text)
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "," not in tokens

    def test_score_bm25_simple(self):
        """Test that scoring ranks relevant documents higher."""
        engine = RAGEngine()
        
        query = "database connection"
        
        doc1 = "This function handles database connection strings."
        doc2 = "This file is about UI rendering and colors."
        
        score1 = engine._score(engine._tokenize(query), engine._tokenize(doc1))
        score2 = engine._score(engine._tokenize(query), engine._tokenize(doc2))
        
        assert score1 > score2

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.is_file")
    @patch("builtins.open", new_callable=mock_open)
    def test_index_files(self, mock_file, mock_is_file, mock_glob):
        """Test indexing files from directory."""
        engine = RAGEngine()
        
        # Setup mocks
        mock_glob.return_value = [Path("file1.py"), Path("file2.md")]
        mock_is_file.return_value = True
        
        # Setup file content
        file_map = {
            Path("file1.py"): "def connect_db(): pass",
            Path("file2.md"): "# Database Config\nInfo here."
        }
        
        def side_effect(file, *args, **kwargs):
            # Convert string path to Path object if needed
            p = Path(file) if isinstance(file, str) else file
            # Simple mock content
            content = file_map.get(p, "")
            m = mock_open(read_data=content).return_value
            return m
            
        mock_file.side_effect = side_effect
        
        engine.index_files(Path("."))
        
        # Check if index is populated
        assert len(engine.documents) > 0
        
        # Search
        results = engine.search("connect", k=1)
        assert len(results) == 1
        assert "connect_db" in results[0].content

class TestContextCompressor:
    """Tests for ContextCompressor."""
    
    def test_compress_python(self):
        code = """
def test():
    # This is a comment
    
    x = 1
    
    return x
"""
        compressor = ContextCompressor()
        minified = compressor.compress(code, "test.py")
        
        assert "# This is a comment" not in minified
        assert "x = 1" in minified
        assert "\n\n\n" not in minified  # Should reduce newlines
