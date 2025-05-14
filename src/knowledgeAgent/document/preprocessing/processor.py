class DocumentProcessor:
    """Orchestrates the document processing pipeline, to save raw files to postgres db ready to load into vector db.
    
    This pipeline manages the end-to-end process of document processing, including:
    - Document loading and parsing
    - Text preprocessing and chunking
    - Summary and metadata generation using LLMs
    - Database storage and deduplication
    
    Attributes:
        document_builder: Handles individual document processing operations
        llm: Language model for generating summaries and metadata
        db: Database connection for document storage
    
    Example:
        pipeline = DocumentPipeline(
            document_builder=DocBuilder(),
            llm=OpenAIAgent(),
            db=VectorDB()
        )
        doc = pipeline.build_document("path/to/doc.pdf", persist=True)
    """

    def __init__(self, document_builder, llm, db):
        self.document_builder = document_builder
        self.llm = llm
        self.db = db

    def save_document_to_db(self,document_object):
        """Store the contents of the document object to SQL Lite DB"""
        exists = self.db.doc_exists(document_object)
        if exists:
            print('Document Already Created')
        else:
            self.db.save_document(document_object)

    def build_document(self, path_to_document,persist):
        """Sequence of operations to build a full document given the path to the document before then saving to a db"""
        document = self.document_builder.create_template(path=path_to_document)
        document = self.document_builder.create_hash(document_object=document)
        document = self.document_builder.load_doc_into_langchain(document_object=document)
        document = self.document_builder.pre_process(document_object=document)
        document = self.document_builder.chunk_document(document_object=document)
        document = self.document_builder.generate_summary(document_object=document, llm=self.llm) # generate summary before adding chunks as we use the summary as chunk metadata
        document = self.document_builder.add_chunks(document_object=document, llm=self.llm)
        document = self.document_builder.generate_title(document_object = document, llm =self.llm )
        self.save_document_to_db(document)
        return document