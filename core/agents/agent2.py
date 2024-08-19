import sys

sys.path.append("..") 

from log import logger 


from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
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
from prompts.prompt  import (
     Thought_prompt,
     Prompt_message,
     task_creating_prompt,
     task_execution_prompt,
)

from config.config import config

from prompts.agent.input_interpretation import interpretation_prompt
from prompts.agent.task_generation import task_generation_prompt
from prompts.agent.task_review import task_review_prompt


from concurrent.futures import ThreadPoolExecutor

MODEL = "gpt-3.5-turbo"
from prompts.user_prompt import task as OBJECTIVE
from prompts.agent.input_interpretation import interpretation_prompt



# Output structure for the language model agent 
from output_formats import (
     Task,
     TaskOutputFormat,
     Thought,
     Thoughts,
     Interpretation,
     interpretationFormat,
     ExecuteTaskFormat
)

import json 
import tools 


tools_dict = {"data_base_query_tool":tools.query_data_base, 
              "write_to_system_tool":tools.write_to_file
              }




def use_tool(tool_selected,tool_arguments):
          """
          Agent has access to a set of tools it can use.
          This dictionairy contains all the tools, and the agent decides which to use
          To complete it's task.
          """
          if tool_selected in tools_dict:
               tools_dict[tool_selected](tool_arguments)
          else:
            raise ValueError(f"Tool '{tool_selected}' is not available.")
 
def llm():
     llm = ChatOpenAI(model = MODEL, api_key = config['api_key'],temperature= 1.5)
     return llm 


def interpret_task(task):
    """
    Function which simulates the agent interpreting the task.
    This aims to simulate the agent thinking and reasoning about the task at hand.
    Before then breaking it down into sub tasks.

    args
    ----
    task : langchain prompt template of the users task

    returns :
    dictionairy

    """
    print(f"\033[95m\033[1m"+"\n***** Interpretation *****\n"+"\033[0m\033[0m")
    output_parser = JsonOutputParser(pydantic_object=interpretationFormat) # Create a pydantic output parser
    thought_chain = interpretation_prompt | llm() | output_parser # Create a chain which takes in the prompt, the model and output parser
    task_interpretation = thought_chain.invoke({"prompt":task,"format_instructions":output_parser.get_format_instructions()})
    
    thoughts = list()
    for key,value in task_interpretation.items():
        for i in value:
            thought_string = f"Agents thought {i['id']} : {i['analysis']} and further_questions {i['questions']}"
            thoughts.append(thought_string)
    
    thought_string = "\n".join(thoughts)
    return thought_string



def create_tasks(task):
     """This functions takes in the users query and breaks in down into a set of tasks to complete."""
     print(f"\033[95m\033[1m"+"\n***** Creating_tasks *****\n"+"\033[0m\033[0m")
     output_parser = JsonOutputParser(pydantic_object=TaskOutputFormat) # Create a pydantic output parser
     task_chain = task_generation_prompt | llm() | output_parser 
     # tasks = task_chain.invoke({"prompt":prompt,"thoughts":thought_string,"format_instructions":output_parser.get_format_instructions()})
     tasks = task_chain.invoke({"prompt":task,"format_instructions":output_parser.get_format_instructions()})

     return tasks




from output_formats import ReviewTask
def handle_task(task):
     """This functions takes in the agents list of tasks and reviews and improves upon them"""
     print(f"\033[95m\033[1m"+"\n***** REVEIWING TASKS *****\n"+"\033[0m\033[0m")
     output_parser = JsonOutputParser(pydantic_object=ReviewTask) # Create a pydantic output parser
     tool_chain = task_review_prompt | llm() | output_parser # Create a chain which takes in the prompt, the model and output parser
     prompt =  f"""You have been given the task of {task}. What improvements can be made to this task given the users objective : {OBJECTIVE} """
     review_of_task = tool_chain.invoke({"prompt":prompt,"format_instructions":output_parser.get_format_instructions()})

     print(review_of_task)



def execute_task(task,llm):
     """
     After creating a set of tasks, the agent can then use tools to execute other tasks.
     For document writing i need the agent to be work properly and properly use tool.
     """
     print(task)     
     output_parser = JsonOutputParser(pydantic_object=ExecuteTaskFormat) # Create a pydantic output parser
     tool_chain = task_execution_prompt | llm() | output_parser # Create a chain which takes in the prompt, the model and output parser
     tool_use = tool_chain.invoke({"prompt":task,"OBJECTIVE":OBJECTIVE,"format_instructions":output_parser.get_format_instructions()})
     # Use tool 
     for key,value in tool_use.items():
          print(value)


def run_agent(user_prompt):
          task_list = [user_prompt]

          print(f"\033[95m\033[1m"+"\n - - - - - TASK LIST - - - - - \n"+"\033[0m\033[0m")
          print(str(task_list[0]))
          # main loop 
          while True: 
               if task_list: # Check the task_list is not empty
                    for task in task_list: # iterate thought each task in the task list 
                         # Thoughts = interpret_task(task=task)
                         print(Thoughts)
                         agent_task_list = create_tasks(task = task)
                         #with ThreadPoolExecutor() as executor: # Agent is going to execute the tasks in parallel 
                         for agent_task in agent_task_list['tasks']:
                             print("\033[94m\033[1m" + f"TASK {agent_task['id']} : " + f"{agent_task['task']}" + "\033[0m")
                             for sub_task in agent_task['subtasks']:
                                  print("\033[92m\033[1m" + f"SUB-TASK {sub_task['id']} : " + f"{sub_task['sub_task']}" +"\033[0m")
                                  handle_task(task = sub_task['sub_task'])


                         print(f"\033[95m\033[1m"+"\n***** TASK COMPLETED, REMOVING TASKS *****\n"+"\033[0m\033[0m")
                         task_list = task_list.remove(task)
               else:
                    print(f"\033[95m\033[1m"+"\n***** NO TASKS LEFT *****\n"+"\033[0m\033[0m")
                    print("no tasks")
                    break 

if __name__=='__main__':
     
        run_agent(user_prompt= OBJECTIVE)