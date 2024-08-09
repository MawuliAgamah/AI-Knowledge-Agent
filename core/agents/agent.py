from langchain_openai import ChatOpenAI
from langchain_core.messages import (
        AIMessage,
        BaseMessage,
        FunctionMessage,
        HumanMessage,
        SystemMessage,
        ToolMessage
)


class AgentConfig:
    chat_model:str = None
    api_key = None



class Agent:


    def __init__(self,config):
        self.config = config 



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

        tools = {
            "agent_calling" : None,
            "database_query" : None,
            "internet_search":None
            }

        pass 


 
    def main(self,tasks,prompt):
        # Though loop : 
        while True:
            pass 
         



from prompts.prompt import BroadUserPrompt

if __name__=='__main__':
        
        agent = Agent(config = AgentConfig)
        
        agent.main(prompt = BroadUserPrompt)