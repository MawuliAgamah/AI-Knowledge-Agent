from .models.document import Document, DocumentMetadata
from .models.chunk import TextChunk
from .preprocessing.processor import DocumentProcessor
from .cache.cache_manager import CacheManager



class DocumentService:
    """Service for document operations, used by the client"""


    def add_document(
            self,
            document_path: str,
            document_type: str,
            cache: bool = True,
    ):
        
        """
        Add a document to the system.
        """

        print(f"Adding document from {document_path} to the system...")