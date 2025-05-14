
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from .citation import Citation
from .chunk import TextChunk


@dataclass
class DocumentMetadata:
    """Contains all metadata about the document."""
    title: Optional[str] = None        # Document title
    authors: List[str] = field(default_factory=list)  # Author names
    created_date: Optional[datetime] = None  # Document creation date
    modified_date: Optional[datetime] = None  # Last modified date
    
    # Content metadata
    language: str = "en"               # Document language
    word_count: int = 0                # Word count

        
    # Custom metadata
    tags: List[str] = field(default_factory=list)     #User-assigned tags


@dataclass
class Document:
    """Core representation of a preprocessed document."""
    id: str                      # Unique identifier
    filename: str                # Original filename
    file_path: str               # Original file path
    file_type: str               # File format (PDF, DOCX, MD, etc.)
    file_size: int               # Size in bytes
    title: str
    
    # Content
    raw_content: str             # Original extracted text
    clean_content: str           # Normalized/cleaned text
    
    # Metadata
    metadata: DocumentMetadata   # Extracted metadata
    
    # Chunks placeholder - will be filled during preprocessing
    textChunks: List[TextChunk]
    
    # Processing information
    document_created_at: datetime = field(default_factory=datetime.now)
    preprocessed_at: Optional[datetime] = None
    
    # Storage information
    cache_location: Optional[str] = None
    is_cached: bool = False
    cache_created_at: Optional[datetime] = None
    cache_updated_at: Optional[datetime] = None
    is_preprocessed: bool = False
    is_chunked: bool = False
    is_metadata_generated: bool = False
    is_hash_generated: bool = False
    
    