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
     task_creating_prompt,
     task_execution_prompt,
)

from concurrent.futures import ThreadPoolExecutor



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
import tools 
class TaskCreationAgent:
     def __init__(self,config,llm):
        # agent config
        self.config = config 

        # model set up 
        self.llm = llm
        self.model = "gpt-3.5-turbo"

        # non-config vars 
        self.persona = None
        self.thoughts = {}
        self.tools = {
            "data_base_query_tool":tools.query_data_base,
            "write_to_system_tool":tools.write_to_file
            }

     def use_tool(self,tool_selected,tool_arguments):
          """
          Agent has access to a set of tools it can use.
          This dictionairy contains all the tools, and the agent decides which to use
          To complete it's task.
          """
          if tool_selected in self.tools:
               self.tools[tool_selected](tool_arguments)
          else:
            raise ValueError(f"Tool '{tool_selected}' is not available.")
 

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

     def execute_task(self,task,prompt,output_format):
         """After creating a set of tasks, the agent can then use tools to execute other tasks.
          For document writing i need the agent to be work properly and properly use tool.
         """
         # Plan for completing the taskl 
         
         # Use tool 
         


         return 

         
         
 
    
     def main(self,user_prompt):
          task_list = [user_prompt]

          print(f"\033[95m\033[1m"+"\n***** TASK LIST *****\n"+"\033[0m\033[0m")
          print(str(task_list[0]))
          # main loop 
          while True: 
               if task_list: # Check the task_list is not empty
                    for task in task_list: # iterate thought each task in the task list 
                         Thoughts = self.interpret_task(task  = task,output_format=interpretationFormat)
                         print(Thoughts)
                         agent_task_list = self.create_tasks(prompt = task, thought_string = Thoughts ,output_format=TaskOutputFormat)
                         #task_list = task_list.remove(task)
                         
                         #with ThreadPoolExecutor() as executor: # Agent is going to execute the tasks in parallel 
                         for agent_task in agent_task_list['tasks']:
                             print("\033[94m\033[1m" + f"TASK {agent_task['id']} : " + f"{agent_task['description']}" + "\033[0m")
                             #self.execute_task(task = agent_task['description'],prompt=)
                             #      print('Task : ',value)
                                   #future = executor.submit(self.execute_tasks(task), task, task_list, OBJECTIVE)
   
                         #result = self.execute_task(interpret_json)
                         print(f"\033[95m\033[1m"+"\n***** TASK COMPLETED, REMOVING TASKS *****\n"+"\033[0m\033[0m")
                         task_list = task_list.remove(task)
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
from prompts.prompt import init_prompt


if __name__=='__main__':
        
        agent = TaskCreationAgent(config = config, llm = ChatOpenAI)
        
        agent.main(user_prompt= init_prompt)