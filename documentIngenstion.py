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

def load_documents():
    documents = []
    for path in glob.glob("/Users/mawuliagamah/gitprojects/STAR/data/documents/word/*.docx"):
        documents.append(path)
        loader = Docx2txtLoader(path)
        data = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=100,chunk_overlap=20)
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



class TaskPlanner:
    
    """
    Takes query and breaks it down into sub queries 
    
    
    """
    def __init__(self,model):
        self.name = 'Planner'
        self.model = model 



    def decompose_task(self):
        from prompt import  UserPrompt
        
        template_string = f"""
        Analyze the following career development Here:

        {UserPrompt}

        Please provide a structured breakdown of this prompt into the following components:

        1. Main goal
        2. Available resources
        3. Specific tasks to be completed
        4. Desired outputs

        For each task, create a detailed sub-prompt that can be used as input for a language model. These sub-prompts should be actionable and focused on generating specific, relevant information.

        Ensure that the breakdown and sub-prompts cover all aspects of the original request while maintaining clarity and coherence.
        """


        return self.model.invoke(template_string).content

from langchain_core.pydantic_v1 import BaseModel,Field,validator
class Tasks(BaseModel):
    """Output structure for tasks """
    tasknumber:int = Field(description="The numeric ID of the task")
    task_description :int = Field(description="A descriotion of the task")





if __name__ == "__main__":
    from langchain.tools.retriever import create_retriever_tool
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    import os
    from langchain.output_parsers import MarkdownListOutputParser
    
    os.environ["OPENAI_API_KEY"] = 'sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b'
    model_name = "gpt-3.5-turbo"

    # Load all of the relevant documents into a vector DB
    documents = load_documents()
    retreiver = create_retreiver(documents)

    # Call the first language model 
    llm_planner = ChatOpenAI(model_name=model_name,openai_api_key='sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')
    planner_agent = TaskPlanner(model = llm_planner)
    task_breakdown = planner_agent.decompose_task()

    llm = ChatOpenAI(model_name=model_name,openai_api_key='sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')

    for task in task_breakdown:
        outputs = []
        result = query_documents(retreiver,llm,task)
        outputs.appemd(result)


    print(query_documents(retreiver,llm,task_breakdown))






    #documents = load_documents()
    #vector_database = store_documents_in_vector_store(documents)
    #query_documents(llm = llm, vectordb=vector_database, query=query)


