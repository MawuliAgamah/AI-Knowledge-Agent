
from abc import ABC, abstractmethod

class DocumentParser(ABC):
    """Base class for document parsers."""
    
    @abstractmethod
    def extract(self, file_path):
        """
        Extract content and metadata from a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            tuple: (content, metadata)
        """
        pass


class DefaultParser():
    """Default parser for unknown file types."""
    
    def extract(self, file_path):
        """Extract content and metadata from an unknown file type."""
        return None, {}


class TextParser():
    """Parser for plain text files."""
    
    def extract(self, file_path):
        """Extract content and metadata from a text file."""
        # Get file stats
        stats = os.stat(file_path)
        created = datetime.fromtimestamp(stats.st_ctime)
        modified = datetime.fromtimestamp(stats.st_mtime)
        
        # Read content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic metadata
        lines = content.split('\n')
        title = os.path.basename(file_path)
        
        # Try to find a title in the first few lines
        for line in lines[:5]:
            if line.strip() and len(line.strip()) < 100:
                title = line.strip()
                break
        
        # Create metadata
        metadata = {
            'title': title,
            'created_date': created,
            'modified_date': modified,
            'language': self._detect_language(content),
            'word_count': len(content.split()),
            'authors': []  # Can't reliably detect from text files
        }
        
        return content, metadata
    
    def _detect_language(self, text):
        """Simple language detection."""
        # In a real implementation, use a language detection library
        return "en"  # Default to English


class MarkdownParser(DocumentParser):
    """Parser for Markdown files."""
    
    def extract(self, file_path):
        """Extract content and metadata from a Markdown file."""
        return 





def _get_parser_for_type(file_type):
    """Get appropriate parser for file type."""
    parsers = {
        # 'pdf': PDFParser(),
        # 'docx': DocxParser(),
        # 'txt': TextParser(),
        'md': MarkdownParser(),
        # 'html': HTMLParser()
    }
    return parsers.get(file_type, DefaultParser())