
from agents.document_agent import DocumentAgent 


from Document import (
    DocumentPipeline , 
    DocumentBuilder
    )


from config.config import llm_config

from VectorDataBase import (
    DataBaseHandler, 
    DataBase as VectorDb
)

import utils.chroma_utils as chroma_utils  

from langchain_openai import ChatOpenAI

if __name__ == '__main__':

    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"
    document_builder = DocumentBuilder()

    document_agent = DocumentAgent(config=llm_config,llm = ChatOpenAI) # Instantiate the document agent with the configuration
    
    pipeline = DocumentPipeline(document_builder = document_builder ,llm = document_agent) # Instanstiate a document pipeline with a docment builder and the
    document_object = pipeline.build_document(path_to_document = path) # Create a document object for a single document 

    print(document_object.contents)
    
    chorma_client = chroma_utils.get_client(path = '/Users/mawuliagamah/gitprojects/STAR/db/chroma/chroma.sqlite3')
    database = DataBaseHandler(database = VectorDb(), client = chorma_client)

    database.add_document(document_object,collection="word_document",doc_type = "docx")
    database.show_contents()



    #database.query("query")

    #database.embed(document_object,embedding_model = embedding_model)
    
    #query_pipeline = QueryPipeline(query = Query, database = database, agents = agents)

    # We now want to 


    # SandBox(document_agent,query_agent,planner_agents)

    # Work station API which we can then use in a DJANGO application 
    #work_station = WorkStation()
    #work_station.inject_document("path")
    #work_station.enhance(query = "query")