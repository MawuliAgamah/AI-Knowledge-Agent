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
     Prompt_message,
     task_creating_prompt
)



# Output structure for the language model agent 
from output_formats import (
     Task,
     TaskOutputFormat,
     Thought,
     Thoughts,
     Interpretation,
     interpretationFormat
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

     def chat(self,output_format,prompt_template = None,thoughts = None):
        """Function for the agent to interact with its internal llm.
        

        args
        ----
        prompt : 
        output_format : Pyndanditc object which instructs the model as to how 
        to ouput the 

        returns:
        Dictioniry

        """
        if thoughts == None:
          output_parser = JsonOutputParser(pydantic_object=output_format)
          llm = self.llm(model = self.model, api_key = self.config['api_key'])
          thought_chain = Thought_prompt | llm | output_parser 
          output = thought_chain.invoke({"prompt":prompt_template,"format_instructions":output_parser.get_format_instructions()})
          return output
        else:
          output_parser = JsonOutputParser(pydantic_object=output_format)
          llm = self.llm(model = self.model, api_key = self.config['api_key'])
          thought_chain = Thought_prompt | llm | output_parser 
          output = thought_chain.invoke({"prompt":thoughts,"format_instructions":output_parser.get_format_instructions()})
          return output
            
    
    
     def interpret_task(self,task,output_format):
          print(f"\033[95m\033[1m"+"\n***** Interpretation *****\n"+"\033[0m\033[0m")
          task_interpretation = self.chat(prompt_template=task,output_format = output_format)
        
          thoughts = list()
          for key,value in task_interpretation.items():
               for i in value:
                    thought_string = f" Thought {i['id']} : {i['analysis']} and the reasoning behind this is : {i['reasoning']}"
                    thoughts.append(thought_string)
          
          thought_string = "\n".join(thoughts)
          return thought_string
    
     def create_tasks(self,prompt,thought_string,output_format):
         print(f"\033[95m\033[1m"+"\n***** Creating_tasks *****\n"+"\033[0m\033[0m")
         tasks = self.chat(prompt_template = prompt,thoughts=thought_string,output_format = output_format)
         return tasks


         
         
 
    
     def main(self,user_prompt):
          task_list = [user_prompt]

          print(f"\033[95m\033[1m"+"\n***** TASK LIST *****\n"+"\033[0m\033[0m")
          print(str(task_list[0]))

          # main loop 
          while True: 
               if  task_list: # Check the task_list is not empty
                    for task in task_list: # iterate thought each task in the task list 
                         Thoughts = self.interpret_task(task  = task,output_format=interpretationFormat)
                         print(Thoughts)
                         tasks = self.create_tasks(prompt = task, thought_string = Thoughts ,output_format=TaskOutputFormat)
                         print(tasks)
                         task_list = task_list.remove(task)
                         result = self.execute_tasks(task)
                         #result = self.execute_task(interpret_json)
               else:
                    print(f"\033[95m\033[1m"+"\n***** NO TASKS LEFT *****\n"+"\033[0m\033[0m")
                    print("no tasks")
                    break 
                    #self.chat(prompt_template = , output_format= )
                    #thought_chain = Thought_prompt | llm | thought_parser 
                    #thoughts = thought_chain.invoke({"prompt":user_prompt,"format_instructions":thought_parser.get_format_instructions()})
                    #memory.append(thoughts['thought'])
               
               # Add this to the thought and then the language model will next review, make any corrections 
               # before then going to the next ate 
                #self.thoughts['task'] = {
                #  "id":thoughts['thought']['id'],
                #  "Thought":thoughts['Thought']['thought'],
                #  "Reaosoning":thoughts['Thought']['reasoning']}
            
            # Iterate through the models thoughts and it's reasoning and let the model analyse how good the it's approach is
            #for key,value in self.thoughts['task']:
            #      response = self.chat(prompt_template = , output_format= )
                 
                 

            
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