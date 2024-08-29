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
from core.prompts.prompt  import (
     Thought_prompt,
     Prompt_message,
     task_creating_prompt,
)

from core.config.config import config

from core.prompts.agent.input_interpretation import interpretation_prompt
from core.prompts.agent.task_generation import task_generation_prompt
from core.prompts.agent.task_review import task_review_prompt
from core.prompts.agent.task_execution import task_execution_prompt

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
     ExecuteTaskFormat
)

import json 

def llm():
     llm = ChatOpenAI(model = MODEL, api_key = config['api_key'],temperature= 1.5,max_tokens = 500)
     return llm 


def chat(task):
     """This functions takes in the users query and breaks in down into a set of tasks to complete."""
     print(f"\033[95m\033[1m"+"\n - - - - -  Creating Tasks  - - - - - \n"+"\033[0m\033[0m")
     output_parser = JsonOutputParser(pydantic_object=TaskOutputFormat) # Create a pydantic output parser
     prompt = PromptTemplate(
            template=task_generation_prompt,
            input_variables=["OBJECTIVE"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()}
     )
     ai = llm() 
     task_chain = prompt | ai | output_parser 
     tasks = task_chain.invoke({"OBJECTIVE":task})
     return tasks



def run_agent(user_prompt):
          task_list = [user_prompt]
          print(f"\033[95m\033[1m"+"\n - - - - - TASK LIST - - - - - \n"+"\033[0m\033[0m")
          print(str(task_list[0]))
          # main loop 
          while True: 
               if task_list: # Check the task_list is not empty
                    for task in task_list: # iterate thought each task in the task list 
                         agent_task_list = chat(task = task)

                         task_list = task_list.remove(task)
               else:
                    print(f"\033[95m\033[1m"+"\n***** NO TASKS LEFT *****\n"+"\033[0m\033[0m")
                    print("no tasks")
                    break 