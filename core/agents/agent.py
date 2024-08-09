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


from langchain_core.pydantic_v1 import ( 
    BaseModel, 
    Field
    )

from typing import List 

class Task(BaseModel):
    """
    Schema for an individual task.
    """
    task_id: int = Field(description="Number to identify the task")
    description: str = Field(description="Description of the task required to complete the action")


class OutputFormat(BaseModel):
    """
    Output schema for the agent. 
    The agent takes in a prompt and returns a list of tasks related to the problem.
    """
    tasks: List[Task] = Field(description="A list of tasks required to complete the action")


Prompt_message = ChatPromptTemplate.from_messages([
    ("system", """
    You are a component of an AI system, specifically designed to generate task plans for other AI agents within the system. Your primary function is to allocate and assign tasks to these agents based on the user's input to effectively accomplish the user's request.
    
    You have access to the following tools:
    - **Agent Calling**: Utilize this to delegate tasks or communicate with other AI agents.
    - **Database Query**: Use this tool to retrieve or store information in a database.
    - **Internet Search**: Leverage this tool to gather information from the web.

    Think of yourself as the central planner, coordinating the efforts of multiple AI agents.

    Your output should be a structured dictionary, where each key-value pair represents a specific task allocated to an AI agent, including which tool to use. The format of the output should adhere to the specified format instructions: {format_instructions}.
    """),
    ("human", "{prompt}")
])

import json 
class TaskCreationAgent:
    def __init__(self,config,llm):
        self.config = config 
        self.llm = llm
        self.model = "gpt-3.5-turbo"
        self.persona = None
        self.thoughts = None

    def _react_task_planning(self):
         pass
    
    def _sequential_task_planning(self):
         pass 

    def memory(self):
         pass 
    
    def _set_persona(self):
         """ Set the role and personality of the agents. 
         Set the tools the agent has accesss to.
         
         """

    def use_tool(self):
        """
        Agent has access to a set of tools it can use.
        This dictionairy contains all the tools, and the agent decides which to use
        To complete it's task.
        """
        
        tools = {
            "agent_calling" : None,
            "database_query" : None,
            "internet_search":None
            }

        pass 


 
    def main(self,user_prompt):
        
        # LLM Agent to take in the prompt and determine a lists of tasks which are then run in the main loop
        parser = JsonOutputParser(pydantic_object=OutputFormat)
        llm = self.llm(model = self.model, api_key = self.config['api_key'])
        chain = Prompt_message | llm | parser 
        
        to_do = chain.invoke({"prompt":user_prompt,"format_instructions":parser.get_format_instructions()})
        tasks = to_do['tasks']
        #to_do = json.loads(to_do)
        # Main loop to through through the agents tasks
        #while tasks: 
                # Run through the loop
        for task in tasks:
            print(task)





from config.config import config
from prompts.prompt import BroadUserPrompt


if __name__=='__main__':
        
        agent = TaskCreationAgent(config = config, llm = ChatOpenAI)
        
        agent.main(user_prompt= BroadUserPrompt)