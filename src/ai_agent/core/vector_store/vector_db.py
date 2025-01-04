"""This scri
Database class :
Database handler:
Database Pipeline:
"""
# import dotenv
# import sys
import os
from typing import Any

from dataclasses import dataclass
import chromadb.utils.embedding_functions as embedding_functions
from llama_index.vector_stores.chroma import ChromaVectorStore


from llama_index.core import (
    StorageContext,
    VectorStoreIndex
)

from dotenv import load_dotenv

from rich.console import Console
# from rich.panel import Panel
# from rich.table import Table
# from rich.progress import track
# from rich import print as rprint

from ai_agent.core.log import logger
from ai_agent.core.utils import chroma_utils

console = Console()


@dataclass
class VectorStoreConfig:
    """Confiuration class for the database"""
    def __init__(self, path_to_chroma_db):
        self.path_to_chroma_db = path_to_chroma_db
        self.client = self.get_chroma_client()
        self.engine = None
        self.api_key: str
        self.embedding_model = "text-embedding-3-small"

    def get_chroma_client(self) -> Any:
        """Get the chroma db client"""
        client = chroma_utils.get_client(path=self.path_to_chroma_db)
        print(client)
        return client

    def get_embedding_function(self) -> Any:
        """Get the embedding function"""
        load_dotenv()
        return embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=self.embedding_model
                )


class VecStoreEngine:
    """Class which handle all interactions with the database"""

    def __init__(self, config):
        self.name = "database handler"
        self.config = config

    def get_collection(self, collection_name):
        """Get a collection"""
        client = self.config.client
        collection = client.get_or_create_collection(name=collection_name)
        client.collections[f'{collection_name}'] = collection
        return collection

    def add_document(self, document_object, collecton_name, doc_type):
        """
            document_object : Document() class generated in document.py
        """
        # get the chroma db collection
        collection = self.get_collection(collecton_name)
        chunks = document_object.get_contents("chunks")

        for key, chunk in chunks.items():

            document_summary = chunk['metadata']['Document summary']
            title = chunk['metadata']['Document title']
            key_words = chunk['metadata']['keywords']
            tags = chunk['metadata']['Tags']
            questons = chunk['metadata']['questions']

            meta_data = {"summary": document_summary,
                         "title": title,
                         "tag": tags[0] if tags else '',
                         "keyword": key_words[0] if key_words else '',
                         "questions": questons[0] if questons else ''}

            chroma_utils.add_items(collection=collection,
                                   item=chunk['chunk'].page_content,
                                   metadata=meta_data,
                                   id_num=key)

        path = document_object.get_contents("path")
        console.print(f"[bold green]✓[/bold green] {path} added to db")
        return self


    def show_collection_contents(self):
        """Show the collections"""
        print(self.config.client.list_collections())

    def load_vector_store_index(self, chroma_collecion):
        """Load up the Vector Store Index"""
        # Check if index exists
        vector_store = ChromaVectorStore(chroma_collection=chroma_collecion)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)

        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context
        )
        return index

    def search(self, index, query):
        """Query the database using llama index"""
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return response


class VectorStore:
    """
    Interface to interact with the vector stor
       methods:
        add_document()

        query_data_base()

    """
    def __init__(self, client, config, engine, collection, reset_client=True):
        self.config = config
        self.engine = engine
        self.collection = collection
 
        if reset_client:
            client = self.config.client.reset()  # This empties the database
            self.config = client
        else:
            pass

    def add_document(self, document_object, collecton_name, doc_type):
        """Add docuemnt to the vector store """
        self.engine.add_document(document_object,
                                 collection=collecton_name,
                                 doc_type=doc_type)
        return self

    def query_data_base(self, query):
        """Query the vector store"""
        collection_name = self.collection
        collection = (self.engine
                      .get_collection(collection_name=collection_name))
        index = (self.engine
                 .load_vector_store_index(chroma_collecion=collection))
        response = self.engine.search(index=index, query=query)
        return response


def initialise_vector_store(path_to_chroma_db, collection, collection_name):
    """Instantite and set up a vector store so it's ready to go"""
    configuraton = VectorStoreConfig(path_to_chroma_db=path_to_chroma_db)
    engine = VecStoreEngine(config=configuraton)
    client = configuraton.get_chroma_client()
    vec_store = (VectorStore(config=configuraton,
                             engine=engine,
                             client=client,
                             collection=collection))
    console.print("[bold green]✓[/bold green] Chroma DB Initialised ")
    return vec_store


def test_run():
    """Enhanced test run with rich output"""
    initialise_vector_store(
        path_to_chroma_db="/Users/mawuliagamah/utilities/chroma",
        collection="obsidian_database",
        collection_name="obsidian_database"
        )
    console.print("[bold green]✓[/bold green] Test run completed successfully")

    # Display some test information
    # test_info = Table(title="Vector Store Information")
    # test_info.add_column("Property", style="cyan")
    # test_info.add_column("Value", style="magenta")
    # test_info.add_row("Database Path", str(store.config.path_to_chroma_db))
    # test_info.add_row("Collection", store.collection)
    # test_info.add_row("Embedding Model", store.config.embedding_model)

    # except Exception as e:
    #    console.print(f"[red]Test run failed: {e}[/red]")


if __name__ == "__main__":
    test_run()
