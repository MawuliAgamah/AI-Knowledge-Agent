from langchain_core.pydantic_v1 import BaseModel,Field


TOOLS_DESCRIPTION = """
ool 1:

Name: data_base_query_tool
Arguments: Query (string)

Description:

The data_base_query_tool is designed to facilitate interactions with a graph database by allowing users to execute queries in natural language. The Query argument is a string that specifies the information you want to retrieve or analyze from the database. This tool interprets the query and extracts relevant data based on the user's request.

Examples:

Query: "Tell me about the user's past experiences."
Query: "What skills are required for the job they are applying for?"
This tool simplifies the process of querying the database, making it easy to access complex data with straightforward language.

"""

from vector_store.vector_db import DataBasePipeline
database_pipeline = DataBasePipeline(reset_client=False)

def query_data_base(query):
    response = database_pipeline.query_data_base(query = query,collection_name = "word_documents")
    return response  


def write_to_file(file_name):
    pass