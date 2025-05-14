from typing import Dict, Optional, Union, List, Any
import logging
from dataclasses import dataclass

@dataclass
class GraphDatabaseConfig:
    db_type: str
    database: str
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    schema: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    ssl_mode: Optional[str] = None
    application_name: Optional[str] = "KnowledgeAgent"

@dataclass
class AuthCredentials:
    username: str
    password: str
    auth_type: str = "basic"
    token: Optional[str] = None
    
class KnowledgeGraphClient:
    """
    Main client interface for interacting with Knowledge Graphs.
    Handles document processing, entity extraction, and graph operations.
    """
    
    def __init__(
        self,
        graph_db_config: Union[Dict, GraphDatabaseConfig],
        auth_credentials: Optional[Union[Dict, AuthCredentials]] = None,
        log_level: str = "INFO",
        cache_config: Optional[Union[Dict, str]] = None,
        models: Optional[Dict[str, str]] = None,
        embedding_dimension: int = 768,
        max_connections: int = 10,
        timeout: int = 30
    ):
        """
        Initialize the Knowledge Graph Client.
        
        Args:
            db_config: Database configuration object or dictionary
            auth_credentials: Authentication credentials or dictionary (optional)
            log_level: Logging level (default: INFO)
            cache_config: Cache configuration dictionary or path string (default: None)
            models: Dictionary of AI model names to use
            embedding_dimension: Dimension for vector embeddings
            max_connections: Maximum number of concurrent connections
            timeout: Connection timeout in seconds
        """
        # Convert dictionary configs to objects if needed
        self.db_config = graph_db_config if isinstance(graph_db_config, GraphDatabaseConfig) else GraphDatabaseConfig(**graph_db_config)
        
        if auth_credentials:
            self.auth = auth_credentials if isinstance(auth_credentials, AuthCredentials) else AuthCredentials(**auth_credentials)
        else:
            # Use credentials from db_config if available
            if self.db_config.username and self.db_config.password:
                self.auth = AuthCredentials(
                    username=self.db_config.username,
                    password=self.db_config.password
                )
            else:
                self.auth = None
        
        # Set up logging
        self._configure_logging(log_level)
        
        # Initialize configuration
        self.cache_config = cache_config
        self.cache_dir = self._setup_cache_directory(cache_config)
        self.models = models or self._get_default_models()
        self.embedding_dimension = embedding_dimension
        self.max_connections = max_connections
        self.timeout = timeout
        
        # Initialize services (these would be separate classes)
        self._initialize_database_connection()
        self._initialize_services()
        
        self.logger.info("KnowledgeGraphClient initialized successfully")
    
    def _configure_logging(self, log_level: str) -> None:
        """Configure logging for the client."""
        self.logger = logging.getLogger("knowledgeAgent")
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        # Add handlers, formatters, etc.
    
    def _setup_cache_directory(self, cache_config: Optional[Union[Dict, str]]) -> str:
        """Set up and validate the cache directory."""
        import os
        import tempfile
        
        # If cache_config is a string, use it as directory path
        if isinstance(cache_config, str):
            if os.path.exists(cache_config):
                return cache_config
            else:
                try:
                    os.makedirs(cache_config, exist_ok=True)
                    return cache_config
                except Exception as e:
                    self.logger.warning(f"Failed to create cache directory {cache_config}: {e}")
                    
        # If cache_config is a dict, extract location
        elif isinstance(cache_config, dict) and "cache_location" in cache_config:
            location = cache_config["cache_location"]
            if os.path.exists(os.path.dirname(location)):
                return os.path.dirname(location)
        
        # Default to system temp directory
        default_dir = os.path.join(tempfile.gettempdir(), "knowledgeAgent_cache")
        os.makedirs(default_dir, exist_ok=True)
        self.logger.info(f"Using default cache directory: {default_dir}")
        return default_dir
    
    def _get_default_models(self) -> Dict[str, str]:
        """Get default AI models configuration."""
        return {
            "embedding": "sentence-transformers/all-MiniLM-L6-v2",
            "entity_extraction": "spacy/en_core_web_lg",
            "relation_extraction": "default-relation-model"
        }
    
    def _initialize_database_connection(self) -> None:
        """Establish connection to the database."""
        self.logger.debug(f"Connecting to {self.db_config.db_type} database")
        # Implementation for database connection
        # Create appropriate adapter based on db_type
        # Verify schema, create tables if needed
    
    def _initialize_services(self) -> None:
        """Initialize all required services."""
        from src.knowledgeAgent.document.service import DocumentService
        
        # Convert cache_config to format expected by DocumentService
        if isinstance(self.cache_config, str):
            doc_cache_config = {"enabled": True, "location": self.cache_dir}
        elif isinstance(self.cache_config, dict):
            doc_cache_config = self.cache_config
            if "enabled" not in doc_cache_config:
                doc_cache_config["enabled"] = True
        else:
            doc_cache_config = {"enabled": True, "location": self.cache_dir}
            
        self.document_service = DocumentService(cache_config=doc_cache_config)
    
    # Document Operations
    def add_document(self, document_path: str,document_id: str,document_type: Optional[str] = None) -> str:
        """
        Add a document to the knowledge graph.
        
        Args:
            document_path: Path to the document file
            document_type: Type of document (optional, will be inferred if not provided)
            
        Returns:
            document_id: Unique ID for the added document
        """
        self.logger.info(f"Adding document: {document_path}")
        
        # Infer document type if not provided
        if document_type is None:
            # Simple inference based on file extension
            import os
            ext = os.path.splitext(document_path)[1].lower()
            if ext == '.pdf':
                document_type = 'pdf'
            elif ext in ['.doc', '.docx']:
                document_type = 'docx'
            elif ext in ['.md', '.markdown']:
                document_type = 'markdown'
            elif ext in ['.txt']:
                document_type = 'text'
            else:
                document_type = 'unknown'
            
            self.logger.info(f"Inferred document_type: {document_type}")
        
        # If document_id is None, generate a fallback ID
        if document_id is None:
            import hashlib
            import time
            fallback_id = hashlib.md5(f"{document_path}:{time.time()}".encode()).hexdigest()
            self.logger.warning(f"Document service returned None ID, using fallback: {fallback_id}")
            document_id = fallback_id
        
                # Use document service to process the document
        document_id = self.document_service.add_document(
            document_path=document_path,
            document_type=document_type,
            document_id=document_id,
            cache=True
        )
            
        self.logger.info(f"Document added with ID: {document_id}")
        return document_id
    
    def process_document(self, document_id: str) -> Dict[str, Any]:
        """
        Process a document to extract entities and relationships.
        
        Args:
            document_id: ID of the document to process
            
        Returns:
            processing_results: Dictionary with processing statistics
        """
        # Implementation
        return {"status": "not_implemented", "document_id": document_id}
    
    # Graph Operations
    def create_graph(self, name: str, description: Optional[str] = None) -> str:
        """
        Create a new knowledge graph.
        
        Args:
            name: Name for the new graph
            description: Optional description
            
        Returns:
            graph_id: Unique ID for the created graph
        """
        # Implementation
        return f"graph_{name}"
    
    # Query Operations
    def query(self, query_text: str, graph_id: Optional[str] = None) -> List[Dict]:
        """
        Query the knowledge graph using natural language.
        
        Args:
            query_text: Natural language query
            graph_id: Optional graph ID (if not provided, uses default)
            
        Returns:
            results: List of matching results
        """
        # Implementation
        return [{"result": "not_implemented"}]
    
    # Connection Management
    def close(self) -> None:
        """Close all connections and free resources."""
        # Implementation to clean up connections
        self.logger.info("KnowledgeGraphClient closed")


if __name__ == "__main__":

    client = KnowledgeGraphClient(
        graph_db_config={
            "db_type": "neo4j",
            "host": "localhost",
            "port": 7687,
            "database": "knowledge",
            "username": "neo4j",
            "password": "password"
        },
        cache_config={
            "cache_type": "sqlite",
            "cache_location": "/Users/mawuliagamah/utilities/obsidian/server/obsidian/obsidian_cache.db"
        }
    )


    client.add_document(
            document_path="/Users/mawuliagamah/obsidian vaults/Software Company/3. BookShelf/Books/Psychocybernetics Principles for Creative Living/Psycho-Cybernetics.md",
            document_type="markdown",
            document_id="1234567890"
            )
    


    # document.display()
    client.close()

