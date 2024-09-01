import sys

sys.path.append("..") 
from core.log import logger 


from langchain_openai import ChatOpenAI

from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import JsonOutputParser

from langchain_core.messages import (
        AIMessage,
        BaseMessage,
        FunctionMessage,
        HumanMessage,
        SystemMessage,
        ToolMessage
)

# Import all prompts used throughout application

from core.config.config import config

from core.prompts.agent.input_interpretation import interpretation_prompt
from core.prompts.agent.task_generation import task_generation_prompt
from core.prompts.agent.task_review import task_review_prompt
from core.prompts.agent.task_execution import task_execution_prompt
from core.prompts.agent.basic_agent import basic_agent_prompt

from concurrent.futures import ThreadPoolExecutor

MODEL = "gpt-3.5-turbo"
# MODEL = "gpt-4o"
from core.prompts.user_prompt import task as OBJECTIVE
from core.prompts.agent.input_interpretation import interpretation_prompt



# Output structure for the language model agent 
from core.agents.output_formats import (
     Task,
     TaskOutputFormat,
     Thought,
     Thoughts,
     Interpretation,
     interpretationFormat,
     ExecuteTaskFormat,
     BasicAgentOutputFormat
)

import json 

def llm():
     llm = ChatOpenAI(model = MODEL, api_key = config['api_key'],temperature= 1.5,max_tokens = 500)
     return llm 


def chat(user_prompt):
     """This functions takes in the users query and breaks in down into a set of tasks to complete."""
     print(f"\033[95m\033[1m"+"\n - - - - -  Creating Tasks  - - - - - \n"+"\033[0m\033[0m")
     output_parser = JsonOutputParser(pydantic_object=BasicAgentOutputFormat) # Create a pydantic output parser
     prompt = PromptTemplate(
            template=basic_agent_prompt,
            partial_variables={"format_instructions": output_parser.get_format_instructions()}
     )
     ai = llm() 
     task_chain = prompt | ai | output_parser 
     tasks = task_chain.invoke({"OBJECTIVE":user_prompt})
     return tasks



def run(user_prompt):
    print(f"\033[95m\033[1m"+"\n - - - - - USER INPUT - - - - - \n"+"\033[0m\033[0m")
    print(str(user_prompt))
    try:
        # main loop 
        model_response = chat(user_prompt)
        print(model_response)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        model_response = None
    return model_response 