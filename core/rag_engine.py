import os
import PyPDF2
import openai
import datetime
import glob 

                                                                                                                                                                                              
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(Path("/Users/mawuliagamah/gitprojects/STAR/.env"))

os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')
model_name = "gpt-3.5-turbo"

# Langchain imports 

from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools.retriever import create_retriever_tool

# Chroma imports 

import chromadb 
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from chromadb import Client as ChormaClient
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

import json 
from openai import OpenAI
import json

# My own utils 
from document_utils import load_documents, split_document


# Functions 

def query_documents(vectordb,llm,query):
    qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb(search_kwargs={'k': 12}),return_source_documents=True)
    result = qa_chain({"query": query})
    return  result["result"]





def planner_agent(prompt_template,output_format):
    import json 
    from openai import OpenAI
    import json

    client = OpenAI(api_key = 'sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')

    chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type":"json_object"},
            messages=[
                {"role":"system","content":
                """You are a part of a team of language models. 
                   Your role is this team is a leader, meaning you give the other models instructions. 
                   You must Provide your output in valid JSON. 
                   The data schema should in this format: """ +
                 json.dumps(output_format)},

                {"role":"user","content":prompt_template}
                ]
            )
        
    finish_reason = chat_completion.choices[0].finish_reason
    data = chat_completion.choices[0].message.content
    output = json.loads(data)
    return output
 
def worker_rag_agent(prompt, output_format):
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    system_message = """
    You are a specialized AI assistant working with a RAG (Retrieval-Augmented Generation) system. Your task is to use the provided query to retrieve relevant information from the database and synthesize it into a coherent response.

    Instructions:
    1. Analyze the given query in the context of retrieving information from a RAG database.
    2. Generate a specific, targeted database query that will retrieve the most relevant information.
    3. Consider both the user's current CV data and the target job descriptions in your query formulation.
    4. Provide a concise, actionable query that directly addresses the task at hand.
    5. Ensure your query is tailored to gather information that will help the user become a lead data scientist in the UK civil service within one year.

    Your response should be a clear, specific query string that can be used to interrogate the RAG database effectively.
    """

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        )
    
    data = chat_completion.choices[0].message.content
    return data









def rag_agent(prompt,output_format):
    pass 


def create_or_get_chromadb():
    # Check if the Chorma db and collection exyts 
    pass





def main():
    from core.prompts.prompt import  BroadUserPrompt, Planner_prompt  , example_json 
    from document_utils import document_processor


    
    # Load all of the relevant documents into a vector DB
    documents = document_processor(path ="/Users/mawuliagamah/gitprojects/STAR/data/documents/word/*.docx")

    # Chunk the documents 
    chunks_list =[]    
    for doc in documents:
        chunks = split_document(doc)
        chunks_list.append(chunks)


    embedding_function = OpenAIEmbeddingFunction(api_key= os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-ada-002")

    from chroma_utils import get_chroma_client,add_item_to_chroma_db

    chorma_client = get_chroma_client()
    chorma_client.delete_collection(name="word_documents")

    chroma_collection = chorma_client.get_or_create_collection(name = "word_documents" ,embedding_function = embedding_function)

    
    for chunk in chunks_list:
        for idx,item in enumerate(chunk):
            add_item_to_chroma_db( collection = chroma_collection, item = item.page_content, metadata = {"source":item.metadata['source']} , id_num=  str(idx) )

    
    
    planner_json_output = planner_agent(Planner_prompt,example_json)

    queries = []
    for task in planner_json_output['tasks']:

        #print("LLM Task : ", task['task_description'])

        output = worker_rag_agent(task['task_description'],"A string, no longer than 50 characters")
        queries.append(output)

    
    for idx,query in enumerate(queries):
        from chroma_utils import query_vector_db
        print(f"Input query [{idx+1}]: {query}")

        output = query_vector_db(query= query , collection = chroma_collection )


        print(f"Retrieved output [{idx+1}]:\n \n {output}\n")

    

