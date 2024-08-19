# For OpenAI

import os
import sys
sys.path.append("..") 

# from environment_setup import setup_env_vars
import environment_setup 
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



from llama_index.core import KnowledgeGraphIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.graph_stores.nebula import NebulaGraphStore

from config import config


from llama_index.llms.openai import OpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from pyvis.network import Network
    
from llama_index.core.query_engine import ( 
    KnowledgeGraphQueryEngine,
    RetrieverQueryEngine
    )

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from  llama_index.core  import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    KnowledgeGraphIndex,
    ServiceContext,
    StorageContext,
    load_index_from_storage
)
import nest_asyncio


# Environment variable set up 
from dotenv import load_dotenv
from pathlib import Path



from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

import json 
import time

from nebula_utils import print_resp

from nebula3.common.ttypes import ErrorCode
from nebula3.Config import SessionPoolConfig
from nebula3.gclient.net import Connection
from nebula3.gclient.net.SessionPool import SessionPool

# Set enviornment variables 

os.environ["NEBULA_USER"] = "root"
os.environ["NEBULA_PASSWORD"] = "nebula"  
os.environ["NEBULA_ADDRESS"] = "0.0.0.0:9669"  # assumed we have NebulaGraph 3.5.0 or newer installed locally

NEBULA_USER = 'root'
NEBULA_PASSWORD = 'nebula'
NEBULA_ADDRESS = '0.0.0.0'



def get_nebula_client():
    """Function to connect to and get the nebula db client to allow you to write queries to the graph db """
    client = None
    try:
        config = Config()
        config.max_connection_pool_size = 5
        # init connection pool
        connection_pool = ConnectionPool()
        ok = connection_pool.init([(NEBULA_ADDRESS, 9669)], config)
        # get session from the pool
        with connection_pool.session_context('root', 'nebula') as session:
            session.execute('USE STAR')
            session.execute('SHOW TAGS')
        connection_pool.close()
        
    except Exception:
        import traceback
        print(traceback.format_exc())
        if client is not None:
            client.release()
        exit(1)


def nebula_create_space(space_name:str):
    """Create a space on nebula and create nodes,edges and relationships."""
    
    config = Config()
    config.max_connection_pool_size = 5
    # init connection pool
    connection_pool = ConnectionPool()
    connection_pool.init([(NEBULA_ADDRESS, 9669)], config)
    # get session from the pool
    #client = connection_pool.get_session("root", "nebula")
    #client.release()
    with connection_pool.session_context('root', 'nebula') as session:
        # create a space 
        session.execute(f"CREATE SPACE IF NOT EXISTS `{space_name}` (vid_type=FIXED_STRING(256), partition_num=1);")
        session.execute(f"USE {space_name};")
        session.execute("CREATE EDGE IF NOT EXISTS relationship(relationship string);")
        session.execute("CREATE TAG IF NOT EXISTS entity(name string)")
        print("NEBULA DB : query executed")        
    connection_pool.close()


def get_storage_context(space_name):
    """Whats this doing?"""

    edge_types, rel_prop_names,tags = ["relationship"], ["relationship"],["entity"]

    graph_store = NebulaGraphStore(
    space_name=space_name,
    edge_types=edge_types,
    rel_prop_names=rel_prop_names,
    tags=tags,
    )
    storage_context = StorageContext.from_defaults(graph_store=graph_store)
    return storage_context

def get_document_from_file(file_path):
     document = SimpleDirectoryReader(input_dir = file_path).load_data()
     return document 

def construct_knowledge_graph_index(documents,storage_context,space_name,edge_types,rel_prop_names,tags):
    my_file = Path("/Users/mawuliagamah/gitprojects/STAR/data/graph/test/default__vector_store.json")
    if my_file.is_file():
        print("File exists:", my_file.is_file())
        storage = StorageContext.from_defaults(persist_dir=str(my_file.parent))
        kg_index = load_index_from_storage(storage)
        return kg_index
    else:
        print("Doesnt exists:", my_file.is_file())
        kg_index = KnowledgeGraphIndex.from_documents(
        documents,
        max_triplets_per_chunk=10,
        include_embeddings=True,
        )
        kg_index.storage_context.persist(persist_dir="/Users/mawuliagamah/gitprojects/STAR/data/graph/test/")
        return kg_index

def generate_query_engine(llm,storage_context):
    query_engine = KnowledgeGraphQueryEngine(
    storage_context=storage_context,
    llm=llm,
    verbose=True,
    )
    return query_engine


def lamma_index_set(llm,embedding_model,chunk_size):            
    Settings.llm = llm
    Settings.embed_model = embedding_model
    Settings.chunk_size = chunk_size


def get_edges_props_tags():
    edge_types, rel_prop_names,tags = ["relationship"],["relationship"],["entity"]
    return edge_types, rel_prop_names ,tags



if __name__=='__main__':

        lamma_index_set(llm = OpenAI(temperature=0, model="gpt-3.5-turbo-instruct"),embedding_model= OpenAIEmbedding(),chunk_size=514)
        nebula_create_space(space_name="STAR")
        storage_context = get_storage_context(space_name="STAR")
        edge_types, rel_prop_names,tags = get_edges_props_tags()
        document = get_document_from_file(file_path="/Users/mawuliagamah/gitprojects/STAR/data/documents/word")
        llm = OpenAI(temperature=0, model="gpt-3.5-turbo-instruct")
        service_context = ServiceContext.from_defaults(llm=llm, chunk_size=512)
        kg_index = construct_knowledge_graph_index(documents = document, space_name = "STAR",storage_context =  storage_context,edge_types = edge_types,tags= tags,rel_prop_names = rel_prop_names)
        query_engine = kg_index.as_query_engine()
        print(query_engine.query('What skills and experience does this person have?"'))

