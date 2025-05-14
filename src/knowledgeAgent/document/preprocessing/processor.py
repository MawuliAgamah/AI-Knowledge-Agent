from src.knowledgeAgent.document.preprocessing.parser import _get_parser_for_type
from src.knowledgeAgent.document.manager.document_manager import DocumentManager

class DocumentProcessor:
    """Orchestrates the document processing pipeline, to save raw files to postgres db ready to load into vector db.
    """

    def __init__(self, document_builder, llm, db):
        self.document_builder = document_builder
        self.document_manager = DocumentManager()
        self.llm = llm
        self.db = db

    def preprocess(self, document_path, document_id, document_type):
        document = self._initialise_document(document_path,document_id,document_type)
        document = self._clean_document(document)
        document = self._create_chunks(document)
        document = self._create_metadata(document)
        self._cache_document(document)
        return document 
    
    def _initialise_document(self, document_path, document_type):
        """Initialise the document object."""
        document = self.document_manager.make_new_document(document_path,document_id,document_type)
        return document

    def _clean_document(self, document):
        """Clean the document."""
        return document 
    
    def _create_chunks(self, document):
        return document
    
    def _create_metadata(self, document):
        return document





    # def build_document(self, path_to_document,persist):
    #     """Sequence of operations to build a full document given the path to the document before then saving to a db"""
    #     document = self.document_builder.create_template(path=path_to_document)
    #     document = self.document_builder.create_hash(document_object=document)
    #     document = self.document_builder.load_doc_into_langchain(document_object=document)
    #     document = self.document_builder.pre_process(document_object=document)
    #     document = self.document_builder.chunk_document(document_object=document)
    #     document = self.document_builder.generate_summary(document_object=document, llm=self.llm) # generate summary before adding chunks as we use the summary as chunk metadata
    #     document = self.document_builder.add_chunks(document_object=document, llm=self.llm)
    #     document = self.document_builder.generate_title(document_object = document, llm =self.llm )
    #     self._cache_document(document)
    #     return document

    def _cache_document(self,document_object):
        """Store the contents of the document object to SQL Lite DB"""
        exists = self.db.doc_exists(document_object)
        if exists:
            print('Document Already Created')
        else:
            self.db.save_document(document_object)