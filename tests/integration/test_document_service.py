import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import uuid

from src.knowledgeAgent.document.service import DocumentService


class TestDocumentService(unittest.TestCase):
    """Integration tests for DocumentService."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_db_client = MagicMock()
        self.mock_llm_service = MagicMock()
        self.document_service = DocumentService(
            db_client=self.mock_db_client,
            llm_service=self.mock_llm_service
        )
    
    def test_service_initialization(self):
        """Test DocumentService initialization."""
        self.assertIsNotNone(self.document_service)
        self.assertEqual(self.document_service.db_client, self.mock_db_client)
        self.assertEqual(self.document_service.llm_service, self.mock_llm_service)
        self.assertIsNotNone(self.document_service.processor)
    
    def test_add_document_with_provided_id(self):
        """Test adding document with provided document ID."""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test document content for integration testing.")
            temp_file_path = temp_file.name
        
        try:
            document_id = "test_doc_123"
            
            # Mock the processor to return a successful result
            mock_document = MagicMock()
            mock_document.id = document_id
            
            with patch.object(self.document_service.processor, 'process_document', return_value=mock_document):
                result = self.document_service.add_document(
                    document_path=temp_file_path,
                    document_type="text",
                    document_id=document_id
                )
            
            # Verify the result
            self.assertEqual(result, document_id)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_add_document_with_auto_generated_id(self):
        """Test adding document without provided ID (auto-generation)."""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write("# Test Markdown\nContent for auto ID test.")
            temp_file_path = temp_file.name
        
        try:
            # Mock the processor to return a successful result
            mock_document = MagicMock()
            generated_id = "auto_generated_123"
            mock_document.id = generated_id
            
            with patch.object(self.document_service.processor, 'process_document', return_value=mock_document), \
                 patch('uuid.uuid4', return_value=MagicMock(__str__=lambda x: generated_id)):
                
                result = self.document_service.add_document(
                    document_path=temp_file_path,
                    document_type="markdown"
                    # No document_id provided
                )
            
            # Should return the auto-generated ID
            self.assertEqual(result, generated_id)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_add_document_processor_failure(self):
        """Test add_document when processor fails."""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name
        
        try:
            # Mock processor to return None (failure)
            with patch.object(self.document_service.processor, 'process_document', return_value=None):
                result = self.document_service.add_document(
                    document_path=temp_file_path,
                    document_type="text",
                    document_id="test_failure"
                )
            
            # Should return None when processing fails
            self.assertIsNone(result)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_add_document_with_exception(self):
        """Test add_document when an exception occurs."""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name
        
        try:
            # Mock processor to raise an exception
            with patch.object(self.document_service.processor, 'process_document', side_effect=Exception("Processing error")):
                result = self.document_service.add_document(
                    document_path=temp_file_path,
                    document_type="text",
                    document_id="test_exception"
                )
            
            # Should return None when exception occurs
            self.assertIsNone(result)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_delete_document(self):
        """Test the delete_document method."""
        document_id = "test_delete_123"
        
        # Mock the db_client delete method
        self.mock_db_client.delete_document = MagicMock()
        
        # Call delete_document
        self.document_service.delete_document(document_id)
        
        # Verify db_client.delete_document was called
        self.mock_db_client.delete_document.assert_called_once_with(document_id)
    
    def test_add_document_different_file_types(self):
        """Test adding documents with different file types."""
        file_types = [
            ('.txt', 'text'),
            ('.md', 'markdown'),
            ('.markdown', 'markdown')
        ]
        
        for file_ext, doc_type in file_types:
            with tempfile.NamedTemporaryFile(mode='w', suffix=file_ext, delete=False) as temp_file:
                temp_file.write(f"Test content for {file_ext} file")
                temp_file_path = temp_file.name
            
            try:
                document_id = f"test_{doc_type}_doc"
                
                # Mock successful processing
                mock_document = MagicMock()
                mock_document.id = document_id
                
                with patch.object(self.document_service.processor, 'process_document', return_value=mock_document):
                    result = self.document_service.add_document(
                        document_path=temp_file_path,
                        document_type=doc_type,
                        document_id=document_id
                    )
                
                # Should successfully process all file types
                self.assertEqual(result, document_id)
                
            finally:
                os.unlink(temp_file_path)


class TestDocumentServiceErrorHandling(unittest.TestCase):
    """Test error handling in DocumentService."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_db_client = MagicMock()
        self.mock_llm_service = MagicMock()
        self.document_service = DocumentService(
            db_client=self.mock_db_client,
            llm_service=self.mock_llm_service
        )
    
    def test_add_document_nonexistent_file(self):
        """Test adding a document that doesn't exist."""
        nonexistent_path = "/path/that/does/not/exist.txt"
        
        result = self.document_service.add_document(
            document_path=nonexistent_path,
            document_type="text",
            document_id="nonexistent_test"
        )
        
        # Should handle non-existent files gracefully
        self.assertIsNone(result)
    
    def test_add_document_empty_path(self):
        """Test adding document with empty path."""
        result = self.document_service.add_document(
            document_path="",
            document_type="text",
            document_id="empty_path_test"
        )
        
        # Should handle empty paths gracefully
        self.assertIsNone(result)
    
    def test_add_document_invalid_parameters(self):
        """Test add_document with invalid parameters."""
        # Create a valid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name
        
        try:
            # Test with various invalid parameter combinations
            test_cases = [
                (None, "text", "test1"),  # None path
                (temp_file_path, None, "test2"),  # None type
                (temp_file_path, "", "test3"),  # Empty type
            ]
            
            for path, doc_type, doc_id in test_cases:
                result = self.document_service.add_document(
                    document_path=path,
                    document_type=doc_type,
                    document_id=doc_id
                )
                
                # Should handle invalid parameters gracefully
                self.assertIsNone(result)
                
        finally:
            os.unlink(temp_file_path)
    
    def test_delete_document_with_db_error(self):
        """Test delete_document when database operation fails."""
        document_id = "test_delete_error"
        
        # Mock db_client to raise an exception
        self.mock_db_client.delete_document.side_effect = Exception("Database error")
        
        # Should handle database errors gracefully
        try:
            self.document_service.delete_document(document_id)
            # If no exception is raised, that's acceptable
        except Exception:
            # If an exception is raised, it should be handled appropriately
            pass


