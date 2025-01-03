"""
Author : Mawuli Agamah
Version : 0.1.0
License:
"""
from dataclasses import dataclass
from typing import List, Optional, Any
from pathlib import Path
from ai_agent.core.utils import chroma_utils
from langchain_openai import ChatOpenAI
# from utils.chroma_utils import (get_client, add_item_to_chroma_db)

from document.document import (
    DocumentPipeline,
    DocumentBuilder
)

# Handles everything related to interacting with the database

from vector_store.vector_db import (
    DataBaseHandler,
    DataBase as VectorDb,
    DataBasePipeline
)

from agents.document_agent import DocumentAgent
from config.config import config


@dataclass
class Config:
    """Configuration class for AgentModule"""
    vector_db_path: str
    chroma_client: Optional[Any]  # not sure what the chorma client is yet
    model_name: str = "gpt-3.5-turbo"
    rag_type: str = "vector"
    reset_db: bool = False
    collection: str = "base"


class AgentModule:
    """Entry point to ai agent system"""
    database: Optional[DataBasePipeline]
    document_agent: Optional[DocumentAgent]
    document_parser: Optional[DocumentPipeline]
    client: Optional[Any]  # Type from chroma client
    parsed_documents: List[Any]  # Type from your document objects

    def __init__(self, configuration: Config):
        self.client = None
        self.document_parser = None
        self.document_agent = None
        self.database = None
        self.parsed_documents = []
        self.config = configuration

        # initialise all components
        self._initialize_components()

    def _initialize_components(self):
        """
        initalise all of the data and objects needed to then run the code

        """
        if self.config.rag_type == "vector":
            self._initialise_with_vector_rag()
        else:
            raise ValueError(f"Unsupported RAG type: {self.config.rag_type}")

    def _initialise_with_vector_rag(self) -> None:
        """Set up AI agent with vector based rag"""
        # ----------------------------------
        # 1. initialise vector database handler
        # ----------------------------------
        self.database = DataBasePipeline(reset_client=True,
                                         client=self.config.chroma_client
                                         )
        # ----------------------------------
        # 2.initialise document agent
        # ----------------------------------
        self.document_agent = DocumentAgent(
            config=config,
            model=self.config.model_name,
            llm=ChatOpenAI
        )
        # ----------------------------------
        # initialise builders
        # ----------------------------------
        document_builder = DocumentBuilder()
        self.document_parser = (
            DocumentPipeline(
                document_builder=document_builder,
                llm=self.document_agent
            )
        )

    def parse_document(self, path_to_document: List['str']):
        """For a list of paths to document,
           build the agents internal document Model
        """
        for doc_path in path_to_document:
            try:
                document = self.document_parser \
                    .build_document(path_to_document=doc_path)  # type: ignore
                self.parsed_documents.append(document)
                print("Document Parsed and Stored in List")
                print(document.contents['summary'])
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error parsing document {doc_path}: {str(e)}")
        return self

    def embed_documents(self, collection):
        """Embed users documnets in vector db"""
        collection = (self.database
                      .get_collection(
                        client=self.client, colleciton_name=collection)
                      )

        for idx, item in enumerate(self.parsed_documents):
            self.database.add_document(document_object=item,  # type: ignore
                                       collecton_name="word_documents",
                                       doc_type="md"
                                       )

            chroma_utils.add_item_to_chroma_db(
                collection=collection, item=item, id_num=idx,
                metadata={"folders": "machinelearning"},
            )

    def query(self, query):
        """ ... """
        response = (self.database.query_data_base(  # type: ignore
            query=query,
            collection_name="word_documents"
            )
        )
        return response


def create_module(vector_db_path: str,
                  collection: str,
                  model_name: str = "gpt-3.5-turbo",
                  rag_type: str = "vector",
                  reset_db: bool = False,
                  ) -> AgentModule:
    """Set up the Agent"""
    client = chroma_utils.get_client(path=vector_db_path) # grab client to work with chroma db
    configuraton = Config(
        vector_db_path=vector_db_path,
        chroma_client=client,
        model_name=model_name,
        collection=collection,
        rag_type=rag_type,
        reset_db=reset_db
    )
    return AgentModule(configuraton)


def test_run(path_to_note):
    """
    Testing
    """

    agent = create_module(
        vector_db_path="/Users/mawuliagamah/utilities/chroma/chroma.sqlite3",
        collection="obsidan_databse",
        model_name="gpt-3.5-turbo",
        reset_db=True
        )

    agent.parse_document(path_to_document=path_to_note)\
        .embed_documents(collection="obsidan_databse")

    agent.query("What are my knowledge gaps in graph neural networks?")

    # agent = (
    #    agent
    #    .set_up(path_to_vectordb='/Users/mawuliagamah/utilities/chroma',
    #            rag='vector'
    #            )
    # )

    #  """ BLOCK 2 : RAG """

    # Instantiate a database pipeline
    # database_pipeline = DataBasePipeline(reset_client=True)

    # database_pipeline = database_pipeline.add_document(
    #    document_object, collecton_name="word_documents", doc_type="docx")

    # resonse = database_pipeline.query_data_base(
    #    query="What skills do i need for a data role?", collection_name="word_documents")


if __name__ == "__main__":
    notes = ["""/Users/mawuliagamah/obsidian vaults/Software Company/Learning/Machine Learning/Graph Neural Networks.md"""]
    test_run(path_to_note=notes)
