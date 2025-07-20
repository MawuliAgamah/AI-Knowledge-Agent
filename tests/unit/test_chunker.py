import unittest
from unittest.mock import patch, MagicMock
import uuid

from src.knowledgeAgent.document.preprocessing.chunker import (
    MarkdownSection,
    StructuredMarkdownChunker,
    Chunker
)
from src.knowledgeAgent.document.models.chunk import TextChunk, ChunkMetadata


class TestMarkdownSection(unittest.TestCase):
    """Test the MarkdownSection class."""
    
    def setUp(self):
        self.section = MarkdownSection(level=1, title="Test Section", content="Test content")
    
    def test_initialization(self):
        """Test MarkdownSection initialization."""
        section = MarkdownSection(level=2, title="Header", content="Content")
        self.assertEqual(section.level, 2)
        self.assertEqual(section.title, "Header")
        self.assertEqual(section.content, "Content")
        self.assertEqual(section.subsections, [])
        self.assertIsNone(section.parent)
        self.assertEqual(section.start_index, 0)
        self.assertEqual(section.end_index, 0)
    
    def test_add_subsection(self):
        """Test adding subsections."""
        parent = MarkdownSection(level=1, title="Parent")
        child = MarkdownSection(level=2, title="Child")
        
        parent.add_subsection(child)
        
        self.assertEqual(len(parent.subsections), 1)
        self.assertEqual(parent.subsections[0], child)
        self.assertEqual(child.parent, parent)
    
    def test_full_content_with_headers(self):
        """Test full_content method with headers included."""
        section = MarkdownSection(level=2, title="Test Header", content="Content here\n")
        result = section.full_content(include_headers=True)
        expected = "## Test Header\n\nContent here\n"
        self.assertEqual(result, expected)
    
    def test_full_content_without_headers(self):
        """Test full_content method without headers."""
        section = MarkdownSection(level=2, title="Test Header", content="Content here\n")
        result = section.full_content(include_headers=False)
        self.assertEqual(result, "Content here\n")
    
    def test_full_content_with_subsections(self):
        """Test full_content method including subsections."""
        parent = MarkdownSection(level=1, title="Parent", content="Parent content\n")
        child1 = MarkdownSection(level=2, title="Child 1", content="Child 1 content\n")
        child2 = MarkdownSection(level=2, title="Child 2", content="Child 2 content\n")
        
        parent.add_subsection(child1)
        parent.add_subsection(child2)
        
        result = parent.full_content(include_headers=True)
        
        # Should include parent header and content, plus both children
        self.assertIn("# Parent", result)
        self.assertIn("Parent content", result)
        self.assertIn("## Child 1", result)
        self.assertIn("Child 1 content", result)
        self.assertIn("## Child 2", result)
        self.assertIn("Child 2 content", result)
    
    def test_size_calculation(self):
        """Test size calculation."""
        section = MarkdownSection(level=1, title="Test", content="Content")
        size = section.size()
        expected_size = len(section.full_content())
        self.assertEqual(size, expected_size)
    
    def test_get_full_path_single_section(self):
        """Test get_full_path for a single section."""
        section = MarkdownSection(level=1, title="Root")
        path = section.get_full_path()
        self.assertEqual(path, "Root")
    
    def test_get_full_path_nested_sections(self):
        """Test get_full_path for nested sections."""
        root = MarkdownSection(level=1, title="Root")
        child = MarkdownSection(level=2, title="Child")
        grandchild = MarkdownSection(level=3, title="Grandchild")
        
        root.add_subsection(child)
        child.add_subsection(grandchild)
        
        path = grandchild.get_full_path()
        self.assertEqual(path, "Root > Child > Grandchild")
    
    def test_empty_title_section(self):
        """Test section with empty title."""
        section = MarkdownSection(level=1, title="", content="Content only")
        content = section.full_content(include_headers=True)
        # Should not add header for empty title
        self.assertEqual(content, "Content only")


