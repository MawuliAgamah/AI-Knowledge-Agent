"""
Script which handles everything related to processing to be embedded.
"""
# import os
# import sys
# import glob
import sqlite3
from dataclasses import dataclass

# from tqdm import tqdm
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_community.document_loaders import (
    Docx2txtLoader,
    UnstructuredMarkdownLoader
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

import nltk
from nltk.stem import * # type: ignore


# from .config import config
# Import Langchain

from gensim.parsing.preprocessing import remove_stopwords

from ai_agent.core.agents.document_agent import DocumentAgent
from ai_agent.core.config import config

from ai_agent.core.prompts.document_prompts import (
    map_template,
    reduce_template
)

from ai_agent.core.log import logger
from ai_agent.core.document.sql_queries import (CREATE_LIBRARY_TABLE,
                                                SAVE_DOCUMENT_IN_LIBRARY)

from rich.console import Console
console = Console()

@dataclass
class DocumentState:
    """Tracks the construction state of a document"""
    is_initialized: bool = False
    is_loaded: bool = False
    is_preprocessed: bool = False
    is_chunked: bool = False
    is_summarized: bool = False

import os
class DocumentSQL:
    """Handles SQL operations for documents"""

    def __init__(self):
        self.db_path = "/Users/mawuliagamah/gitprojects/aiModule/databases/sql_lite/document_db.db"
    
    def save_document(self,document):
        """ Persist a fully constructred document to the daatabase"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # insert document db
                # populate the library table
                cursor.execute(SAVE_DOCUMENT_IN_LIBRARY,
                               (
                               document.path,
                               document.chunks,
                               document.no_of_chunks,
                               document.title,
                               document.doctype,
                               document.summary,
                               document.title
                               )
                               )
                # insert document metadata it no 
            console.print(f"[red] Document Saved to DB : {document.path}[/red]")
        except Exception as e:
            console.print(f"[red]Error saving document to database: {e}[/red]")
            return False

    def check_document_exists(self):
        """Query DB to check if a document exists"""


    
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
        self.doc_type = None
        self.contents = {
            "id": None,
            "path": None,
            "document_hash":None,
            "raw_txt": None,
            "langchain.docObject":None,
            "summary": None,
            "chunks": {},
            "no_of_chunks": None,
            "doc_type":None,
            "metadata": {
                "title": None,
                "Topic": None,
                "Filename": None,
                "document_type": "doc_x",
                "category": None,
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

    def update(self, contents, payload, chunk_id=None,):
        """
        method to update a documents contents
        """
        if contents == "path":
            self.contents['path'] = payload
        if contents == "page_content":
            self.contents['langchain.docObject'][0].page_content = payload
            return self
        elif contents == "chunked_document":
            self.contents['chunked_document'] = payload
            return self
        elif contents == "chunks":
            self.contents['chunks'][chunk_id] = payload
            return self
        elif contents == "summary":
            self.contents['summary'] = payload
            return self
        else:
            return ValueError('Not yet implemented')

    def persist(self):
        """Persit the constructed document to SQL"""
   
 
# Define all imports which are used by the class below


class DocumentBuilder:
    """Construct Document Object"""
    def __init__(self,
                 document,
                loader_docx,
                loader_md,
                lemmetizer,
                text_splitter,
                ):
        self.name = "word document builder"
        self.document = document
        self.loader_docx = loader_docx
        self.loader_md = loader_md
        self.lemmetizer = lemmetizer
        self.text_splitter = text_splitter
   
    def create_template(self, path):
        """Initialise the document object setting the documents path attribute as the path."""
        document_template = self.document.set(path=path)
        console.print("[bold green]✓[/bold green] created document template")
        return document_template

    def create_hash(self,document_object):
        from hashlib import sha256
        """from the path of the file, create a uniuqe hash in referencee to it"""
        path_to_doc = str(document_object.path)
        hash_object = sha256(path_to_doc.encode())
        document_object.hash = hash_object.hexdigest()[:8]
        console.print("[bold green]✓[/bold green] document hash generated")
        return document_object

    def load_doc_into_langchain(self, document_object):
        """Loads a document into the langchain data loader."""
        path_to_document = document_object.get_contents('path')
        if path_to_document.endswith('.docx'):
            doc = self.loader_docx.load()
            document_object.contents['langchain.docObject'] = doc
            document_object.doc_type = 'docx'
            console.print("[bold green]✓[/bold green] document loaded into langchain (.docx)")
            return document_object
        # Markdown document
        elif path_to_document.endswith('.md'):
            doc = self.loader_md.load()
            self.document.contents['langchain.docObject'] = doc
            self.document.doc_type = 'md'
            console.print("[bold green]✓[/bold green] document loaded into langchain (.md)")
            return self.document

    def pre_process(self, document_object):
        """..."""
        # Get page contents from the document object
        page_contents = document_object.get_contents(contents="page_contents")
        page_contents = page_contents.lower()  # Make page contents lower case
        # stemmer = PorterStemmer()  # Create stemmer
        lemmertizer = self.lemmetizer # instantiate lemmertizer
        page_contents = ' '.join(lemmertizer.lemmatize(token) for token in nltk.word_tokenize(page_contents))
        page_contents = remove_stopwords(page_contents)  # remove stop words
        # Update the page contents of the documnet
        document_object = (document_object.update(
            contents="page_content", payload=page_contents)
        )
        console.print("[bold green]✓[/bold green] Stop words removed and lemmatized")
        return document_object

    def chunk_document(self, document_object):
        """
        Chunks document into pieces

        params
        ------
        document_object : object

        returns
        -------
        document_object : object
        """
        docoument = document_object.get_contents("document")
        chunks = self.text_splitter.split_documents(docoument)
        document_object = document_object.update(
            "chunked_document", payload=chunks)

        # calculate the number of chunks 
        return document_object

    def add_chunks(self, document_object, llm):
        """Insert the chunks intot the document object """

        chunks = document_object.get_contents("chunked_document")
        document_summary = document_object.get_contents("summary")
        # document_title = document_object.get_contents("title")

        # Add the chunk a longside it's ID to the Chunks dictionairy
        logger.info(f"{len(chunks)} chunks to iterate through in this doucment")

        # for idx,chunk in tqdm(enumerate(chunks),desc="Chunking with metadata : ",total=len(chunks)):
        chunk_list = []
        for idx, chunk in enumerate(chunks):
            logger.info(f"Chunk : {idx}")
            metadata = llm.make_metadata(chunk)
            chunk_store = {
                "chunk": chunk,
                "metadata": {
                    "Document title": "NaN",
                    "Document summary": document_summary,
                    "keywords": metadata['Keywords'],
                    "Tags": metadata['Tags'],
                    "questions": metadata['Questions']
                }}
            chunk_list.append(chunk)
            print('Chunks' ,chunk_list)    
            print('n_Chunks' ,len(chunk_list))    

            document_object = (
                document_object
                .update(
                    contents="chunks",
                    chunk_id=f"chunk_{idx}",
                    payload=chunk_store
                )
            )
        return document_object

    def generate_summary(self, document_object, llm):
        """
        Generate a summary of the document using language model.

        params
        ------
        document_object : object
        document object which stores a document, and related meta data.

        llm : object
        language model used to summarise the document.

        returns
        ------
        The document object.
        """
        # We should encapsulate all of this into the LLM, so that its the llm that does the map reduce.
        # Create document summary via langchains map reduce - document_summary = llm.map_reduce(map_prompt,reduce_prompt)
        map_prompt = PromptTemplate.from_template(map_template)
        reduce_prompt = PromptTemplate.from_template(reduce_template)

        map_chain = llm.llm_chain(prompt=map_prompt)
        reduce_chain = llm.llm_chain(prompt=reduce_prompt)
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="doc_summaries")
        # logger.info(f"Combine document chain : {combine_documents_chain}")
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            collapse_documents_chain=combine_documents_chain
        )
        # logger.info(f"Combine document chain : {reduce_documents_chain}")
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain, document_variable_name="content",
            reduce_documents_chain=reduce_documents_chain
        )
        logger.info(f"{map_reduce_chain}")
        # We use the chunked document to feed into langchain
        chunked_dcoument = document_object.get_contents("chunked_document")
        # Get contents of the chunked document to then send into the map reduce chain
        document_summary = map_reduce_chain.run(chunked_dcoument)
        # Update the document summary with the generated summary
        document_object = document_object.update(
            "summary", payload=document_summary)

        document_object.summary = document_summary
        console.print("[bold green]✓[/bold green] Document summary generated")
        return document_object

    def generate_meta_data(self, document_object_llm):
        """

        """
        pass


class DocumentPipeline:
    """
    Class that serves as a higher level orchestrator.
    Uses the document builder to perform a sequence of operations
    on a document objec to construct a document for insertion
    into a  vector database.
    attr
    ----
    document_builder : object

    llm : object

    """

    def __init__(self, document_builder, llm, db):
        self.document_builder = document_builder
        self.llm = llm
        self.db = db

    def _persist(self,document_object):
        """Store the contents of the document object to SQL Lite DB"""
        exists = False #self.db.doc_exists()
        created = False #self.doc_created()
        if exists & created:
            print('Document Already Created')
            #self.db.save_document()
            #console.pr
        else:
            print('Persisting DB .... IMPLEMENTING THIS')

    def build_document(self, path_to_document,persist):
        """
        Sequence of operations to build 
        a full document given the path to
        the document.

        params
        ------
        path_to_document : str
        path to the document on file
        """
        # Check if the document has already been created:
         

        document_template = self.document_builder.create_template(path=path_to_document)
        hashed_document = self.document_builder.create_hash(document_object=document_template)
        
        document = (
            self.document_builder
            .load_doc_into_langchain(document_object=hashed_document)
        )
        document = self.document_builder.pre_process(document_object=document)
        document = self.document_builder.chunk_document(
            document_object=document)
        # Create the document summary using a language model
        document = self.document_builder.generate_summary(
            document_object=document, llm=self.llm)
        # Create the document summary using a language model
        document = self.document_builder.add_chunks(
            document_object=document, llm=self.llm)
        
        if persist:
            print("Saving document")
        else:
            print("Persit = False, document not saved")
        #    self._persist(document)
        return document



def build_document(path,meta_data = None,persist = True):
    """Main Function to build a whole document"""
    doc_builder = DocumentBuilder(document = Document(),
                                  loader_docx=Docx2txtLoader(path),
                                  loader_md=UnstructuredMarkdownLoader(path),
                                  lemmetizer=WordNetLemmatizer(),
                                  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=5))

    # will need to refactor this 
    document_agent = DocumentAgent(config=config,llm = ChatOpenAI, model = 'gpt-3.5-turbo')
    sql_db = DocumentSQL()
    
    # pipeline to build out a document 
    doc_pipeline = (
        DocumentPipeline(
        document_builder=doc_builder, 
        llm = document_agent,
        db = sql_db,
        )
    )
    from time import sleep
    with console.status("[bold blue] Building document", spinner="dots") as status:

        doc_pipeline.build_document(path_to_document=path, persist=persist)

        status.update("[bold red] Finished ")


from pprint import pprint
def test_run():
    """Test Module"""
    import os 
    path = os.path.join(
            "/Users/mawuliagamah/obsidian vaults",
            "Software Company/Learning/Machine Learning",
            "Graph Neural Networks.md"
        )
    
    document = build_document(path = path, meta_data=None ,persist=False)
    pprint(document.contents)
    
# self._init_db()

def init_db(self):
    """Initialised the data base. Creates on if it doesn't exist"""
    self.db_path = '/Users/mawuliagamah/gitprojects/aiModule/databases/sql_lite/document_db.db'
    # Create the Document Tables
    with sqlite3.connect(self.db_path) as conn:
        # Create documents table
        conn.execute(CREATE_LIBRARY_TABLE)
        conn.commit()
    console.print(f"[bold green]✓[/bold green] document db created at : {self.db_path}")



if __name__ == "__main__":
    test_run()


#    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"

#    document_builder = DocumentBuilder()
#    document_agent = DocumentAgent(config=config)

#    pipeline = DocumentPipeline(document_builder = document_builder ,llm = document_agent)
#    document_object = pipeline.build_document(path_to_document = path)

#    print(document_object.contents)
