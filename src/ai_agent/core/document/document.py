"""
Script which handles everything related to processing to be embedded.
"""
# import os
# import sys
# import glob
import sqlite3

# from tqdm import tqdm
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_community.document_loaders import (
    Docx2txtLoader,
    UnstructuredMarkdownLoader
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate


import nltk
from nltk.stem import *


# from .config import config
# Import Langchain

from gensim.parsing.preprocessing import remove_stopwords

from ai_agent.core.agents.document_agent import DocumentAgent

from prompts.document_prompts import (
    map_template,
    reduce_template
)

from ai_agent.core.log import logger


@dataclass
class DocumentState:
    """Tracks the construction state of a document"""
    is_initialized: bool = False
    is_loaded: bool = False
    is_preprocessed: bool = False
    is_chunked: bool = False
    is_summarized: bool = False


class DocumentSQL:
    """Handles SQL operations for documents"""

        def __init__(self, db_path: str = "documents.db"):
            self.db_path = db_path
            self._init_db()















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

    def __init__(self, path):
        self.contents = {
            "id": None,
            "path": path,
            "document": None,
            "chunked_document": None,
            "chunks": {},
            "summary": None,
            "metadata": {
                "title": None,
                "Topic": None,
                "Filename": None,
                "document_type": "doc_x",
                "category": None,
            }
        }

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
            return self.contents['document']
        elif contents == "path":
            return self.contents['path']
        elif contents == "summary":
            return self.contents['summary']
        elif contents == "chunked_document":
            return self.contents['chunked_document']
        elif contents == "chunks":
            return self.contents['chunks']
        elif contents == "page_contents":
            return self.contents['document'][0].page_content

    def update(self, contents, payload, chunk_id=None,):
        """
        method to update a documents contents

        """
        if contents == "page_content":
            self.contents['document'][0].page_content = payload
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


# Define all imports which are used by the class below


class DocumentBuilder:
    """
    Class that handles all tasks involved in constructing a document.
    loading, pre-processing, summarisation
    attr
    ----
    """

    def __init__(self):
        self.name = "word document builder"

    def init(self, path):
        """
        initialises the document object setting the documents path attribute as the path.
        """
        document = Document(path=path)
        logger.info("Created document template")
        return document

    def load(self, document_object):
        """Loads a document into the langchain data loader.

        Parameters:
            document_object (Document): The Document object to load

        Returns:
            Document: The Document object with loaded content
        """
        path_to_document = document_object.get_contents('path')
        if path_to_document.endswith('.docx'):
            loader = Docx2txtLoader(path_to_document)
            doc = loader.load()
            document_object.contents['document'] = doc
            logger.info("Word Document Loaded")
            return document_object
        # Markdown document
        elif path_to_document.endswith('.md'):
            loader = UnstructuredMarkdownLoader(path_to_document)
            doc = loader.load()
            document_object.contents['document'] = doc
            logger.info("Markdown Document Loaded")
            document_object.contents['metadata']['document_type'] = 'md'
            return document_object

    def pre_process(self, document_object):
        """
        ...
        """
        # Get page contents from the document object
        page_contents = document_object.get_contents(contents="page_contents")
        page_contents = page_contents.lower()  # Make page contents lower case
        # stemmer = PorterStemmer()  # Create stemmer
        lemmertizer = WordNetLemmatizer()  # instantiate lemmertizer
        page_contents = ' '.join(lemmertizer.lemmatize(
            # Lemmertize
            token) for token in nltk.word_tokenize(page_contents))
        page_contents = remove_stopwords(page_contents)  # remove stop words
        # Update the page contents of the documnet
        document_object = document_object.update(
            contents="page_content", payload=page_contents)
        logger.info("Document Pre-Processed")  # Log on completion
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
        docoument = document_object.get_contents(
            # Get the contents of the document contents from the document. This is a langchain document object.
            "document")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=5)
        chunks = text_splitter.split_documents(docoument)
        document_object = document_object.update(
            "chunked_document", payload=chunks)
        return document_object

    def add_chunks(self, document_object, llm):
        """
        Insert the chunks intot the document object 
        """

        chunks = document_object.get_contents("chunked_document")
        document_summary = document_object.get_contents("summary")
        # document_title = document_object.get_contents("title")

        # Add the chunk a longside it's ID to the Chunks dictionairy
        logger.info(
            f"{len(chunks)} chunks to iterate through in this doucment")

        # for idx,chunk in tqdm(enumerate(chunks),desc="Chunking with metadata : ",total=len(chunks)):
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

    def __init__(self, document_builder, llm):
        self.document_builder = document_builder
        self.llm = llm

    def build_document(self, path_to_document):
        """
        Sequence of operations to build 
        a full document given the path to
        the document.

        params
        ------
        path_to_document : str
        path to the document on file
        """
        document_template = self.document_builder.init(path=path_to_document)
        document = (
            self.document_builder
            .load(document_object=document_template)
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
        return document


# if __name__ == "__main__":

#    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"

#    document_builder = DocumentBuilder()
#    document_agent = DocumentAgent(config=config)

#    pipeline = DocumentPipeline(document_builder = document_builder ,llm = document_agent)
#    document_object = pipeline.build_document(path_to_document = path)

#    print(document_object.contents)
