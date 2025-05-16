from src.knowledgeAgent.document.preprocessing.parser import _get_parser_for_type
from src.knowledgeAgent.document.manager.document_manager import DocumentManager
from src.knowledgeAgent.document.cache.sqllite import SqlLite
import logging

class DocumentProcessor:
    """Orchestrates the document processing pipeline, to save raw files to postgres db ready to load into vector db."""
    def __init__(self, db, llm_service):
        self.document_manager = DocumentManager(llm_service=llm_service)
        self.logger = logging.getLogger("knowledgeAgent.document")
    
        # Get database path from cache config
        db_path = None
        if isinstance(db, dict):
            db_path = db.get('cache_location') or db.get('location')
        elif hasattr(db, 'cache_location'):
            db_path = db.cache_location
        elif hasattr(db, 'db_path'):
            db_path = db.db_path
            
        if not db_path:
            self.logger.warning("No database path provided, using default")
            
        self.logger.info(f"Initializing database with path: {db_path}")
        self.db = SqlLite(db_path=db_path)

    def process_document(self, document_path, document_id):
        # Process new document
        self.logger.info(f"Processing new document: {document_path}")
        
        # Initialize document
        document = self._initialise_document(document_path, document_id)
        if document is None:
            self.logger.error("Failed to initialize document")
            return None
            
        # Process document through pipeline
        try:
            document = self._create_chunks(document)
            if document is None:
                self.logger.error("Failed to create chunks")
                return None
                
            document = self._create_metadata(document)
            if document is None:
                self.logger.error("Failed to create metadata")
                return None
                
            self._save_document(document)
            return document
            
        except Exception as e:
            self.logger.error(f"Error processing document: {e}")
            return None

    def _initialise_document(self, document_path, document_id):
        """Initialise the document object."""
        try:
            document = self.document_manager.make_new_document(document_path, document_id)
            if document is None:
                self.logger.error("Document manager returned None")
                return None
            self.logger.info(f"Document initialized with ID: {document.id}")
            return document
        except Exception as e:
            self.logger.error(f"Error initializing document: {e}")
            return None
    
    def _create_chunks(self, document):
        document = self.document_manager.chunk_document(document)
        document = self.document_manager.enrich_document_chunks(document)
        return document
    
    def _create_metadata(self, document):
        document = self.document_manager.generate_document_level_metadata(document)
        return document

    def _save_document(self, document):
        """Save document to SQLite"""
        try:
            if not self.db:
                self.logger.warning("Database not initialized, skipping save")
                return document
                
            self.db.save_document(document)
            document.is_cached = True
            self.logger.info(f"Document saved to database")
        except Exception as e:
            self.logger.error(f"Error saving to database: {e}")
        return document


