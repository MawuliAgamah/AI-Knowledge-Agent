"""
Script which handles everything related to processing to be embedded.
"""
# import os
# import sys
# import glob


from dataclasses import dataclass
from src.knowledgeAgent.document.models.metadata import DocumentMetadata
from src.knowledgeAgent.document.models.document import Document
from src.knowledgeAgent.document.preprocessing.chunker import Chunker
from src.knowledgeAgent.document.preprocessing.parser import ParserFactory

import uuid

class DocumentManager:
    """Construct Document Object"""
    def __init__(self):
        self.name = "Document builder"

    def make_new_document(self, document_path, document_id):
       import os
       """Create a new Document instance based on file information"""
       # Get file metadata
       print(f"Creating document for {document_path}")
       
       file_size = os.path.getsize(document_path)
       filename = os.path.basename(document_path)
    
       print("creating metadata")
       metadata = DocumentMetadata(
           title=os.path.splitext(filename)[0],
                        document_id=document_id,
                        metadata_id=str(uuid.uuid4()),
                        )
       
       # Create the Document instance
       document = Document(
           id=document_id,
           filename=filename,
           file_path=document_path,
           file_type=os.path.splitext(document_path)[1],
           file_size=file_size,
           title=os.path.splitext(filename)[0],  # Use filename without extension as title
           raw_content="",  # Will be filled during parsing
           clean_content="",  # Will be filled during cleaning
           metadata=metadata,  # Inline metadata creation
           textChunks=[]  # Will be filled during chunking
           )
       print("document initialized and loaded with contents")
       document = self._load_document_contents(document)
       return document


    def _load_document_contents(self, document):
        """Parse document content based on document type"""
        print(f"Parsing document {document.id} of type {document.file_type}")
        # Get appropriate parser for document type
        parser = ParserFactory.get_parser(document.file_type)
        # Parse document
        raw_content = parser.parse(document.file_path)
        # Update document with content
        document.raw_content = raw_content
        document.is_parsed = True
        return document
    
    def chunk_document(self, document):
        """Process document through chunking pipeline"""
        print(f"Chunking document {document.id}")
        
        # Create chunker with default strategy
        chunker = Chunker()
        
        # Execute chunking pipeline
        chunks = chunker.chunk(document)
        chunk_metadatas = chunker.create_chunk_metadata(document, chunks)
        text_chunks = chunker.add_chunks_to_document(document, chunks, chunk_metadatas)
        
        # Update document with chunks
        document.textChunks = text_chunks
        document.is_chunked = True
        
        print(f"Document chunking complete: {len(text_chunks)} chunks")
        return document

    def generate_document_level_metadata(self, document):
        pass
       














