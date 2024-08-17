# For OpenAI

import os


import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



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



def setup_db(embedding_model,token):
    HuggingFaceInferenceAPIEmbeddings = embedding_model
    HF_TOKEN = token

    embed_model = LangchainEmbedding(
    HuggingFaceInferenceAPIEmbeddings(api_key=HF_TOKEN,model_name="thenlper/gte-large"))



def construct_knowledge_graph_index():
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
      return result 



if __name__=='__main__':
        

    
        query(user_prompt= task)
