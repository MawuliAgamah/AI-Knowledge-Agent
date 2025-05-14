

class Chunker:
    """Tools used by the doc builder"""    
    def __init__(self,text_splitter):
        self.text_splitter = text_splitter

    def chunk(self,document):
        """Different chunking strategies"""
        pass 
    
    def _create_chunk_metadata(self,document):
        """Create chunk metadata"""
        print("creating chunk related metadata")
        return document
