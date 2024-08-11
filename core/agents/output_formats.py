

from langchain_core.pydantic_v1 import ( 
    BaseModel, 
    Field
    )

from typing import List

#### Tasks 
class Task(BaseModel):
    """
    Schema for an individual task.
    """
    id: int = Field(description=" A unique number to identify the task")
    description: str = Field(description="Description of the sub-task required to complete the users objective.")

class TaskOutputFormat(BaseModel):
    """
    Output schema for the agent. 
    The agent takes in a prompt and returns a list of tasks related to the problem.
    """
    tasks: List[Task] = Field(description="A list of indiviual tasks")


# Thoughts 

class Thought(BaseModel):
    """
    Schema for an individual task.
    """
    id: int = Field(description="unique intiger which identifies the thought.")
    thought: str = Field(description="A 'thought', which describes the an agents 'thinking' to solve the problem")
    reasoning: str = Field(description="Explanation of WHY this approach was taken to solve the problem.")

class Thoughts(BaseModel):
    """
    Output schema for the agent. 
    The agent takes in a prompt and returns a list of tasks related to the problem.
    """
    thought: List[Thought] = Field(description="An array of thoughts detailing your reasoning, solution preparation, and next steps.")


# Interpret task 
class Interpretation(BaseModel):
    """
    Output schema for a model to review its own actions 
    """
    id : str = Field(description="unique intiger for analysis and reasoning block")
    analysis : str = Field(description="Your detailed review and analysis of the task given to you.")
    reasoning : str = Field(description="")


class interpretationFormat(BaseModel):
    """
    Output schema for a model to review its own actions 
    """
    thought : List[Interpretation] = Field(description="A list of at maxiumum 5 interprations")
