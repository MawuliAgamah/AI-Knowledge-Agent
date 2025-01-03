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
from dotenv import load_dotenv

from log import logger


import utils.chroma_utils as chroma_utils
from llama_index.vector_stores.chroma import ChromaVectorStore

from llama_index.core import (
    StorageContext,
    VectorStoreIndex
)


@dataclass
class VectorStoreConfig:
    """Confiuration class for the database"""
    def __init__(self, path_to_chroma_db):
        self.path_to_chroma_db = path_to_chroma_db
        self.client = None
        engine = None
        self.api_key: str
        self.embedding_model = "text-embedding-3-small"

    def get_chroma_client(self) -> Any:
        """Get the chroma db client"""
        return chroma_utils.get_client(path=self.path_to_chroma_db)

    def get_embedding_function(self) -> Any:
        """Get the embedding function"""
        load_dotenv()
        return embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=self.embedding_model
                )


class VecStoreEngine:
    """Class which handle all interactions with the database"""

    def __init__(self,config):
        self.name = "database handler"
        self.config=config
        logger.info("Created DB Handler")


    def get_collection(self, collection_name):
        """Get a collection"""
        client = self.config.client
        collection = client.get_or_create_collection(name=collection_name)
        client.collections[f'{collection_name}'] = collection
        return collection

    def add_document(self, document_object, collection, doc_type):
        """
            document_object : Document() class generated in document.py
        """
        # get the chroma db collection
        collection = self.get_collection(collection)
        if doc_type == "docx":
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
                             "questions": questons[0] if questons else ''
                             }

                chroma_utils.add_items(collection=collection,
                                       item=chunk['chunk'].page_content,
                                       metadata=meta_data,
                                       id_num=key
                                       )
            
            logger.info("Document added to collection")
            return self
        else:
            return print("non implemeted")

    def show_collection_contents(self):
        """Show the collections"""
        print(self.client.list_collections())

    def create_or_load_vector_store_index(self, chroma_collecion):
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

# self.client = (chroma_utils.get_client(path='/Users/mawuliagamah/gitprojects/STAR/db/chroma/chroma.sqlite3'))


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
        """Query the vector stor e"""
        # chorma_client = self.client
        collection = self.engine.get_collection(collection_name=self.collection)
        index = self.engine.create_or_load_vector_store_index(chroma_collecion=collection)
        response =self.engine.search(index=index, query=query)
        return response

    # def document(self,query):
    #    return output


def initialise_vector_store(path_to_chroma_db, collection):
    """Instantite and set up a vector store so it's ready to go"""
    configuraton = VectorStoreConfig(path_to_chroma_db=path_to_chroma_db)
    engine = VecStoreEngine(config=configuraton)
    client = configuraton.get_chroma_client()
    vec_store = (VectorStore(config=configuraton,
                             engine=engine,
                             client=client,
                             collection=collection))
    return vec_store


