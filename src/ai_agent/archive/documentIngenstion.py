import os
import PyPDF2
import openai
import datetime
import glob 


from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from  langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings



from langchain_core.prompts import ChatPromptTemplate


############################################################
# Create classes 
############################################################

class doucmentLoader():
    def __init__(self):
        self.documents = None



    def load_documents(self):
        pass


    def semantic_text_splitter(self):
        pass 
        


def load_documents():
    documents = []
    for path in glob.glob("/Users/mawuliagamah/gitprojects/STAR/data/documents/word/*.docx"):
        documents.append(path)
        loader = Docx2txtLoader(path)
        data = loader.load()
        for data in data:
            print(data.metadata)
    
    text_splitter = CharacterTextSplitter(chunk_size=1000,chunk_overlap=5)
    documents = text_splitter.split_documents(data)

    return documents


def create_retreiver(documents):
    vectordb = Chroma.from_documents(documents,embedding=OpenAIEmbeddings(),persist_directory='./db')
    vectordb.persist() # Save the data to the disk
    return vectordb.as_retriever


def query_documents(vectordb,llm,query):
    qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb(search_kwargs={'k': 12}),return_source_documents=True)
    result = qa_chain({"query": query})
    return  result["result"]


#from langchain_core.pydantic_v1 import BaseModel,Field,validator
#class TaskPlannerOutput(BaseModel):
#    """Output structure for tasks"""
#    tasknumber: str = Field(description="The identifier for a task, for example Task1")
#    task_description: str = Field(description="A description of the task")


class TaskPlanner:
    
    """
    Takes query and breaks it down into sub queries 
    
    
    """
    def __init__(self):
        self.name = 'Planner'


    def step_back(self):
        """Implements step back prompting """



    def decompose_task(self):
        from core.prompts.prompt import  UserPrompt
        from openai import OpenAI
        import json

        prompt_template = f"""
        Analyze the following career development prompt:

        {UserPrompt}

        Please provide a structured breakdown of this prompt into smaller sub-tasks.

        For each sub-task, create a detailed sub-prompt that can be used as input by another language model to query a database to get relevant information. 
        
        Keep this in mind when generating prompts. 

        The output should be a JSON list of objects, each containing the following fields:
        - "task_number": The identifier for a task, for example "Task 1"
        - "task_description": A description of the task

        At the start of each tasks description, ensure you are reminding the LLM to consider the data at hand


        """

        example_json = {
            "tasks": [
                {
                    "tasknumber": "Task 1",
                    "task_description": "Identify specific technical and soft skills required for a Role"
                },
                {
                    "tasknumber": "Task 2",
                    "task_description": "Determine any gaps between current skillset and desired qualifications"
                },
                {
                    "tasknumber": "Task 3",
                    "task_description": "Recommend relevant courses, certifications, and training programs"
                },
                {
                    "tasknumber": "Task 4",
                    "task_description": "Prioritize learning objectives based on impact and time investment"
                },
                {
                    "tasknumber": "Task 5",
                    "task_description": "Outline key milestones and set realistic deadlines"
                }
            ]
        }

        client = OpenAI(api_key = 'sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')

        chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format={"type":"json_object"},
                messages=[
                    {"role":"system","content":"Provide output in valid JSON. The data schema should in this format: "+json.dumps(example_json)},
                    {"role":"user","content":prompt_template}
                ]
            )
        
        finish_reason = chat_completion.choices[0].finish_reason
        data = chat_completion.choices[0].message.content
        output = json.loads(data)

        return output





if __name__ == "__main__":
    from langchain.tools.retriever import create_retriever_tool
    from langchain.chat_models import ChatOpenAI
    import os

    
    os.environ["OPENAI_API_KEY"] = 'sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b'
    model_name = "gpt-3.5-turbo"

    # Load all of the relevant documents into a vector DB
    documents = load_documents()
    retreiver = create_retreiver(documents)


    # Create the task planning AI agent and ask it to decompose the task
    #planner_agent = TaskPlanner()
    #task_breakdown = planner_agent.decompose_task()


    #llm_executor = ChatOpenAI(model_name=model_name,openai_api_key='sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')



    #for tasks in task_breakdown['tasks']:
    #    print(tasks['task_description'])
    #    result = query_documents(llm =llm_executor ,vectordb=retreiver,query = tasks['task_description'])
    #    print("Executor : ",result)