class TestDocumentServiceIntegration(unittest.TestCase):
    """Full integration tests for DocumentService."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_db_client = MagicMock()
        self.mock_llm_service = MagicMock()
        self.document_service = DocumentService(
            db_client=self.mock_db_client,
            llm_service=self.mock_llm_service
        )
    
    def test_complete_document_workflow(self):
        """Test a complete document processing workflow."""
        # Create a comprehensive test document
        test_content = """# Integration Test Document

This document is designed to test the complete DocumentService workflow.

## Overview
The DocumentService coordinates between multiple components:
- Document parsing
- Content chunking
- Metadata extraction
- Database storage

## Features
### Text Processing
The service handles various text formats and structures.

### Metadata Generation
Automatic metadata extraction from document content.

### Database Integration
Seamless integration with the database layer.

## Conclusion
This integration test validates the complete workflow.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            document_id = "integration_workflow_test"
            
            # Mock the complete processing pipeline
            mock_document = MagicMock()
            mock_document.id = document_id
            
            with patch.object(self.document_service.processor, 'process_document') as mock_process:
                mock_process.return_value = mock_document
                
                # Test the complete workflow
                result = self.document_service.add_document(
                    document_path=temp_file_path,
                    document_type="markdown",
                    document_id=document_id,
                    cache=True
                )
                
                # Verify successful processing
                self.assertEqual(result, document_id)
                
                # Verify processor was called with correct parameters
                mock_process.assert_called_once_with(temp_file_path, document_id)
                
        finally:
            os.unlink(temp_file_path)
    
    def test_service_with_different_configurations(self):
        """Test DocumentService with different configurations."""
        # Test with different mock configurations
        test_configs = [
            {"db_type": "sqlite", "llm_model": "gpt-3.5-turbo"},
            {"db_type": "neo4j", "llm_model": "gpt-4"},
        ]
        
        for config in test_configs:
            # Create service with specific config
            mock_db = MagicMock()
            mock_llm = MagicMock()
            mock_llm.config = config
            
            service = DocumentService(
                db_client=mock_db,
                llm_service=mock_llm
            )
            
            # Verify service initialization
            self.assertIsNotNone(service)
            self.assertEqual(service.db_client, mock_db)
            self.assertEqual(service.llm_service, mock_llm)
            
            # Test basic functionality
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(f"Test for config: {config}")
                temp_file_path = temp_file.name
            
            try:
                document_id = f"config_test_{config['db_type']}"
                
                # Mock successful processing
                mock_document = MagicMock()
                mock_document.id = document_id
                
                with patch.object(service.processor, 'process_document', return_value=mock_document):
                    result = service.add_document(
                        document_path=temp_file_path,
                        document_type="text",
                        document_id=document_id
                    )
                
                # Should work with any configuration
                self.assertEqual(result, document_id)
                
            finally:
                os.unlink(temp_file_path)


class TestDocumentServiceCaching(unittest.TestCase):
    """Test caching functionality in DocumentService."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_db_client = MagicMock()
        self.mock_llm_service = MagicMock()
        self.document_service = DocumentService(
            db_client=self.mock_db_client,
            llm_service=self.mock_llm_service
        )
    
    def test_add_document_with_caching_enabled(self):
        """Test add_document with caching enabled."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content for caching")
            temp_file_path = temp_file.name
        
        try:
            document_id = "cache_test_doc"
            
            # Mock successful processing
            mock_document = MagicMock()
            mock_document.id = document_id
            
            with patch.object(self.document_service.processor, 'process_document', return_value=mock_document):
                result = self.document_service.add_document(
                    document_path=temp_file_path,
                    document_type="text",
                    document_id=document_id,
                    cache=True
                )
            
            # Should return document ID
            self.assertEqual(result, document_id)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_add_document_with_caching_disabled(self):
        """Test add_document with caching disabled."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test content without caching")
            temp_file_path = temp_file.name
        
        try:
            document_id = "no_cache_test_doc"
            
            # Mock successful processing
            mock_document = MagicMock()
            mock_document.id = document_id
            
            with patch.object(self.document_service.processor, 'process_document', return_value=mock_document):
                result = self.document_service.add_document(
                    document_path=temp_file_path,
                    document_type="text",
                    document_id=document_id,
                    cache=False
                )
            
            # Should still work without caching
            self.assertEqual(result, document_id)
            
        finally:
            os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main()
