import unittest
import tempfile
import os
from unittest.mock import patch, mock_open

from src.knowledgeAgent.document.preprocessing.parser import (
    DocumentParser,
    DefaultParser,
    TextParser,
    MarkdownParser,
    ParserFactory
)


# Note: DocumentParser is an abstract class tested indirectly through its concrete implementations

class TestDefaultParser(unittest.TestCase):
    """Test the DefaultParser class."""
    
    def setUp(self):
        self.parser = DefaultParser()
    
    def test_parse_returns_empty_string(self):
        """Test that DefaultParser returns empty string for any file."""
        result = self.parser.parse("any_file.unknown")
        self.assertEqual(result, "")
    
    @patch('builtins.print')
    def test_parse_prints_message(self, mock_print):
        """Test that DefaultParser prints a message when parsing."""
        self.parser.parse("test_file.xyz")
        mock_print.assert_called_with("Using default parser for test_file.xyz")


class TestTextParser(unittest.TestCase):
    """Test the TextParser class."""
    
    def setUp(self):
        self.parser = TextParser()
    
    def test_parse_successful_file(self):
        """Test parsing a valid text file."""
        test_content = "This is a test file\nwith multiple lines."
        
        with patch("builtins.open", mock_open(read_data=test_content)):
            result = self.parser.parse("test.txt")
            self.assertEqual(result, test_content)
    
    @patch('builtins.print')
    def test_parse_prints_success_message(self, mock_print):
        """Test that successful parsing prints a message."""
        test_content = "Test content"
        
        with patch("builtins.open", mock_open(read_data=test_content)):
            self.parser.parse("test.txt")
            mock_print.assert_called_with(f"Text file parsed: {len(test_content)} chars")
    
    def test_parse_file_not_found(self):
        """Test parsing a non-existent file."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            result = self.parser.parse("nonexistent.txt")
            self.assertEqual(result, "")
    
    @patch('builtins.print')
    def test_parse_file_error_prints_message(self, mock_print):
        """Test that file errors print error messages."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            self.parser.parse("nonexistent.txt")
            mock_print.assert_called_with("Error parsing text file nonexistent.txt: File not found")
    
    def test_parse_encoding_error(self):
        """Test handling of encoding errors."""
        with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")):
            result = self.parser.parse("invalid_encoding.txt")
            self.assertEqual(result, "")
    
    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        with patch("builtins.open", mock_open(read_data="")):
            result = self.parser.parse("empty.txt")
            self.assertEqual(result, "")


class TestMarkdownParser(unittest.TestCase):
    """Test the MarkdownParser class."""
    
    def setUp(self):
        self.parser = MarkdownParser()
    
    def test_parse_markdown_file(self):
        """Test parsing a markdown file."""
        markdown_content = """# Header 1
This is content under header 1.

## Header 2
Content under header 2.

### Header 3
More content here.
"""
        
        with patch("builtins.open", mock_open(read_data=markdown_content)):
            result = self.parser.parse("test.md")
            self.assertEqual(result, markdown_content)
    
    def test_parse_empty_markdown(self):
        """Test parsing an empty markdown file."""
        with patch("builtins.open", mock_open(read_data="")):
            result = self.parser.parse("empty.md")
            self.assertEqual(result, "")
    
    def test_parse_markdown_with_special_characters(self):
        """Test parsing markdown with special characters."""
        markdown_content = """# Test with émojis 🚀
Content with **bold** and *italic* text.
`Code blocks` and [links](http://example.com).
"""
        
        with patch("builtins.open", mock_open(read_data=markdown_content)):
            result = self.parser.parse("special.md")
            self.assertEqual(result, markdown_content)


class TestParserFactory(unittest.TestCase):
    """Test the ParserFactory class."""
    
    def test_get_text_parser(self):
        """Test getting parser for text files."""
        parser = ParserFactory.get_parser(".txt")
        self.assertIsInstance(parser, TextParser)
    
    def test_get_markdown_parser(self):
        """Test getting parser for markdown files."""
        parser = ParserFactory.get_parser(".md")
        self.assertIsInstance(parser, MarkdownParser)
        
        parser = ParserFactory.get_parser(".markdown")
        self.assertIsInstance(parser, MarkdownParser)
    
    def test_get_default_parser_for_unknown_type(self):
        """Test getting default parser for unknown file types."""
        parser = ParserFactory.get_parser(".xyz")
        self.assertIsInstance(parser, DefaultParser)
        
        parser = ParserFactory.get_parser(".doc")
        self.assertIsInstance(parser, DefaultParser)
    
    def test_get_parser_case_insensitive(self):
        """Test that file extensions are handled case-insensitively."""
        parser = ParserFactory.get_parser(".TXT")
        self.assertIsInstance(parser, TextParser)
        
        parser = ParserFactory.get_parser(".MD")
        self.assertIsInstance(parser, MarkdownParser)
    
    def test_get_parser_without_dot(self):
        """Test getting parser for extensions without leading dot."""
        parser = ParserFactory.get_parser("txt")
        self.assertIsInstance(parser, TextParser)
        
        parser = ParserFactory.get_parser("md")
        self.assertIsInstance(parser, MarkdownParser)
    
    def test_get_parser_empty_extension(self):
        """Test getting parser for empty extension."""
        parser = ParserFactory.get_parser("")
        self.assertIsInstance(parser, DefaultParser)
        
        parser = ParserFactory.get_parser(".")
        self.assertIsInstance(parser, DefaultParser)


class TestIntegrationWithRealFiles(unittest.TestCase):
    """Integration tests with real temporary files."""
    
    def test_text_parser_with_real_file(self):
        """Test TextParser with an actual temporary file."""
        content = "Real file content\nLine 2\nLine 3"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            parser = TextParser()
            result = parser.parse(temp_path)
            self.assertEqual(result, content)
        finally:
            os.unlink(temp_path)
    
    def test_markdown_parser_with_real_file(self):
        """Test MarkdownParser with an actual temporary file."""
        content = """# Real Markdown Test
        
This is **real** markdown content.

## Subsection
- List item 1
- List item 2

```python
print("code block")
```
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            parser = MarkdownParser()
            result = parser.parse(temp_path)
            self.assertEqual(result, content)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
