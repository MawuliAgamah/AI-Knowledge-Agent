
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from .metadata import DocumentMetadata
from .citation import Citation
from .chunk import TextChunk

@dataclass
class Document:
    """Core representation of a preprocessed document."""
    id: str                      # Unique identifier
    filename: str                # Original filename
    file_path: str               # Original file path
    file_type: str               # File format (PDF, DOCX, MD, etc.)
    file_size: int               # Size in bytes
    
    # Content
    raw_content: str             # Original extracted text
    clean_content: str           # Normalized/cleaned text
    
    # Metadata
    metadata: DocumentMetadata   # Extracted metadata
    citations : Citation
    hash: str                    # Content hash for versioning
    
    # Chunks placeholder - will be filled during preprocessing
    chunks: List[TextChunk]
    
    # Processing information
    created_at: datetime = field(default_factory=datetime.now)
    preprocessed_at: Optional[datetime] = None
    last_processed_at: Optional[datetime] = None
    preprocessing_stats: Dict[str, Any] = field(default_factory=dict)
    
    # Storage information
    cache_location: Optional[str] = None