from re import U
from langchain_experimental.graph_transformers import LLMGraphTransformer
from ai_agent.core.config.config import NebulaConfig

import json


from llama_index.core.query_engine import (
    KnowledgeGraphQueryEngine,
    RetrieverQueryEngine
)


from llama_index.core import (SimpleDirectoryReader,PropertyGraphIndex)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor



from ai_agent.core.log import setup_logger

logger = setup_logger()


from typing import Literal

import os
os.environ["NEBULA_ADDRESS"] = "0.0.0.0:9669"
os.environ["NEBULA_USER"] = "root"
os.environ["NEBULA_PASSWORD"] = "nebula"
# assumed we have NebulaGraph 3.5.0 or newer installed locally

entities = Literal[
   "CONCEPT",
   "TOPIC",
   "EXAMPLE",
   "REFERENCE",
   "EXPLANATION"
]

# Relationship types between entities
relations = Literal[
   "PREREQUISITES", 
   "BUILDS_ON",
   "SIMILAR_TO", 
   "CONTRASTS_WITH",
   "EXPLAINED_IN",
   "REFERENCED_BY", 
   "EXAMPLE_IN",
   "BELONGS_TO",
   "RELATES_TO"
]

# Schema defining valid relationships between entity types
schema = {
   "CONCEPT": [
       "PREREQUISITES",
       "BUILDS_ON", 
       "SIMILAR_TO",
       "CONTRASTS_WITH",
       "EXPLAINED_IN",
       "REFERENCED_BY",
       "EXAMPLE_IN",
       "BELONGS_TO",
       "RELATES_TO"
   ],
   "TOPIC": [
       "PREREQUISITES",
       "BUILDS_ON",
       "SIMILAR_TO", 
       "CONTRASTS_WITH",
       "EXPLAINED_IN",
       "BELONGS_TO",
       "RELATES_TO"
   ],
   "EXAMPLE": [
       "EXAMPLE_IN",
       "RELATES_TO",
       "BELONGS_TO"
   ],
   "REFERENCE": [
       "REFERENCED_BY",
       "RELATES_TO",
       "BELONGS_TO"
   ],
   "EXPLANATION": [
       "EXPLAINED_IN",
       "RELATES_TO",
       "BELONGS_TO"
   ]
}


class NebulaDB:
    def __init__(self,config):
        self.config = config

    def get_client(self):
        from nebula3.gclient.net.SessionPool import SessionPool
        from nebula3.gclient.net import Connection
        from nebula3.Config import (Config, SessionPoolConfig)
        from nebula3.common.ttypes import ErrorCode
        from nebula3.gclient.net import ConnectionPool
        """Function to connect to and get the nebula db client to allow you to write queries to the graph db"""
        client = None
        try:
            nebula_config = Config()
            nebula_config.max_connection_pool_size = 5
            # init connection pool
            connection_pool = ConnectionPool()
            ok = connection_pool.init([(self.config.adddress, 9669)], nebula_config)
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
    
    def create_graph_space(self,space_name):
        """Create a space on nebula and create nodes,edges and relationships."""
        from nebula3.Config import (Config, SessionPoolConfig)
        from nebula3.gclient.net import ConnectionPool
        config = Config()
        config.max_connection_pool_size = 5
        # init connection pool
        connection_pool = ConnectionPool()
        connection_pool.init([('0.0.0.0', 9669)], config)
        # get session from the pool
        # client = connection_pool.get_session("root", "nebula")
        # client.release()
        with connection_pool.session_context('root', 'nebula') as session:
            # create a space
            session.execute(f"CREATE SPACE IF NOT EXISTS `{space_name}` (vid_type=FIXED_STRING(256), partition_num=1);")
            session.execute(f"USE {space_name};")
            session.execute(
                "CREATE EDGE IF NOT EXISTS relationship(relationship string);")
            session.execute("CREATE TAG IF NOT EXISTS entity(name string)")
            logger.info(f"Space Generated : {space_name}")
        connection_pool.close()




