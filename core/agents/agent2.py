from config.config import config
from prompts.prompt import task
        
from tools import tools      
tools = {"data_base_query_tool":tools.query_data_base,"write_to_system_tool":tools.write_to_file}




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


def run_agent(self,user_prompt):
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



if __name__=='__main__':
        

        run_agent(user_prompt= task)