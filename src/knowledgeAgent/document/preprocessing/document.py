"""
Script which handles everything related to processing to be embedded.
"""
# import os
# import sys
# import glob
from operator import imod
from pydoc import text
import sqlite3
from dataclasses import dataclass

# from tqdm import tqdm
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain


# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
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

# from ai_agent.core.log import logger
from ai_agent.core.document.sql_queries import (CREATE_LIBRARY_TABLE,
                                                SAVE_DOCUMENT_IN_LIBRARY,DOCUMENT_EXISTS_QUERY)

from regex import F
from rich.console import Console

from ai_agent.core.document.sqldb import DocumentSQL
from ai_agent.core.document.template import Document
    
console = Console()

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
        # self.doc_agent = doc_agent 
   
    def create_template(self, path):
        """Initialise the document object setting the documents path attribute as the path."""
        document_template = self.document.set(path=path)
        console.print("[bold green]✓[/bold green] created document template")
        return document_template

    def check_contents(self,document_object):
        """Look at the contents of the document. If it is empty, then skip the document"""

    def create_hash(self,document_object):
        from hashlib import sha256
        """from the path of the file, create a uniuqe hash in referencee to it"""
        path_to_doc = str(document_object.path)
        hash_object = sha256(path_to_doc.encode())
        document_object = (
                    document_object.update(
                contents="hash", payload=hash_object.hexdigest()[:8])
            )
        # document_object.hash = hash_object.hexdigest()[:8]
        console.print("[bold green]✓[/bold green] document hash generated")
        return document_object

    def load_doc_into_langchain(self, document_object):
        """Loads a document into the langchain data loader."""
        path_to_document = document_object.get_contents('path')
        if path_to_document.endswith('.docx'):
            doc = self.loader_docx.load()
            # document_object.contents['langchain.docObject'] = doc
            document_object = (
                document_object.update(
            contents="langchain.docObject", payload=doc)
        )
            document_object = (
                    document_object.update(
                contents="doctype", payload='docx')
            )
            console.print("[bold green]✓[/bold green] document loaded into langchain (.docx)")
            return document_object
        # Markdown document
        elif path_to_document.endswith('.md'):
            doc = self.loader_md.load()
            # self.document.contents['langchain.docObject'] = doc
            
            document_object = (
                    document_object.update(
                contents="doctype", payload='md')
            )
            document_object = (
                document_object.update(
            contents="langchain.docObject", payload=doc)
        )
            console.print("[bold green]✓[/bold green] document loaded into langchain (.md)")
            return document_object

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
        document_object = (document_object.update(contents="page_content", payload=page_contents))
        console.print("[bold green]✓[/bold green] Stop words removed and lemmatized")
        return document_object

    def chunk_document(self, document_object):
        """Split the document up into chunk"""
        document = document_object.get_contents("document")
        chunks = self.text_splitter.split_documents(document)
        document_object = document_object.update("chunked_document", payload=chunks)
        document_object = document_object.update('number_of_chunks',payload=len(chunks))
        console.print(f"[bold green]✓[/bold green] Document chunked : {len(chunks)} chunks ")
        return document_object

    def add_chunks(self, document_object, llm):
        """Insert the chunks into the document object """
        chunks = document_object.get_contents("chunked_document")
        document_summary = document_object.get_contents("summary")
        document_title = document_object.get_contents("summary")
        chunk_list = []
        for idx, chunk in enumerate(chunks):
            # LLM Creates meta_data for each chunk. Need to make this more 
            metadata = llm.make_chunk_metadata(chunk)
            chunk_store = {
                "chunk": chunk,
                "metadata": {
                    "Document title": document_title,
                    "Document summary": document_summary,
                    "keywords": metadata['Keywords'],
                    "Tags": metadata['Tags'],
                    "questions": metadata['Questions']
                }}
            chunk_list.append(chunk)
            document_object = (
                document_object
                .update(
                    contents="chunks",
                    chunk_id=f"chunk_{idx}",
                    payload=chunk_store
                )
            )
        # calculate the number of chunks and add that to the docuent object 
        document_object = (
        document_object
        .update(
            contents="no_of_chunks",
            payload=len(chunk_list)
            )
        )   
        console.print(f"[bold green]✓[/bold green] Chunks added to document template")
        return document_object

    def generate_summary(self,llm,document_object):
        """Generate a summary of the document using language model."""
        chunks = document_object.get_contents("chunked_document")
        summary = llm.generate_document_summary(chunks = chunks)
        document_object = document_object.update(contents="summary",payload=summary)
        console.print(f"[bold green]✓[/bold green] Summary generated")
        return document_object
            
    def generate_title(self,document_object,llm):
            title = 'working on titles'
            summary = document_object.get_contents('chunked_document')
            title = llm.generate_document_title(chunks = summary)
            document_object = document_object.update(contents = "title", payload=title)
            console.print(f"[bold green]✓[/bold green] Title generated")
            return document_object




from ai_agent.core.agents.document_agent import DocumentAgent
from ai_agent.core.config.config import OllamaConfig
from ai_agent.core.agents.document_agent import DocumentAgentUtilities


def create_doc_builder(path):
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import (
            Docx2txtLoader,
            UnstructuredMarkdownLoader
        )
        # doc_agent = DocumentAgent(config=config, utils=model_utils)

        """create an instanstiated document builder obejct"""
        doc_builder = DocumentBuilder(
            document = Document(),
            loader_docx=Docx2txtLoader(path),
            loader_md=UnstructuredMarkdownLoader(path),
            lemmetizer=WordNetLemmatizer(),
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=5),
            )
        return doc_builder


def build_document(path,meta_data = None,persist = True):
    """Main Function to build a whole document"""
    from ai_agent.core.config.config import OllamaConfig , OpenAIConfig
    doc_builder = create_doc_builder(path = path)

    # will need to refactor this 
    config = OpenAIConfig() 
    model_utils = DocumentAgentUtilities()
    document_agent = DocumentAgent(config=config, utils=model_utils)
    sql_db = DocumentSQL()
    
    # pipeline to build out a document 
    processor = (
        DocumentProcessor(
        document_builder=doc_builder, 
        llm = document_agent,
        db = sql_db
        )
    )
    with console.status("[bold blue] Building document", spinner="dots") as status:
        document = processor.build_document(path_to_document=path, persist=persist)
        status.update("[bold red] saving document")
        processor.save_document_to_db(document)
        status.update("[bold red] Finished ")
    return document



def test_run():
    from pprint import pprint
    import os
    """Test Module"""
    path =   '/Users/mawuliagamah/obsidian vaults/Software Company/BookShelf/Books/The Art of Doing Science and Engineering.md'
    document = build_document(path = path, meta_data=None ,persist=False)
    pprint(document.contents)
    
def init_db():
    """Initialised the data base. Creates on if it doesn't exist"""
    db_path = '/Users/mawuliagamah/gitprojects/aiModule/databases/sql_lite/document_db.db'
    # Create the Document Tables
    with sqlite3.connect(db_path) as conn:
        # Create documents table
        conn.execute(CREATE_LIBRARY_TABLE)
        conn.commit()
    console.print(f"[bold green]✓[/bold green] document db created at : {db_path}")

if __name__ == "__main__":
    test_run()

