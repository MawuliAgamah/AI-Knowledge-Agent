from typing import List, Dict, Optional, Tuple
from src.knowledgeAgent.document.models.chunk import TextChunk, ChunkMetadata
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class Chunker:
    """Handles document chunking with various strategies"""    
    def __init__(self, text_splitter=None):
        self.recursive_character_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    def chunk_document(self, document) -> List[str]:
        """Split document content into chunks using configured strategy"""
        print(f"Chunking document {document.id} using {self.recursive_character_text_splitter.__class__.__name__}")
        
        if not document.raw_content:
            print("Warning: Document has no content to chunk")
            return []
            
        # Split text and get raw content from Document objects
        doc_chunks = self.recursive_character_text_splitter.split_text(document.raw_content)
        chunks = [chunk.page_content if isinstance(chunk, Document) else chunk for chunk in doc_chunks]
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_chunk_metadata(self, document, chunks: List[str]) -> List[ChunkMetadata]:
        """Generate metadata for each chunk"""
        print("Creating metadata for chunks")
        
        chunk_metadatas = []
        current_position = 0
        
        for i, chunk_text in enumerate(chunks):
            # Calculate basic metrics
            word_count = len(chunk_text.split())
            
            # Find the chunk's position in the original document
            start_index = document.raw_content.find(chunk_text, current_position)
            if start_index == -1:  # If not found, try from beginning
                start_index = document.raw_content.find(chunk_text)
            end_index = start_index + len(chunk_text) if start_index != -1 else -1
            
            # Update current position for next search
            current_position = end_index if end_index != -1 else current_position

            # Create metadata
            metadata = ChunkMetadata(
                start_index=start_index,
                end_index=end_index,
                word_count=word_count,
                language=document.metadata.language if hasattr(document.metadata, 'language') else 'en'
            )
            chunk_metadatas.append(metadata)
    
        return chunk_metadatas
    
    
    def reconstruct_document(self, document, chunks: List[str], chunk_metadatas: List[ChunkMetadata]) -> List[TextChunk]:
        """Create TextChunk objects with metadata and navigation links"""
        text_chunks = []
        
        # Track indices for navigation
        for i, (chunk_text, metadata) in enumerate(zip(chunks, chunk_metadatas)):
            chunk_id = f"{document.id}_chunk_{i}"
            
            # Create previous/next links
            prev_id = f"{document.id}_chunk_{i-1}" if i > 0 else None
            next_id = f"{document.id}_chunk_{i+1}" if i < len(chunks) - 1 else None
            
            # Create chunk using metadata's indices
            chunk = TextChunk(
                id=chunk_id,
                document_id=document.id,
                content=chunk_text,
                metadata=metadata,
                previous_chunk_id=prev_id,
                next_chunk_id=next_id
            )
            text_chunks.append(chunk)
            
        print(f"Created {len(text_chunks)} text chunks")
        return text_chunks
    


