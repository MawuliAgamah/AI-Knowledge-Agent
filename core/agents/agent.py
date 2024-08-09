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


from prompts.prompt  import (
     Thought_prompt,
     Prompt_message
)

from typing import List 


# Output structure for the language model agent 

from output_formats import (
     Task,
     OutputFormat,
     Thought,
     Thoughts
)

import json 
class TaskCreationAgent:
    def __init__(self,config,llm):
        self.config = config 
        self.llm = llm
        self.model = "gpt-3.5-turbo"
        self.persona = None
        self.thoughts = {}

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

    def chat(self,prompt,output_format):
        """Function for the agent to interact with its internal llm.
        

        args
        ----
        prompt : 
        output_format : Pyndanditc object which instructs the model as to how 
        to ouput the 



        returns:
        Dictioniry


        
        """
        output_parser = JsonOutputParser(pydantic_object=output_format)
        llm = self.llm(model = self.model, api_key = self.config['api_key'])
        thought_chain = Thought_prompt | llm | output_parser 
        output = thought_chain.invoke({"prompt":prompt,"format_instructions":output_parser.get_format_instructions()})
        return output
         
 
    def main(self,user_prompt):
        
        # LLM Agent to take in the prompt and determine a lists of tasks which are then run in the main loop
        #parser = JsonOutputParser(pydantic_object=OutputFormat)
        llm = self.llm(model = self.model, api_key = self.config['api_key'])
        #chain = Prompt_message | llm | parser 
        #to_do = chain.invoke({"prompt":user_prompt,"format_instructions":parser.get_format_instructions()})
        #tasks = to_do['tasks']
        #to_do = json.loads(to_do)
        # Main loop to through through the agents tasks
        memory = []

        thought_parser = JsonOutputParser(pydantic_object=Thoughts)

        while len(memory) < 1: 
            
            thought_chain = Thought_prompt | llm | thought_parser 
            thoughts = thought_chain.invoke({"prompt":user_prompt,"format_instructions":thought_parser.get_format_instructions()})
            memory.append(thoughts['thought'])
            
            # Add this to the thought and then the language model will next review, make any corrections 
            # before then going to the next ate 
            self.thoughts['task'] = {
                 "id":thoughts['thought']['id'],
                  "Thought":thoughts['Thought']['thought'],
                  "Reaosoning":thoughts['Thought']['reasoning']}
            
            # Iterate through the models thoughts 
            for key,value in self.thoughts['task']:
                 
                 

            
        # We could then add all of the thoughts to the database as a memory? Then the model can use this as a sort of 
        # of long term meory?

        


            ##for i in thoughts:
              #   print(i)
              #   memory.append(i)






from config.config import config
from prompts.prompt import BroadUserPrompt


if __name__=='__main__':
        
        agent = TaskCreationAgent(config = config, llm = ChatOpenAI)
        
        agent.main(user_prompt= BroadUserPrompt)