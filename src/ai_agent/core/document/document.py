"""
Script which handles everything related to processing to be embedded.
"""
# import os
# import sys
# import glob
from operator import imod
import sqlite3
from dataclasses import dataclass

# from tqdm import tqdm
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_community.document_loaders import (
    Docx2txtLoader,
    UnstructuredMarkdownLoader
)

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

from ai_agent.core.log import logger
from ai_agent.core.document.sql_queries import (CREATE_LIBRARY_TABLE,
                                                SAVE_DOCUMENT_IN_LIBRARY,DOCUMENT_EXISTS_QUERY)

from rich.console import Console

from ai_agent.core.document.sqldb import DocumentSQL
from ai_agent.core.document.template import Document
    
console = Console()

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
        document = document_object.get_contents("document")
        chunks = self.text_splitter.split_documents(document)
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
            # LLM Creates meta_data for each chunk. Need to make this more 
            metadata = llm.make_chunk_metadata(chunk)
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
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate
        
        # Extract the actual LLM from the DocumentAgent
        actual_llm = llm.llm
        
        # Create prompt template for summarization
        prompt = ChatPromptTemplate.from_template("Summarize this content: {context}")
    
        # Create the chain using the actual LLM
        chain = create_stuff_documents_chain(actual_llm, prompt)
        
        # Get the chunked document
        chunks = document_object.get_contents("chunked_document")
        
        try:
            # Generate summary using the chain - note the changed input format
            document_summary = chain.invoke({
                "context": chunks
            })
            
            # The result might be in a different format now, so let's handle that
            if isinstance(document_summary, dict):
                summary_text = document_summary.get('output', '')
            else:
                summary_text = str(document_summary)
            

            # Update the document summary
            document_object = document_object.update(
                "summary", payload=summary_text
            )
            
            console.print("[bold green]✓[/bold green] Document summary generated")
            return document_object
            
        except Exception as e:
            console.print(f"[bold red]Error generating summary: {str(e)}[/bold red]")
            raise

    def generate_title(self,document_object,llm):
            title = 'working on titles'
            document_object = document_object.update(
                contents = "title", payload=title
            )
            return document_object


class DocumentPipeline:
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
        """Sequence of operations to build a full document given the path to the document."""
        document = self.document_builder.create_template(path=path_to_document)
        document = self.document_builder.create_hash(document_object=document)
        document = self.document_builder.load_doc_into_langchain(document_object=document)
        document = self.document_builder.pre_process(document_object=document)
        document = self.document_builder.chunk_document(document_object=document)
        document = self.document_builder.generate_summary(document_object=document, llm=self.llm)
        document = self.document_builder.add_chunks(document_object=document, llm=self.llm)
        document = self.document_builder.generate_title(document_object = document, llm =self.llm )
        self.save_document_to_db(document)
        return document


def create_doc_builder(path):
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        """create an instanstiated document builder obejct"""
        doc_builder = DocumentBuilder(
            document = Document(),
            loader_docx=Docx2txtLoader(path),
            loader_md=UnstructuredMarkdownLoader(path),
            lemmetizer=WordNetLemmatizer(),
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=5)
            )
        return doc_builder


def build_document(path,meta_data = None,persist = True):
    """Main Function to build a whole document"""
    doc_builder = create_doc_builder(path = path)

    # will need to refactor this 
    document_agent = DocumentAgent(config=config,llm = ChatOllama(model ='llama3.2:latest'), model = 'llama3.2:latest')
    sql_db = DocumentSQL()
    
    # pipeline to build out a document 
    doc_pipeline = (
        DocumentPipeline(
        document_builder=doc_builder, 
        llm = document_agent,
        db = sql_db
        )
    )
    with console.status("[bold blue] Building document", spinner="dots") as status:
        document = doc_pipeline.build_document(path_to_document=path, persist=persist)
        status.update("[bold red] saving document")
        doc_pipeline.save_document_to_db(document)
        status.update("[bold red] Finished ")
    return document


from pprint import pprint
def test_run():
    """Test Module"""
    import os     
    document = build_document(path = '/Users/mawuliagamah/obsidian vaults/Software Company/BookShelf/Books/The Art of Doing Science and Engineering.md', meta_data=None ,persist=True)
    pprint(document.contents)
    
# self._init_db()

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
    # init_db()
    test_run()

