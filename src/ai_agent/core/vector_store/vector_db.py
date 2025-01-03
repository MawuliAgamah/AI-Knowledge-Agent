
import dotenv
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
import os
import sys

from log import logger


import utils.chroma_utils as chroma_utils
from llama_index.vector_stores.chroma import ChromaVectorStore

from llama_index.core import (
    StorageContext,
    VectorStoreIndex
)


class DataBase:
    """"""

    def __init__(self):
        self.client = None
        self.collections = {}
        self.documents = {}
        self.path_to_db = "/Users/mawuliagamah/utilities/chroma/chroma.s"


load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY,
    model_name="text-embedding-3-small"
)


class DataBaseHandler:
    """
    Class which handle all interactions with the database
    """

    def __init__(self, database, client):
        self.name = "database handler"
        self.database = database
        self.client = client
        logger.info("Created DB Handler")

    def create_collection(self):
        pass

    def get_collection(self, collection_name):
        client = self.client
        collection = client.get_or_create_collection(
            name=collection_name, embedding_function=openai_ef)
        self.database.collections['collection_name'] = collection
        return collection

    def add_document(self, document_object, collection, doc_type):

        collection = self.get_collection(collection)
        if doc_type == "docx":
            chunks = document_object.get_contents("chunks")

            for key, chunk in chunks.items():

                document_summary = chunk['metadata']['Document summary']
                title = chunk['metadata']['Document title']
                key_words = chunk['metadata']['keywords']
                Tags = chunk['metadata']['Tags']
                questons = chunk['metadata']['questions']

                meta_data = {"summary": document_summary,
                             "title": title,
                             "tag": Tags[0] if Tags else '',
                             "keyword": key_words[0] if key_words else '',
                             "questions": questons[0] if questons else ''
                             }

                chroma_utils.add_items(collection=collection,
                                       item=chunk['chunk'].page_content,
                                       metadata=meta_data,
                                       id_num=key
                                       )

            logger.info(f"Document added to collection")
            return self
        else:
            return print("non implemeted")

    def show_collection_contents(self):
        print(self.database.collections)
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


class DataBasePipeline:
    """Database pipeline creates a simple interface to interact with vector store and retreival"""

    def __init__(self, reset_client=True):
        database = DataBase()
        client = chroma_utils.get_client(
            path='/Users/mawuliagamah/gitprojects/STAR/db/chroma/chroma.sqlite3')
        self.db_handler = DataBaseHandler(database=database, client=client)
        if reset_client == True:
            client.reset()  # This empties the client, use in development so we can start with new data
            self.client = client
        else:
            self.client = client

    def add_document(self, document_object, collecton_name, doc_type):
        self.db_handler = self.db_handler.add_document(
            document_object, collection=collecton_name, doc_type=doc_type)
        return self

    def query_data_base(self, query, collection_name=None):
        chorma_client = self.client
        collection = self.db_handler.get_collection(
            collection_name=collection_name)
        index = self.db_handler.create_or_load_vector_store_index(
            chroma_collecion=collection)
        response = self.db_handler.search(index=index, query=query)
        return response

    # def document(self,query):
    #    return output
