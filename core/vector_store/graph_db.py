# For OpenAI

import os
import sys
sys.path.append("..") 

import environment_setup as environment 

import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



from llama_index.core import KnowledgeGraphIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.graph_stores.nebula import NebulaGraphStore





# define LLM
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

from config import config

from llama_index.core import SimpleDirectoryReader
from llama_index.core import KnowledgeGraphIndex
from llama_index.core import Settings
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import StorageContext
from llama_index.llms.openai import OpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from pyvis.network import Network


import nest_asyncio

nest_asyncio.apply()
# Set up nebula db 


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



def get_nebula_client():
    """
    Function to connect to and get the nebula db client to allow you to write queries to the graph db 
    """
    client = None
    try:
        config = Config()
        config.max_connection_pool_size = 2

        # init connection pool
        connection_pool = ConnectionPool()

        assert connection_pool.init([("0.0.0.0", 9669)], config)
        

        # get session from the pool
        client = connection_pool.get_session("root", "nebula")
        assert client is not None

        # get the result in json format
        resp_json = client.execute_json("yield 1")
        json_obj = json.loads(resp_json)
        print(json.dumps(json_obj, indent=2, sort_keys=True))
        return client 

    except Exception:
        import traceback

        print(traceback.format_exc())
        if client is not None:
            client.release()
        exit(1)


def nebula_configure_space(space_name:str,client):
    """Create a space on nebula and create nodes,edges and relationships."""
    # create a space 
    client.execute(f"CREATE SPACE IF NOT EXISTS `{space_name}` (vid_type=FIXED_STRING(256), partition_num=1);")
    client.execute(f"USE {space_name};")
    client.execute("CREATE EDGE IF NOT EXISTS relationship(relationship string);")
    client.execute("CREATE TAG IF NOT EXISTS entity(name string)")
    print("NEBULA DB : query executed")
            


def setup_db(embedding_model,token):
    HuggingFaceInferenceAPIEmbeddings = embedding_model
    HF_TOKEN = token

    embed_model = LangchainEmbedding(
    HuggingFaceInferenceAPIEmbeddings(api_key=HF_TOKEN,model_name="thenlper/gte-large"))


def construct_knowledge_graph_index(llm):
     #setup the service context (global setting of LLM)
    Settings.llm = llm
    Settings.chunk_size = 512

    #setup the storage context
    graph_store = SimpleGraphStore()
    storage_context = StorageContext.from_defaults(graph_store=graph_store)

    #Construct the Knowlege Graph Undex
    index = KnowledgeGraphIndex.from_documents( documents=documents,
                                            max_triplets_per_chunk=3,
                                            storage_context=storage_context,
                                            embed_model=embed_model,
                                            include_embeddings=True)


def query(data,prompt):
      pass



if __name__=='__main__':
        # set up the environment variables
        environment.setup_env_vars()

        # get a client to allow running queries to nebula db 
        client = get_nebula_client()
        nebula_configure_space(space_name="STAR",client=client)

    
        #query(user_prompt= task)
