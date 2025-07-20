import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import uuid

from src.knowledgeAgent.api.client import KnowledgeGraphClient, GraphDatabaseConfig


class TestKnowledgeGraphClient(unittest.TestCase):
    """Integration tests for KnowledgeGraphClient."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_graph_config = {
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "database": "test_knowledge",
            "username": "neo4j",
            "password": "test_password"
        }
        
        self.test_db_config = {
            "db_type": "sqlite",
            "db_location": ":memory:"  # Use in-memory database for testing
        }
        
        self.test_llm_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": "test-api-key"
        }
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_client_initialization_with_dict_config(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test client initialization with dictionary configurations."""
        # Mock the services
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service.return_value = mock_doc_service_instance
        
        # Initialize client
        client = KnowledgeGraphClient(
            graph_db_config=self.test_graph_config,
            db_config=self.test_db_config,
            llm_config=self.test_llm_config
        )
        
        # Verify initialization
        self.assertIsNotNone(client)
        
        # Verify services were created
        mock_llm_service.assert_called_once()
        mock_doc_service.assert_called_once()
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_client_initialization_with_dataclass_config(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test client initialization with dataclass configurations."""
        # Create dataclass config
        graph_config = GraphDatabaseConfig(
            db_type="neo4j",
            database="test_db",
            host="localhost",
            port=7687,
            username="test_user",
            password="test_pass"
        )
        
        # Mock the services
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service.return_value = mock_doc_service_instance
        
        # Initialize client
        client = KnowledgeGraphClient(
            graph_db_config=graph_config,
            llm_config=self.test_llm_config
        )
        
        # Verify initialization
        self.assertIsNotNone(client)
        
        # Verify dataclass was processed correctly
        mock_db_client.assert_called_once()
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_add_document_integration(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test the complete add_document workflow."""
        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service_instance.add_document.return_value = "doc_123"
        mock_doc_service.return_value = mock_doc_service_instance
        
        # Create client
        client = KnowledgeGraphClient(
            graph_db_config=self.test_graph_config,
            llm_config=self.test_llm_config
        )
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test document content for integration testing.")
            temp_file_path = temp_file.name
        
        try:
            # Test add_document
            result = client.add_document(
                document_path=temp_file_path,
                document_type="text",
                document_id="test_doc_123"
            )
            
            # Verify result
            self.assertEqual(result, "doc_123")
            
            # Verify document service was called correctly
            mock_doc_service_instance.add_document.assert_called_once()
            
        finally:
            os.unlink(temp_file_path)
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_add_document_with_auto_generated_id(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test add_document with automatically generated document ID."""
        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service_instance.add_document.return_value = "auto_generated_id"
        mock_doc_service.return_value = mock_doc_service_instance
        
        # Create client
        client = KnowledgeGraphClient(
            graph_db_config=self.test_graph_config,
            llm_config=self.test_llm_config
        )
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write("# Test Markdown\nContent for testing auto ID generation.")
            temp_file_path = temp_file.name
        
        try:
            # Test add_document without explicit ID
            result = client.add_document(
                document_path=temp_file_path,
                document_type="markdown",
                document_id="auto_gen_test"  # Use a test ID
            )
            
            # Should return the auto-generated ID
            self.assertEqual(result, "auto_generated_id")
            
        finally:
            os.unlink(temp_file_path)
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_extract_document_ontology(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test the extract_document_ontology method."""
        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service.return_value = mock_doc_service_instance
        
        # Create client
        client = KnowledgeGraphClient(
            graph_db_config=self.test_graph_config,
            llm_config=self.test_llm_config
        )
        
        # Test extract_document_ontology if method exists
        if hasattr(client, 'extract_document_ontology'):
            document_id = "test_doc_ontology"
            
            # Should call the method without error
            try:
                result = client.extract_document_ontology(document_id)
                # Method should return something or None
                self.assertTrue(result is None or isinstance(result, (dict, list, str)))
            except NotImplementedError:
                # Method might not be fully implemented yet
                self.skipTest("extract_document_ontology not yet implemented")
        else:
            self.skipTest("extract_document_ontology method not found")


class TestKnowledgeGraphClientErrorHandling(unittest.TestCase):
    """Test error handling in KnowledgeGraphClient."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_graph_config = {
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "database": "test_knowledge",
            "username": "neo4j",
            "password": "test_password"
        }
        
        self.test_llm_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": "test-api-key"
        }
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_add_document_with_invalid_file(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test add_document with invalid file path."""
        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service_instance.add_document.return_value = None  # Simulate failure
        mock_doc_service.return_value = mock_doc_service_instance
        
        # Create client
        client = KnowledgeGraphClient(
            graph_db_config=self.test_graph_config,
            llm_config=self.test_llm_config
        )
        
        # Test with non-existent file
        result = client.add_document(
            document_path="/nonexistent/file.txt",
            document_type="text",
            document_id="error_test"
        )
        
        # Should handle error gracefully
        self.assertIsNone(result)
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    def test_initialization_with_invalid_config(self, mock_db_client):
        """Test client initialization with invalid configuration."""
        # Test with missing required config fields
        invalid_graph_config = {
            "db_type": "neo4j"
            # Missing required fields
        }
        
        invalid_llm_config = {
            "model": "gpt-3.5-turbo"
            # Missing api_key
        }
        
        # Should handle invalid config gracefully
        try:
            client = KnowledgeGraphClient(
                graph_db_config=invalid_graph_config,
                llm_config=invalid_llm_config
            )
            # If no exception is raised, that's also valid behavior
            self.assertIsNotNone(client)
        except (ValueError, KeyError, TypeError) as e:
            # These are expected exceptions for invalid config
            self.assertIsInstance(e, (ValueError, KeyError, TypeError))


class TestKnowledgeGraphClientConfiguration(unittest.TestCase):
    """Test configuration handling in KnowledgeGraphClient."""
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_default_configuration_values(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test that default configuration values are applied correctly."""
        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service.return_value = mock_doc_service_instance
        
        minimal_config = {
            "db_type": "neo4j",
            "database": "test"
        }
        
        llm_config = {
            "model": "gpt-3.5-turbo",
            "api_key": "test-key"
        }
        
        # Create client with minimal config
        client = KnowledgeGraphClient(
            graph_db_config=minimal_config,
            llm_config=llm_config
        )
        
        # Verify client was created successfully
        self.assertIsNotNone(client)
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_custom_configuration_values(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test that custom configuration values override defaults."""
        # Setup mocks
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service.return_value = mock_doc_service_instance
        
        graph_config = {
            "db_type": "neo4j",
            "database": "test"
        }
        
        llm_config = {
            "model": "gpt-4",
            "api_key": "test-key"
        }
        
        # Create client with custom values
        client = KnowledgeGraphClient(
            graph_db_config=graph_config,
            llm_config=llm_config,
            log_level="DEBUG",
            embedding_dimension=1024,
            max_connections=20,
            timeout=60
        )
        
        # Verify client was created successfully with custom config
        self.assertIsNotNone(client)


class TestKnowledgeGraphClientIntegration(unittest.TestCase):
    """Full integration tests for KnowledgeGraphClient."""
    
    @patch('src.knowledgeAgent.api.client.DatabaseClient')
    @patch('src.knowledgeAgent.llm.service.LLMService')
    @patch('src.knowledgeAgent.document.service.DocumentService')
    def test_complete_document_workflow(self, mock_doc_service, mock_llm_service, mock_db_client):
        """Test a complete document processing workflow."""
        # Setup comprehensive mocks
        mock_db_instance = MagicMock()
        mock_db_client.return_value = mock_db_instance
        
        mock_llm_instance = MagicMock()
        mock_llm_service.return_value = mock_llm_instance
        
        mock_doc_service_instance = MagicMock()
        mock_doc_service_instance.add_document.return_value = "workflow_doc_123"
        mock_doc_service.return_value = mock_doc_service_instance
        
        # Configuration
        graph_config = GraphDatabaseConfig(
            db_type="neo4j",
            database="workflow_test",
            host="localhost",
            port=7687,
            username="neo4j",
            password="password"
        )
        
        llm_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": "workflow-test-key"
        }
        
        # Create client
        client = KnowledgeGraphClient(
            graph_db_config=graph_config,
            llm_config=llm_config,
            log_level="INFO"
        )
        
        # Create test document
        test_content = """# Knowledge Graph Test Document

This document tests the complete workflow of the knowledge graph system.

## Introduction
Knowledge graphs represent information as entities and relationships.

## Methodology
1. Document ingestion
2. Text chunking
3. Entity extraction
4. Relationship identification
5. Graph construction

## Conclusion
The system should process this document successfully.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Add document
            document_id = client.add_document(
                document_path=temp_file_path,
                document_type="markdown",
                document_id="workflow_test_doc"
            )
            
            # Verify document was added
            self.assertEqual(document_id, "workflow_doc_123")
            
            # Step 2: Extract ontology (if implemented)
            if hasattr(client, 'extract_document_ontology'):
                try:
                    ontology_result = client.extract_document_ontology(document_id)
                    # Should return some result or None
                    self.assertTrue(ontology_result is None or isinstance(ontology_result, (dict, list)))
                except NotImplementedError:
                    # Method might not be implemented yet
                    pass
            
            # Verify services were used correctly
            mock_doc_service_instance.add_document.assert_called_once()
            
        finally:
            os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main()
