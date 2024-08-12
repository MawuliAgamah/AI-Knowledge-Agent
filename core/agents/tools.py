from langchain_core.pydantic_v1 import BaseModel,Field




from vector_store.vector_db import DataBasePipeline
database_pipeline = DataBasePipeline(reset_client=False)

def query_data_base(query):
    response = database_pipeline.query_data_base(query = query,collection_name = "word_documents")
    return response  


def write_to_file(file_name):
    pass