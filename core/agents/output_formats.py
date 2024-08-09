

from langchain_core.pydantic_v1 import ( 
    BaseModel, 
    Field
    )

from typing import List


class Task(BaseModel):
    """
    Schema for an individual task.
    """
    id: int = Field(description=" A unique number to identify the task")
    description: str = Field(description="Description of the task required to complete the action")


class OutputFormat(BaseModel):
    """
    Output schema for the agent. 
    The agent takes in a prompt and returns a list of tasks related to the problem.
    """
    tasks: List[Task] = Field(description="A list of tasks required to complete the action")


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
    thought: List[Thought] = Field(description="A list of tasks required to complete the action")

