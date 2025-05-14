from typing import List, Dict, Optional, Tuple
from src.knowledgeAgent.document.models.chunk import TextChunk, ChunkMetadata
import uuid



class ChunkMetaDataExtractor:



    def 



class Chunker:
    """Handles document chunking with various strategies"""    
    def __init__(self, text_splitter=None):
        self.text_splitter = text_splitter or self._default_text_splitter()
        
    def _default_text_splitter(self):
        """Create a default text splitter based on paragraphs"""
        return lambda text: [p for p in text.split('\n\n') if p.strip()]
        
    def chunk(self, document) -> List[str]:
        """Split document content into chunks using configured strategy"""
        print(f"Chunking document {document.id} using {self.text_splitter.__class__.__name__}")
        
        if not document.raw_content:
            print("Warning: Document has no content to chunk")
            return []
            
        # Basic chunking based on the text_splitter
        chunks = self.text_splitter(document.raw_content)
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def create_chunk_metadata(self, document, chunks: List[str]) -> List[ChunkMetadata]:
        """Generate metadata for each chunk"""
        print("Creating metadata for chunks")
        
        chunk_metadatas = []
        for i, chunk_text in enumerate(chunks):
            # Calculate basic metrics
            word_count = len(chunk_text.split())
            
            # Create metadata
            metadata = ChunkMetadata(
                paragraph_index=i,
                paragraph_position=self._determine_position(i, len(chunks)),
                word_count=word_count,
                token_count=self._estimate_tokens(chunk_text),
                language=document.metadata.language if hasattr(document.metadata, 'language') else 'en'
            )
            chunk_metadatas.append(metadata)
            
        return chunk_metadatas
    
    def add_chunks_to_document(self, document, chunks: List[str], chunk_metadatas: List[ChunkMetadata]) -> List[TextChunk]:
        """Create TextChunk objects and add to document"""
        text_chunks = []
        
        # Track indices for navigation
        for i, (chunk_text, metadata) in enumerate(zip(chunks, chunk_metadatas)):
            chunk_id = f"{document.id}_chunk_{i}"
            
            # Create previous/next links
            prev_id = f"{document.id}_chunk_{i-1}" if i > 0 else None
            next_id = f"{document.id}_chunk_{i+1}" if i < len(chunks) - 1 else None
            
            # Determine chunk position in document
            start_idx = document.raw_content.find(chunk_text)
            end_idx = start_idx + len(chunk_text) if start_idx != -1 else -1
            
            # Create chunk
            chunk = TextChunk(
                id=chunk_id,
                document_id=document.id,
                content=chunk_text,
                metadata=metadata,
                start_index=start_idx,
                end_index=end_idx,
                previous_chunk_id=prev_id,
                next_chunk_id=next_id
            )
            text_chunks.append(chunk)
            
        print(f"Added {len(text_chunks)} chunks to document")
        return text_chunks
    
    def _determine_position(self, index: int, total: int) -> str:
        """Determine position of chunk in document (start, middle, end)"""
        if total <= 1:
            return "complete"
        elif index == 0:
            return "start"
        elif index == total - 1:
            return "end"
        else:
            return "middle"
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimate of token count (avg 4 chars per token)"""
        return len(text) // 4
