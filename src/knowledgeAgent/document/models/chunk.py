from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ChunkMetadata:
    """Metadata specific to a text chunk"""
    
    # Structural context
    section_title: Optional[str] = None      # Title of the section containing chunk
    section_depth: int = 0                   # Heading level (1 for h1, 2 for h2, etc.)
    page_number: Optional[int] = None        # Page number in source document
    is_table: bool = False                   # Whether chunk contains tabular data
    is_code: bool = False                    # Whether chunk contains code
    is_quote: bool = False                   # Whether chunk is a quotation
    
    # Position information
    paragraph_index: Optional[int] = None    # Paragraph number in document
    paragraph_position: Optional[str] = None # Position (start, middle, end)
    
    # Content analysis
    language: Optional[str] = None           # Language of this specific chunk
    word_count: int = 0                      # Number of words in chunk
    # reading_time: float = 0.0                # Estimated reading time in seconds
    # reading_level: Optional[str] = None      # Readability score/level
    
    # Semantic information
    topics: List[str] = field(default_factory=list)  # Main topics in chunk
    keywords: List[str] = field(default_factory=list)  # Key terms
    sentiment: Optional[float] = None        # Sentiment score if applicable
    importance_score: float = 0.0            # Relevance/importance within document
    
    # Processing metadata
    chunk_strategy: str = "paragraph"        # How chunk was created
    token_count: int = 0                     # Tokenized length
    embedding_model: Optional[str] = None    # Model used for embedding

@dataclass
class TextChunk:
    """A discrete segment of document text"""
    id: str                      # Unique identifier
    document_id: str             # Reference to parent document
    content: str                 # Chunk text content
    metadata: ChunkMetadata      # Chunk-specific metadata
    
    # Position in document
    start_index: int             # Start position in original document
    end_index: int               # End position in original document
    
    # Content navigation
    section: Optional[str] = None             # Document section
    heading: Optional[str] = None             # Nearest heading
    page_num: Optional[int] = None            # Page number
    previous_chunk_id: Optional[str] = None   # Previous chunk
    next_chunk_id: Optional[str] = None       # Next chunk
    
    # Semantic information
    embedding: Optional[List[float]] = None   # Vector embedding
    summary: Optional[str] = None             # Generated summary
    
    def __str__(self):
        return self.content