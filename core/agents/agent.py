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



from prompts.agent.input_interpretation import interpretation_prompt
#from prompts.agent.task_generation import task_generation_prompt
#from prompts.agent.task_execution import task_execution_prompt


from concurrent.futures import ThreadPoolExecutor



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
        prompt : A prompt template
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
            
    
     def interpret_task(self,task):
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
          llm = self.llm(model = self.model, api_key = self.config['api_key'])
          # Create a chain which takes in the prompt, the model and output parser
          thought_chain = interpretation_prompt | llm | output_parser 
          task_interpretation = thought_chain.invoke({"prompt":task,"format_instructions":output_parser.get_format_instructions()})
          
          thoughts = list()
          for key,value in task_interpretation.items():
               for i in value:
                    thought_string = f"Agents thought {i['id']} : {i['analysis']} and further_questions {i['questions']}"
                    thoughts.append(thought_string)
          
          thought_string = "\n".join(thoughts)
          return thought_string
    
     def create_tasks(self,prompt,thought_string):
          print(f"\033[95m\033[1m"+"\n***** Creating_tasks *****\n"+"\033[0m\033[0m")
          
          from prompts.user_prompt import task as OBJECTIVE

          output_parser = JsonOutputParser(pydantic_object=TaskOutputFormat) # Create a pydantic output parser
          llm = self.llm(model = self.model, api_key = self.config['api_key'])
          task_chain = task_execution_prompt | llm | output_parser 
          tasks = task_chain.invoke({"prompt":prompt,"thoughts":thought_string,"format_instructions":output_parser.get_format_instructions()})
          
          return tasks

     def execute_task(self,task):
         """
         After creating a set of tasks, the agent can then use tools to execute other tasks.
         For document writing i need the agent to be work properly and properly use tool.
         """
         print(task)
         from prompts.agent.input_interpretation import interpretation_prompt
         from prompts.user_prompt import task as OBJECTIVE
         
         output_parser = JsonOutputParser(pydantic_object=ExecuteTaskFormat) # Create a pydantic output parser
         llm = self.llm(model = self.model, api_key = self.config['api_key'])
         # Create a chain which takes in the prompt, the model and output parser
         tool_chain = task_execution_prompt | llm | output_parser 
         tool_use = tool_chain.invoke({"prompt":task,"OBJECTIVE":OBJECTIVE,"format_instructions":output_parser.get_format_instructions()})

         # Use tool 
         for key,value in tool_use.items():
             print(value)
               


         
         
 
    
     def main(self,user_prompt):
          task_list = [user_prompt]

          print(f"\033[95m\033[1m"+"\n***** TASK LIST *****\n"+"\033[0m\033[0m")
          print(str(task_list[0]))
          # main loop 
          while True: 
               if task_list: # Check the task_list is not empty
                    for task in task_list: # iterate thought each task in the task list 
                         Thoughts = self.interpret_task(task=task)
                         
                         print(Thoughts)

                         agent_task_list = self.create_tasks(prompt = task, thought_string = Thoughts)
                        
                         
                         #with ThreadPoolExecutor() as executor: # Agent is going to execute the tasks in parallel 
                         for agent_task in agent_task_list['tasks']:
                             print("\033[94m\033[1m" + f"TASK {agent_task['id']} : " + f"{agent_task['description']}" + "\033[0m")
                             tools = self.execute_task(task = agent_task['description'])
                             print(tools)
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
from prompts.prompt import task


if __name__=='__main__':
        
        agent = TaskCreationAgent(config = config, llm = ChatOpenAI)
        
        agent.main(user_prompt= task)