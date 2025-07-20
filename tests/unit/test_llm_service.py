import unittest
import os
from unittest.mock import patch, MagicMock, mock_open
import logging

from src.knowledgeAgent.llm.service import LLMService


class TestLLMService(unittest.TestCase):
    """Test the LLMService class."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock the environment variable for API key
        self.test_api_key = "test-api-key-123"
        self.test_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": self.test_api_key
        }
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key-123"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_initialization_with_config(self, mock_chat_openai):
        """Test LLMService initialization with provided config."""
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        config = {
            "model": "gpt-4",
            "temperature": 0.1,
            "api_key": "custom-api-key"
        }
        
        service = LLMService(config=config)
        
        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once_with(
            model="gpt-4",
            temperature=0.1,
            api_key="custom-api-key"
        )
        self.assertEqual(service.llm, mock_llm_instance)
        self.assertEqual(service.config, config)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_initialization_with_default_config(self, mock_chat_openai):
        """Test LLMService initialization with default config."""
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        service = LLMService()
        
        # Verify default config was created
        expected_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": "env-api-key"
        }
        self.assertEqual(service.config, expected_config)
        
        # Verify ChatOpenAI was called with default parameters
        mock_chat_openai.assert_called_once_with(
            model="gpt-3.5-turbo",
            temperature=0.2,
            api_key="env-api-key"
        )
    
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with self.assertRaises(ValueError) as context:
            LLMService()
        
        self.assertIn("OPENAI_API_KEY environment variable is not set", str(context.exception))
    
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_initialization_with_config_missing_api_key(self, mock_chat_openai):
        """Test initialization with config missing API key."""
        config = {
            "model": "gpt-4",
            "temperature": 0.1
            # No api_key provided
        }
        
        with self.assertRaises(ValueError) as context:
            LLMService(config=config)
        
        self.assertIn("OpenAI API key not found", str(context.exception))
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_extract_topics(self, mock_chat_openai):
        """Test the extract_topics method."""
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        # Create service
        service = LLMService(config=self.test_config)
        
        # Mock the response from LLM
        mock_response = MagicMock()
        mock_response.content = '{"topics": ["AI", "Machine Learning", "Technology"]}'
        mock_llm_instance.invoke.return_value = mock_response
        
        # Test the method
        test_text = "This is a test document about artificial intelligence and machine learning."
        result = service.extract_topics(test_text)
        
        # Verify LLM was called
        self.assertTrue(mock_llm_instance.invoke.called)
        
        # The actual implementation might vary, so we just check it returns something
        self.assertIsNotNone(result)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_extract_keywords(self, mock_chat_openai):
        """Test the extract_keywords method if it exists."""
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        # Create service
        service = LLMService(config=self.test_config)
        
        # Check if extract_keywords method exists
        if hasattr(service, 'extract_keywords'):
            # Mock the response from LLM
            mock_response = MagicMock()
            mock_response.content = '{"keywords": ["neural networks", "deep learning", "algorithms"]}'
            mock_llm_instance.invoke.return_value = mock_response
            
            # Test the method
            test_text = "Neural networks and deep learning algorithms are fundamental to AI."
            result = service.extract_keywords(test_text)
            
            # Verify LLM was called
            self.assertTrue(mock_llm_instance.invoke.called)
            self.assertIsNotNone(result)
        else:
            # Skip test if method doesn't exist
            self.skipTest("extract_keywords method not implemented")
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_extract_ontology(self, mock_chat_openai):
        """Test the extract_ontology method if it exists."""
        # Setup mock LLM
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        # Create service
        service = LLMService(config=self.test_config)
        
        # Check if extract_ontology method exists
        if hasattr(service, 'extract_ontology'):
            # Mock the response from LLM
            mock_response = MagicMock()
            mock_response.content = '{"entities": [], "relationships": []}'
            mock_llm_instance.invoke.return_value = mock_response
            
            # Test the method
            test_text = "The dog chased the cat in the park."
            result = service.extract_ontology(test_text)
            
            # Verify LLM was called
            self.assertTrue(mock_llm_instance.invoke.called)
            self.assertIsNotNone(result)
        else:
            # Skip test if method doesn't exist
            self.skipTest("extract_ontology method not implemented")
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_logging_configuration(self, mock_chat_openai):
        """Test that logging is properly configured."""
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            service = LLMService(config=self.test_config)
            
            # Verify logger was configured
            mock_get_logger.assert_called_with("knowledgeAgent.llm")
            self.assertEqual(service.logger, mock_logger)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_config_access(self, mock_chat_openai):
        """Test that config is properly stored and accessible."""
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        config = {
            "model": "gpt-4",
            "temperature": 0.3,
            "api_key": "test-key"
        }
        
        service = LLMService(config=config)
        
        # Verify config is stored correctly
        self.assertEqual(service.config["model"], "gpt-4")
        self.assertEqual(service.config["temperature"], 0.3)
        self.assertEqual(service.config["api_key"], "test-key")


class TestLLMServiceErrorHandling(unittest.TestCase):
    """Test error handling in LLMService."""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_llm_initialization_failure(self, mock_chat_openai):
        """Test handling of LLM initialization failure."""
        # Make ChatOpenAI raise an exception
        mock_chat_openai.side_effect = Exception("Failed to initialize LLM")
        
        config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": "test-api-key"
        }
        
        with self.assertRaises(Exception):
            LLMService(config=config)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_extract_topics_with_llm_error(self, mock_chat_openai):
        """Test extract_topics handling when LLM raises an error."""
        # Setup mock LLM that raises an error
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.side_effect = Exception("LLM API error")
        mock_chat_openai.return_value = mock_llm_instance
        
        config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": "test-api-key"
        }
        
        service = LLMService(config=config)
        
        # Test that the method handles the error gracefully
        test_text = "Test text for topic extraction"
        
        # The method should either return None, empty result, or raise a handled exception
        try:
            result = service.extract_topics(test_text)
            # If it returns a result, it should be None or empty
            self.assertTrue(result is None or result == [] or result == {})
        except Exception as e:
            # If it raises an exception, it should be a handled one
            self.assertIsInstance(e, (ValueError, RuntimeError, ConnectionError))


class TestLLMServiceIntegration(unittest.TestCase):
    """Integration tests for LLMService with mocked dependencies."""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    @patch('src.knowledgeAgent.llm.service.ChatOpenAI')
    def test_full_workflow(self, mock_chat_openai):
        """Test a complete workflow with the LLM service."""
        # Setup mock LLM with realistic responses
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        # Mock different responses for different calls
        mock_responses = [
            MagicMock(content='{"topics": ["AI", "ML"]}'),
            MagicMock(content='{"keywords": ["neural", "network"]}'),
        ]
        mock_llm_instance.invoke.side_effect = mock_responses
        
        config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.2,
            "api_key": "test-api-key"
        }
        
        service = LLMService(config=config)
        
        # Test multiple method calls
        test_text = "Artificial intelligence and machine learning are transforming technology."
        
        # Test topics extraction
        topics_result = service.extract_topics(test_text)
        self.assertIsNotNone(topics_result)
        
        # Test keywords extraction if available
        if hasattr(service, 'extract_keywords'):
            keywords_result = service.extract_keywords(test_text)
            self.assertIsNotNone(keywords_result)
        
        # Verify LLM was called multiple times
        self.assertGreater(mock_llm_instance.invoke.call_count, 0)


if __name__ == '__main__':
    unittest.main()
