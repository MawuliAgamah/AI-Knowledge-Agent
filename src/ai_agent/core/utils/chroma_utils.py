"""


Author : Mawuli Agamah
Version : 0.1.0
License:
"""
import os
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
import chromadb.utils.embedding_functions as embedding_functions

# from pathlib import Path
# from chromadb import Client as ChromaClient
# from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
# from dotenv import load_dotenv, find_dotenv
# from ..log import logger


def get_client(path):
    """
    Create or get the database client
    """
    if os.path.exists(path):
        print("DB already exists") 
        client = chromadb.PersistentClient(
        path=path,
        settings= Settings(allow_reset=True),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
        )
    else:
        print("Making new client") 
        client = chromadb.PersistentClient(
        path=path,
        settings=Settings(allow_reset=True),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
        )

    return client


def get_chroma_client(path_to_vectordb):
    """create or get chroma db from disk"""
    if os.path.exists(f'{path_to_vectordb}/chroma.sqlite3'):
        print("DB already exists")
        client = chromadb.PersistentClient(
            path=path_to_vectordb)

    else:
        print("Making new client")
        client = chromadb.PersistentClient(
            path=path_to_vectordb,
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )

    return client


def get_or_create_collection(client, colleciton_name):
    """Create a chroma collection from client"""
    collection = client.create_collection(name=colleciton_name)
    return collection


def add_item_to_chroma_db(collection, item, metadata, id_num):
    """Function which adds/stores items to the Chroma DB"""
    # Does the item exist in my collection?
    collection_ids = collection.get(include=[])
    if id_num in collection_ids['ids']:
        # print(f"{id_num} is already in collection, moving to next id.")
        pass
    else:
        collection.add(
            documents=item,
            metadatas=metadata,
            ids=id_num
        )


def add_items(collection, item, metadata, id_num):
    """Function which adds/stores items to the Chroma DB
    """
    # Does the item exist in my collection?
    collection_ids = collection.get(include=[])
    if id_num in collection_ids['ids']:
        print(f"{id_num} is already in collection, moving to next id.")

    else:
        collection.add(
            documents=item,
            metadatas=[metadata],
            ids=[id_num]
        )


def query_vector_db(query, collection):
    """"""
    results = collection.query(
        query_texts=[query],
        n_results=5,
        include=['documents', 'metadatas', 'distances']
    )

    final_retrival = "\n\n".join(results['documents'][0])
    return final_retrival
