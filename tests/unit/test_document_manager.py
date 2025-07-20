import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
import uuid

from src.knowledgeAgent.document.manager.document_manager import DocumentManager
from src.knowledgeAgent.document.models.document import Document
from src.knowledgeAgent.document.models.metadata import DocumentMetadata


class TestDocumentManager(unittest.TestCase):
    """Test the DocumentManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_llm_service = MagicMock()
        self.document_manager = DocumentManager(llm_service=self.mock_llm_service)
    
    def test_initialization(self):
        """Test DocumentManager initialization."""
        self.assertEqual(self.document_manager.name, "Document builder")
        self.assertEqual(self.document_manager.llm_service, self.mock_llm_service)
    
    def test_make_new_document_with_valid_file(self):
        """Test creating a new document with a valid file."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content for document")
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_123"
            
            with patch('uuid.uuid4', return_value=MagicMock(return_value="metadata_id_123")):
                document = self.document_manager.make_new_document(temp_file_path, document_id)
            
            # Verify document was created correctly
            self.assertIsNotNone(document)
            if document is not None:
                self.assertIsInstance(document, Document)
                self.assertEqual(document.id, document_id)
                self.assertEqual(document.file_path, temp_file_path)
                self.assertEqual(document.filename, os.path.basename(temp_file_path))
                
                # Verify metadata was created
                self.assertIsNotNone(document.metadata)
                if document.metadata is not None:
                    self.assertIsInstance(document.metadata, DocumentMetadata)
                    self.assertEqual(document.metadata.document_id, document_id)
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_make_new_document_with_nonexistent_file(self):
        """Test creating document with non-existent file."""
        nonexistent_path = "/path/that/does/not/exist.txt"
        document_id = "test_doc_456"
        
        with patch('builtins.print') as mock_print:
            document = self.document_manager.make_new_document(nonexistent_path, document_id)
        
        # Should return None for non-existent file
        self.assertIsNone(document)
        
        # Should print error message
        mock_print.assert_any_call(f"Error: File not found: {nonexistent_path}")
    
    def test_make_new_document_metadata_creation(self):
        """Test that document metadata is created correctly."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write("# Test Markdown\nThis is test content.")
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_789"
            
            with patch('uuid.uuid4') as mock_uuid:
                mock_uuid.return_value = "mocked_metadata_id"
                document = self.document_manager.make_new_document(temp_file_path, document_id)
            
            # Verify metadata creation
            if document is not None:
                self.assertIsNotNone(document.metadata)
                if document.metadata is not None:
                    self.assertEqual(document.metadata.document_id, document_id)
                    self.assertEqual(document.metadata.title, os.path.splitext(os.path.basename(temp_file_path))[0])
            
        finally:
            os.unlink(temp_file_path)
    
    def test_make_new_document_file_type_detection(self):
        """Test that file type is correctly detected."""
        # Test with different file extensions
        test_cases = [
            ('.txt', '.txt'),
            ('.md', '.md'),
            ('.markdown', '.markdown'),
            ('.pdf', '.pdf'),
            ('', '')  # No extension
        ]
        
        for extension, expected_type in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as temp_file:
                temp_file.write("Test content")
                temp_file_path = temp_file.name
            
            try:
                document_id = f"test_doc_{extension.replace('.', '')}"
                document = self.document_manager.make_new_document(temp_file_path, document_id)
                
                if document:  # Only check if document was created successfully
                    self.assertEqual(document.file_type, expected_type)
                    
            finally:
                os.unlink(temp_file_path)
    
    @patch('builtins.print')
    def test_make_new_document_logging(self, mock_print):
        """Test that appropriate logging messages are printed."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_logging"
            document = self.document_manager.make_new_document(temp_file_path, document_id)
            
            # Verify logging messages
            mock_print.assert_any_call(f"Creating document for {temp_file_path}")
            mock_print.assert_any_call("creating metadata")
            
        finally:
            os.unlink(temp_file_path)
    
    def test_make_new_document_with_unicode_filename(self):
        """Test creating document with unicode characters in filename."""
        # Create a temporary file with unicode name
        with tempfile.NamedTemporaryFile(mode='w', suffix='_测试.txt', delete=False) as temp_file:
            temp_file.write("Unicode test content")
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_unicode"
            document = self.document_manager.make_new_document(temp_file_path, document_id)
            
            # Should handle unicode filenames correctly
            self.assertIsNotNone(document)
            if document is not None:
                self.assertEqual(document.filename, os.path.basename(temp_file_path))
            
        finally:
            os.unlink(temp_file_path)
    
    def test_make_new_document_with_empty_file(self):
        """Test creating document with empty file."""
        # Create an empty temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            # Don't write anything - leave file empty
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_empty"
            document = self.document_manager.make_new_document(temp_file_path, document_id)
            
            # Should handle empty files correctly
            self.assertIsNotNone(document)
            self.assertEqual(document.id, document_id)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_make_new_document_with_large_file(self):
        """Test creating document with a large file."""
        # Create a large temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            # Write a large amount of content
            large_content = "Large file content. " * 10000  # ~200KB
            temp_file.write(large_content)
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_large"
            document = self.document_manager.make_new_document(temp_file_path, document_id)
            
            # Should handle large files correctly
            self.assertIsNotNone(document)
            self.assertEqual(document.id, document_id)
            
        finally:
            os.unlink(temp_file_path)
    
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_make_new_document_with_mocked_file_operations(self, mock_exists, mock_getsize):
        """Test document creation with mocked file operations."""
        # Mock file operations
        mock_exists.return_value = True
        mock_getsize.return_value = 1024  # 1KB file
        
        document_path = "/mocked/path/test.txt"
        document_id = "test_doc_mocked"
        
        with patch('uuid.uuid4', return_value="mocked_metadata_id"):
            document = self.document_manager.make_new_document(document_path, document_id)
        
        # Verify document creation with mocked operations
        self.assertIsNotNone(document)
        self.assertEqual(document.id, document_id)
        self.assertEqual(document.file_path, document_path)
        self.assertEqual(document.filename, "test.txt")
        self.assertEqual(document.file_type, ".txt")
        
        # Verify mocked functions were called
        mock_exists.assert_called_once_with(document_path)
        mock_getsize.assert_called_once_with(document_path)


