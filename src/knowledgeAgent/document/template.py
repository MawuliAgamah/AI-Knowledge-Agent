
from aiohttp import payload_type


class Document:
    """The Document Object Class that represents a document and
    its associated metadata.

    Class serves as a container for document content, 
    metadata, and processing states. Maintains information about the document's path, content, chunks,
    summaries, and other metadata in a structured format.

    Attributes:
        contents (dict): A dictionary containing all document-related 
        information including:
            - id: Unique identifier for the document
            - path: File path to the document
            - document: The loaded document object
            - chunked_document: Document split into smaller chunks
            - chunks: Dictionary of processed document chunks with metadata
            - summary: Document summary
            - metadata: Document metadata 
                        including title, topic, filename, etc.
    """

    def __init__(self):
        self.id = None
        self.hash = None
        self.path = None
        self.title = None,
        self.summary = None,
        self.doc_type = None
        self.number_of_chunks = None
        self.contents = {
            "id": None,
            "path": None,
            "document_hash":None,
            "raw_txt": None,
            "langchain.docObject":None,
            "summary": None,
            "chunks": {},
            "number_of_chunks": None,
            "doc_type":None,
            "metadata": {
                "title": self.title,
                "Filename": self.path,
                "document_type":self.doc_type,
            }
        }

    def set(self,path):
        """Set up a document with initial content"""
        self.contents['path'] = path
        self.path = path
        return self 

    def get_document(self):
        """
        Pull out a document
        """
        return self

    def get_contents(self, contents):
        """
        Returns the contents of different attributes of the document.
        self.contents['docuemnt'] currently stores the document
        as a langchain document.The raw text is accessed via [0].page_contents
        """
        if contents == "document":
            return self.contents['langchain.docObject']
        if contents == "title":
            return self.title
        elif contents == "path":
            return self.contents['path']
        elif contents == "summary":
            return self.contents['summary']
        elif contents == "chunked_document":
            return self.contents['chunked_document']
        elif contents == "chunks":
            return self.contents['chunks']
        elif contents == "page_contents":
            return self.contents['langchain.docObject'][0].page_content

    def update(self,contents,payload, chunk_id=None,):
        """
        update the document
        """
        if contents == "hash":
            self.hash = payload
            self.contents['document_hash'] = payload 
            return self
        elif contents == "doctype":
            self.doc_type = payload
            self.contents['doc_type'] = payload
            return self
        elif contents == 'title':
            self.title = payload
            return self
        elif contents == "path":
            self.contents['path'] = payload
            return self
        elif contents == 'langchain.docObject':
            self.contents['langchain.docObject'] = payload
            return self
        elif contents == "page_content":
            # may not be redundant but shall check
            self.contents['langchain.docObject'][0].page_content = payload
            return self
        elif contents == "chunked_document":
            self.contents['chunked_document'] = payload
            return self
        elif contents == "chunks":
            self.contents['chunks'][chunk_id] = payload
            return self
        elif contents == "no_of_chunks":
            self.contents['no_of_chunks'] = payload
            return self
        elif contents == "summary":
            self.contents['summary'] = payload
            self.summary = payload 
            return self
        elif contents == "number_of_chunks":
            self.no_chunks = payload
            return self 
        else:
            return ValueError('Not yet implemented')

    def persist(self):
        """Persit the constructed document to SQL"""
   