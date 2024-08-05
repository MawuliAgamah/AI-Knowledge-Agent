
from agents.document_agent import DocumentAgent 


from core.document.document import (
    DocumentPipeline , 
    DocumentBuilder
    )


from config.config import llm_config

from core.vector_store.vector_db import (
    DataBaseHandler, 
    DataBase as VectorDb
)

import utils.chroma_utils as chroma_utils  

from langchain_openai import ChatOpenAI

if __name__ == '__main__':

    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"
    document_builder = DocumentBuilder()

    """BLOCK 1"""
    document_agent = DocumentAgent( # Instantiate the document agent with the configuration
        config=llm_config,
        llm = ChatOpenAI
        ) 
    
    pipeline = DocumentPipeline( # Instanstiate a document pipeline with a docment builder and the
        document_builder = document_builder ,
        llm = document_agent
        ) 
    
    document_object = pipeline.build_document(path_to_document = path) # Create a document object for a single document 
    
    print(document_object.contents)
    
    """BLOCK 2"""
    # Turn this into a database pipeline

    chorma_client = chroma_utils.get_client(path = '/Users/mawuliagamah/gitprojects/STAR/db/chroma/chroma.sqlite3')
    
    # Create a vector database handler with the vector DB instanistated inside of this 
    db_handler = DataBaseHandler(database = VectorDb(), client = chorma_client)

    collection_name ="word_document" 

    db_handler = db_handler.add_document(document_object,collection_name=collection_name,doc_type = "docx")

    collection = db_handler.get_collection(collection_name = collection_name)

    index = db_handler.create_or_load_vector_store_index(chroma_collecion=collection)
    response = db_handler.search(index = index, query = "Tell me about data science")

    print(response)


    #database.query("query")

    #database.embed(document_object,embedding_model = embedding_model)
    
    #query_pipeline = QueryPipeline(query = Query, database = database, agents = agents)

    # We now want to 


    # SandBox(document_agent,query_agent,planner_agents)

    # Work station API which we can then use in a DJANGO application 
    #work_station = WorkStation()
    #work_station.inject_document("path")
    #work_station.enhance(query = "query")