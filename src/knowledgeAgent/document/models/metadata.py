
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class DocumentMetadata:
    """Contains all metadata about the document."""
    title: Optional[str] = None        # Document title
    authors: List[str] = field(default_factory=list)  # Author names
    created_date: Optional[datetime] = None  # Document creation date
    modified_date: Optional[datetime] = None  # Last modified date
    
    # Content metadata
    language: str = "en"               # Document language
    num_pages: Optional[int] = None    # Number of pages
    word_count: int = 0                # Word count
    section_headers: List[str] = field(default_factory=list)  # Main section headers
    
    # Bibliographic
    publisher: Optional[str] = None    # Publisher information
    doi: Optional[str] = None          # Digital Object Identifier
    isbn: Optional[str] = None         # For books
    citations: List[Citation] = field(default_factory=list)   # Referenced works
    
    # Custom metadata
    tags: List[str] = field(default_factory=list)     # User-assigned tags
    categories: List[str] = field(default_factory=list)  # Categories
    custom_fields: Dict[str, Any] = field(default_factory=dict)  # Extensible custom metadata