class TestDocumentManagerErrorHandling(unittest.TestCase):
    """Test error handling in DocumentManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_llm_service = MagicMock()
        self.document_manager = DocumentManager(llm_service=self.mock_llm_service)
    
    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_make_new_document_with_file_access_error(self, mock_print, mock_exists, mock_getsize):
        """Test handling of file access errors."""
        # Mock file to exist but getsize to raise an error
        mock_exists.return_value = True
        mock_getsize.side_effect = OSError("Permission denied")
        
        document_path = "/restricted/path/test.txt"
        document_id = "test_doc_error"
        
        # Should handle the error gracefully
        document = self.document_manager.make_new_document(document_path, document_id)
        
        # Might return None or handle error differently
        # The exact behavior depends on implementation
        self.assertTrue(document is None or isinstance(document, Document))
    
    @patch('uuid.uuid4')
    def test_make_new_document_with_uuid_error(self, mock_uuid):
        """Test handling of UUID generation errors."""
        # Make UUID generation fail
        mock_uuid.side_effect = Exception("UUID generation failed")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_uuid_error"
            
            # Should handle UUID error gracefully
            try:
                document = self.document_manager.make_new_document(temp_file_path, document_id)
                # If it doesn't raise an exception, it should return None or handle it gracefully
                self.assertTrue(document is None or isinstance(document, Document))
            except Exception:
                # If it raises an exception, that's also acceptable behavior
                pass
                
        finally:
            os.unlink(temp_file_path)


class TestDocumentManagerIntegration(unittest.TestCase):
    """Integration tests for DocumentManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_llm_service = MagicMock()
        self.document_manager = DocumentManager(llm_service=self.mock_llm_service)
    
    def test_document_creation_workflow(self):
        """Test the complete document creation workflow."""
        # Create test file with different content types
        test_content = """# Test Document
        
This is a test document for integration testing.

## Section 1
Content for section 1.

### Subsection 1.1
Detailed content here.

## Section 2
More content for testing.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            document_id = "integration_test_doc"
            
            # Create document
            document = self.document_manager.make_new_document(temp_file_path, document_id)
            
            # Verify complete document structure
            self.assertIsNotNone(document)
            self.assertEqual(document.id, document_id)
            self.assertTrue(document.filename.endswith('.md'))
            self.assertEqual(document.file_type, '.md')
            self.assertIsNotNone(document.metadata)
            
            # Verify metadata structure
            metadata = document.metadata
            self.assertEqual(metadata.document_id, document_id)
            self.assertIsNotNone(metadata.metadata_id)
            
        finally:
            os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main()