class LlamaIndexKG:
    """Knowledge graph creation with llama index"""

    def __init__(self):
        pass


    
    def get_llm(self):
        from llama_index.llms.ollama import Ollama
        from llama_index.llms.openai import OpenAI
        #llm = OpenAI(model = 'gpt-3.5-turbo')
        llm = Ollama(model="tinyllama:latest", request_timeout=180.0,)
        return llm
    
    #def get_embedding_model(self):
    #    return 


    def get_embedding_model(self):
        pass

    def set_llama_index(self,llm, chunk_size):
        from llama_index.core import Settings
        Settings.llm = llm
        #Settings.embed_model = embedding_model
        Settings.chunk_size = chunk_size

    def get_document_from_file(self,path):
        document = SimpleDirectoryReader(input_dir=path).load_data()
        return document

    def get_graph_store(self,space_name,edge_types,rel_prop_names,tags=None):
        from llama_index.graph_stores.nebula import NebulaGraphStore
        # graph_store = NebulaGraphStore(
        #     space_name=space_name,
        #     edge_types=edge_types,
        #     rel_prop_names=rel_prop_names,
        #     tags=tags,
        #     supports_vector_queries=False  # Add this line
        # )
        from llama_index.graph_stores.nebula import NebulaPropertyGraphStore
       
        graph_store = NebulaPropertyGraphStore(space=space_name, overwrite=True)
        return graph_store
    
    def get_storage_context(self,space_name,graph_store):
        from llama_index.core import StorageContext
        return StorageContext.from_defaults(graph_store=graph_store)
    
    
    def construct_property_graph_index(self,llm,space_name,documents,
                                       graph_store,entities,relations,
                                        schema):
        from llama_index.core import PropertyGraphIndex
        from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
        from llama_index.core.vector_stores.simple import SimpleVectorStore
        
        kg_extractor = SchemaLLMPathExtractor(
            llm=llm,
            possible_entities=entities,
            possible_relations=relations,
            kg_validation_schema=schema,
            strict=True,
            num_workers=4,
            max_triplets_per_chunk=10,
        )
        index = PropertyGraphIndex.from_documents(
        documents,
        kg_extractors=[kg_extractor],
        property_graph_store=graph_store,
        show_progress=True)
        return index
        
    def load_property_graph_index(self):
        index = PropertyGraphIndex.from_existing(property_graph_store=graph_store)
        return index 



class GraphRag:
    def __init__(self):
        pass 






from ai_agent.core.document.sqldb import DocumentSQL 






if __name__ == '__main__':

    #########################
    # Set up nebula grap 
    #########################
    nebula_conf = NebulaConfig()
    nebula = NebulaDB(config = nebula_conf)
    nebula.create_graph_space(space_name = "Knowledge_Graph")



    #########################
    # Set up nebula grap 
    #########################

    llama_index_handler = LlamaIndexKG()

    graph_store = llama_index_handler.get_graph_store(
        space_name = 'Knowledge_Graph',
        edge_types = ["relationship"],
        rel_prop_names = ["relationship"])
    
    #storage_context = llama_index_handler.get_storage_context(
    #    space_name = 'Knowledge_Graph',
    #    graph_store = graph_store)
    
    llama_index_document= llama_index_handler.get_document_from_file(path = '/Users/mawuliagamah/obsidian vaults/Software Company/BookShelf/Books/')
    llm = llama_index_handler.get_llm()

    llama_index_handler.set_llama_index(llm=llm,chunk_size=512)

    index = llama_index_handler.construct_property_graph_index(
        llm = llm,
        documents = llama_index_document,
        space_name = 'Knowledge_Graph',
        graph_store = graph_store,
        entities = entities,
        relations = relations,
        schema = schema)

    query_engine = index.as_query_engine(
    include_text=True,   # include source chunk with matching paths
    similarity_top_k=3,  # top k for vector kg node retrieval
    )
    response = query_engine.query("What is this about?")
    print(response)




    #llama_index_docuemet = llama.get_document_from_file(path = '/Users/mawuliagamah/obsidian vaults/Software Company/BookShelf/Books/')
    #llama.co

    #config = NebulaConfig()
    #graph_db = NebulaDB(config=config) # type: ignore 
    