class TestStructuredMarkdownChunker(unittest.TestCase):
    """Test the StructuredMarkdownChunker class."""
    
    def setUp(self):
        self.chunker = StructuredMarkdownChunker(chunk_size=500, chunk_overlap=50)
    
    def test_initialization(self):
        """Test chunker initialization."""
        chunker = StructuredMarkdownChunker(chunk_size=1000, chunk_overlap=100)
        self.assertEqual(chunker.chunk_size, 1000)
        self.assertEqual(chunker.chunk_overlap, 100)
    
    def test_parse_document_simple(self):
        """Test parsing simple markdown structure."""
        markdown_text = """# Header 1
Content under header 1.

## Header 2
Content under header 2.

### Header 3
Content under header 3.
"""
        sections = self.chunker.parse_document(markdown_text)
        
        # Should have one root section with subsections
        self.assertEqual(len(sections), 1)
        root = sections[0]
        self.assertEqual(root.title, "Header 1")
        self.assertEqual(len(root.subsections), 1)
        
        level2 = root.subsections[0]
        self.assertEqual(level2.title, "Header 2")
        self.assertEqual(len(level2.subsections), 1)
        
        level3 = level2.subsections[0]
        self.assertEqual(level3.title, "Header 3")
    
    def test_parse_document_with_content_before_headers(self):
        """Test parsing markdown with content before any headers."""
        markdown_text = """This is introductory content.

# First Header
Content under first header.
"""
        sections = self.chunker.parse_document(markdown_text)
        
        # Should have content before first header
        self.assertTrue(len(sections) >= 1)
    
    def test_chunk_document_small_content(self):
        """Test chunking when content fits in one chunk."""
        document_mock = MagicMock()
        document_mock.raw_content = "# Small Header\nSmall content that fits in one chunk."
        document_mock.id = "test_doc"
        
        chunks = self.chunker.chunk_document(document_mock)
        
        self.assertEqual(len(chunks), 1)
        self.assertIsInstance(chunks[0], str)
    
    def test_chunk_document_large_content(self):
        """Test chunking when content needs to be split."""
        # Create content larger than chunk_size
        large_content = "# Large Content\n" + "This is a long line. " * 100
        
        document_mock = MagicMock()
        document_mock.raw_content = large_content
        document_mock.id = "test_doc"
        
        chunks = self.chunker.chunk_document(document_mock)
        
        # Should create multiple chunks
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertIsInstance(chunk, str)
    
    def test_chunk_content_structure(self):
        """Test that chunks maintain proper structure."""
        document_mock = MagicMock()
        document_mock.raw_content = "# Header\nContent here"
        document_mock.id = "test_doc"
        
        chunks = self.chunker.chunk_document(document_mock)
        
        # Should have at least one chunk
        self.assertGreater(len(chunks), 0)
        # Each chunk should be a string
        for chunk in chunks:
            self.assertIsInstance(chunk, str)
            self.assertTrue(len(chunk) > 0)


class TestChunker(unittest.TestCase):
    """Test the base Chunker class."""
    
    def setUp(self):
        self.chunker = Chunker(chunk_size=1000, chunk_overlap=100)
    
    def test_initialization(self):
        """Test Chunker initialization."""
        chunker = Chunker(chunk_size=500, chunk_overlap=50)
        self.assertEqual(chunker.chunk_size, 500)
        self.assertEqual(chunker.chunk_overlap, 50)
    
    def test_chunk_document_text_file(self):
        """Test chunking a text document."""
        document_mock = MagicMock()
        document_mock.file_type = ".txt"
        document_mock.raw_content = "This is plain text content that should be chunked."
        document_mock.id = "test_doc"
        
        chunks = self.chunker.chunk_document(document_mock)
        
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertIsInstance(chunk, str)
    
    def test_chunk_document_markdown_file(self):
        """Test chunking a markdown document."""
        document_mock = MagicMock()
        document_mock.file_type = ".md"
        document_mock.raw_content = """# Header
This is markdown content with headers.

## Subheader
More content here.
"""
        document_mock.id = "test_doc"
        
        chunks = self.chunker.chunk_document(document_mock)
        
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertIsInstance(chunk, str)
    
    def test_chunk_document_empty_content(self):
        """Test chunking document with empty content."""
        document_mock = MagicMock()
        document_mock.file_type = ".txt"
        document_mock.raw_content = ""
        document_mock.id = "test_doc"
        
        chunks = self.chunker.chunk_document(document_mock)
        
        # Should handle empty content gracefully
        self.assertIsInstance(chunks, list)


class TestChunkCreation(unittest.TestCase):
    """Test chunk creation and metadata."""
    
    def test_text_chunk_creation(self):
        """Test creating TextChunk objects."""
        chunk_id = str(uuid.uuid4())
        content = "Test chunk content"
        metadata = ChunkMetadata(
            start_index=0,
            end_index=100,
            section_title="Test Section"
        )
        
        chunk = TextChunk(
            id=chunk_id,
            document_id="doc123",
            content=content,
            metadata=metadata
        )
        
        self.assertEqual(chunk.id, chunk_id)
        self.assertEqual(chunk.content, content)
        self.assertEqual(chunk.document_id, "doc123")
        self.assertEqual(chunk.metadata.start_index, 0)
        self.assertEqual(chunk.metadata.end_index, 100)
        self.assertEqual(chunk.metadata.section_title, "Test Section")
    
    def test_chunk_metadata_creation(self):
        """Test creating ChunkMetadata objects."""
        metadata = ChunkMetadata(
            start_index=50,
            end_index=200,
            section_title="Introduction",
            section_depth=1,
            word_count=25
        )
        
        self.assertEqual(metadata.start_index, 50)
        self.assertEqual(metadata.end_index, 200)
        self.assertEqual(metadata.section_title, "Introduction")
        self.assertEqual(metadata.section_depth, 1)
        self.assertEqual(metadata.word_count, 25)


if __name__ == '__main__':
    unittest.main()
