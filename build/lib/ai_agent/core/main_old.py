import utils.chroma_utils as chroma_utils
from agents.document_agent import DocumentAgent
from langchain_openai import ChatOpenAI
from vector_store.vector_db import (
    DataBaseHandler,
    DataBase as VectorDb,
    DataBasePipeline
)
from document.document import (
    DocumentPipeline,
    DocumentBuilder
)
from config.config import config
from log import logger
import sys
sys.path.append("..")


# from agents.agent import(TaskCreationAgent)


if __name__ == '__main__':

    PATH = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"
    document_builder = DocumentBuilder()

    """BLOCK 1 : Document """
    document_agent = DocumentAgent(  # Instantiate doc agent with the configuration
        config=config,
        llm=ChatOpenAI
    )

    pipeline = DocumentPipeline(  # Instanstiate a document pipeline with a docment builder and the
        document_builder=document_builder,
        llm=document_agent
    )

    # Create a document object for a single document
    document_object = pipeline.build_document(path_to_document=path)

    """ BLOCK 2 : RAG """

    # Instantiate a database pipeline
    database_pipeline = DataBasePipeline(reset_client=True)

    database_pipeline = database_pipeline.add_document(
        document_object, collecton_name="word_documents", doc_type="docx")

    resonse = database_pipeline.query_data_base(
        query="What skills do i need for a data role?", collection_name="word_documents")

    # chorma_client = chroma_utils.get_client(path = '/Users/mawuliagamah/gitprojects/STAR/db/chroma/chroma.sqlite3')
    # chorma_client.reset()
    # Create a vector database handler with the vector DB instanistated inside of this
    # db_handler = DataBaseHandler(database = VectorDb(), client = chorma_client)

    # collection_name ="word_document"
    # db_handler = db_handler.add_document(document_object,collection=collection_name,doc_type = "docx")

    # collection = db_handler.get_collection(collection_name = collection_name)

    # index = db_handler.create_or_load_vector_store_index(chroma_collecion=collection)

    # response = db_handler.search(index = index, query = "What skills do i need to be a data scientist")

    print(resonse)

    """Front End"""

    #   database.query("query")

    #   database.embed(document_object,embedding_model = embedding_model)

    #   query_pipeline = QueryPipeline(query = Query, database = database, agents = agents)

    # We now want to

    # SandBox(document_agent,query_agent,planner_agents)

    # Work station API which we can then use in a DJANGO application
    # work_station = WorkStation()
    # work_station.inject_document("path")
    # work_station.enhance(query = "query")
