"""To add



"""
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


import sys
if 1 == 1:
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from prompts.prompt import (
    Thought_prompt,
    Prompt_message,
    task_creating_prompt,
)
from config.config import config
from prompts.agent.input_interpretation import interpretation_prompt
from prompts.agent.task_generation import task_generation_prompt
from prompts.agent.task_review import task_review_prompt
from prompts.agent.task_execution import task_execution_prompt
from concurrent.futures import ThreadPoolExecutor
from prompts.user_prompt import task as OBJECTIVE
from .output_formats import (
    Task,
    TaskOutputFormat,
    Thought,
    Thoughts,
    Interpretation,
    interpretationFormat,
    ExecuteTaskFormat
)
from langchain.prompts import PromptTemplate
from output_formats import ReviewTask
from output_formats import ExecuteTaskFormat
import sys


# Import all prompts used throughout application


MODEL = "gpt-3.5-turbo"
# MODEL = "gpt-4o"


# Output structure for the language model agent

# import json
# from agents.tools import tools


# tools_dict = {"data_base_query_tool":tools.query_data_base,
#              "write_to_system_tool":tools.write_to_file}


# def use_tool(tool_selected,tool_arguments):
#          """
#          Agent has access to a set of tools it can use.
#          To complete it's task.
# This dictionairy contains all the tools, and the agent decides which to use
#          """
#          if tool_selected in tools_dict:
#          else:
# tools_dict[tool_selected](tool_arguments)
#            raise ValueError(f"Tool '{tool_selected}' is not available.")

def llm():
    """LLM
    """
    llm = ChatOpenAI(
        model=MODEL, api_key=config['api_key'],
        temperature=1.5, max_tokens=500)
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
    # Create a pydantic output parser
    output_parser = JsonOutputParser(pydantic_object=interpretationFormat)
    # Create a chain which takes in the prompt, the model and output parser
    thought_chain = interpretation_prompt | llm() | output_parser
    task_interpretation = thought_chain.invoke(
        {"prompt": task,
         "format_instructions": output_parser.get_format_instructions()
         })

    thoughts = list()
    for key, value in task_interpretation.items():
        for i in value:
            thought_string = f"Agents thought {i['id']} : {i['analysis']} and further_questions {i['questions']}"
            thoughts.append(thought_string)

    thought_string = "\n".join(thoughts)
    return thought_string


def create_tasks(task):
    """

    This functions takes in the users query and breaks in down into a 
    set of tasks to complete.
    """

    print("\033[95m\033[1m" +
          "\n - - - - -  Creating Tasks  - - - - - \n"
          + "\033[0m\033[0m")
    # Create a pydantic output parser
    output_parser = JsonOutputParser(pydantic_object=TaskOutputFormat)
    prompt = PromptTemplate(
        template=task_generation_prompt,
        input_variables=["OBJECTIVE"],
        partial_variables={
            "format_instructions": output_parser.get_format_instructions()}
    )
    ai = llm()
    task_chain = prompt | ai | output_parser
    tasks = task_chain.invoke({"OBJECTIVE": task})
    return tasks


def prompt(prompt_string, input_variables, output_format):
    # Create a pydantic output parser
    output_parser = JsonOutputParser(pydantic_object=output_format)
    prompt = PromptTemplate(
        template=task_review_prompt,
        input_variables=["TASK", "OBJECTIVE"],
        partial_variables={
            "format_instructions": output_parser.get_format_instructions()}
    )
    return prompt


def handle_task(task):
    """This functions takes in the agents list of tasks and reviews and improves upon them
    """
    print(f"\033[95m\033[1m" +
          "\n***** REVEIWING TASKS *****\n"+"\033[0m\033[0m")
    # Create a pydantic output parser
    output_parser = JsonOutputParser(pydantic_object=ReviewTask)
    prompt = PromptTemplate(
        template=task_review_prompt,
        input_variables=["TASK", "GLOBAL_OBJECTIVE"],
        partial_variables={
            "format_instructions": output_parser.get_format_instructions()}
    )
    ai = llm()
    # Create a chain which takes in the prompt, the model and output parser
    tool_chain = prompt | ai | output_parser
    review_of_task = tool_chain.invoke(
        {"TASK": task, "GLOBAL_OBJECTIVE": OBJECTIVE})

    return review_of_task['improved_task']


# from tools import *


def execute_task(task):
    """
    After creating a set of tasks, the agent can then use tools to execute other tasks.
    For document writing i need the agent to be work properly and properly use tool.
    """

    # Create a pydantic output parser
    output_parser = JsonOutputParser(pydantic_object=ExecuteTaskFormat)
    prompt = PromptTemplate(
        template=task_execution_prompt,
        input_variables=["TASK", "TOOLS", "OBJECTIVE"],
        partial_variables={
            "format_instructions": output_parser.get_format_instructions()}
    )
    ai = llm()
    # Create a chain which takes in the prompt, the model and output parser
    chain = prompt | ai | output_parser
    task_execution = chain.invoke(
        {"TASK": task, "TOOLS": TOOLS_DESCRIPTION, "OBJECTIVE": OBJECTIVE})

    print(task_execution)


def run_agent(user_prompt):
    task_list = [user_prompt]
    print(f"\033[95m\033[1m" +
          "\n - - - - - TASK LIST - - - - - \n"+"\033[0m\033[0m")
    print(str(task_list[0]))
    # main loop
    while True:
        if task_list:  # Check the task_list is not empty
            for task in task_list:  # iterate thought each task in the task list
                agent_task_list = create_tasks(task=task)
                print(agent_task_list)
                # with ThreadPoolExecutor() as executor:
                # Agent is going to execute the tasks in parallel
                for agent_task in agent_task_list['tasks']:
                    print(
                        "\033[94m\033[1m" + f"TASK {agent_task['id']} : " + f"{agent_task['task']}" + "\033[0m")
                    for sub_task in agent_task['subtasks']:
                        print(
                            "\033[92m\033[1m" + f"SUB-TASK {sub_task['id']} : " + f"{sub_task['sub_task']}" + "\033[0m")
                        refactored_task = handle_task(
                            task=sub_task['sub_task'])
                        execute_task(task=refactored_task)

                print(
                    f"\033[95m\033[1m"+"\n*- - - - - TASK COMPLETED , REMOVING TASK - - - - -\n"+"\033[0m\033[0m")
                task_list = task_list.remove(task)
        else:
            print(f"\033[95m\033[1m" +
                  "\n***** NO TASKS LEFT *****\n"+"\033[0m\033[0m")
            print("no tasks")
            break


if __name__ == '__main__':
    run_agent(user_prompt=OBJECTIVE)
