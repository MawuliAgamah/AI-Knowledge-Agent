from chromadb import Client as ChromaClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os

import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path


from log import logger


import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings


def get_client(path):
    """
    Create or get the database client
    """
    if os.path.exists(path):
        print("DB already exists")
        client = chromadb.PersistentClient(

            path=path,
            settings=Settings(allow_reset=True),
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


def add_item_to_chroma_db(collection, item, metadata, id_num):
    """Function which adds/stores items to the Chroma DB
    """
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
    results = collection.query(
        query_texts=[query],
        n_results=5,
        include=['documents', 'metadatas', 'distances']
    )

    final_retrival = "\n\n".join(results['documents'][0])
    return final_retrival


def get_chroma_client():
    """
    Function which creates or gets the Chroma DB from disk
    """
    if os.path.exists('/Users/mawuliagamah/utilities/chroma/chroma.sqlite3'):
        print("DB already exists")
        client = chromadb.PersistentClient(
            path='/Users/mawuliagamah/utilities/chroma')

    else:
        print("Making new client")
        client = chromadb.PersistentClient(
            path='/Users/mawuliagamah/utilities/chroma',
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )

    return client
