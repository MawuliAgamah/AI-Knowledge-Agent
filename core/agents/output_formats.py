

from langchain_core.pydantic_v1 import ( 
    BaseModel, 
    Field
    )

from typing import List, Dict,Any


class ReviewTask(BaseModel):
    """
    Schema for task review and improvements
    """
#    review : str = Field(description= "Analysis and review of the task")
    review : str = Field(description= "Improvements to be made to the sub-task")
    improved_task : str = Field(description= "New version of the sub-task based on suggested improvements to be given to the next AI agent to execute.")



class SubTask(BaseModel):
    """
    Schema for sub-tasks 
    """
    id : int = Field(description = "sub task id")
    sub_task : str = Field(description= "description of the sub task to be completed")

class Task(BaseModel):
    """
    Schema for an individual task.
    """
    id: int = Field(description=" A unique number to identify the task")
    task: str = Field(description="Description of the task")
    subtasks : List[SubTask] = Field(description = "list of sub tasks to be completed")

class TaskOutputFormat(BaseModel):
    """
    Output schema for the agent. 
    The agent takes in a prompt and returns a list of tasks related to the problem.
    """
    tasks: List[Task] = Field(description="A list of indiviual tasks")

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


class Interpretation(BaseModel):
    """
    Schema for the model to review its own actions.
    """
    id: str = Field(description="A unique identifier for each analysis and reasoning block.")
    analysis: str = Field(description="A detailed review and analysis of the task the model was given, including an evaluation of its approach and outcome.")
    questions: str = Field(description="Any additional questions or clarifications needed to improve the model's performance or better understand the task.")


class interpretationFormat(BaseModel):
    """
    Output schema for a model to review its own actions 
    """
    thought : List[Interpretation] = Field(description="A list of at maxiumum 8 interprations")


class ExecuteTaskFormat(BaseModel):
    """
    Output format to task execution agent to use a tool
    """
    message : str | None = Field(
        description=(
            "The message to send t othe user. This can be none if a function to call has been provided"
        )
    )

    function : str | None = Field(
        description=(
            "The name of the function to call. This can be none if no functin call is required and a response is provided"
        )
    )
    arguments : dict[str,Any] | None = Field(
        description=(
            "The key is the name of the parameter and the value is the argument to pass to it. This can be none if no function call is required and a response is provided to pass to it. This can be none if no function call is required and a response is provided All parameters must be provided."
        )

    )


class BreakDownTask(BaseModel):
    """Schema outlining how an agent must break down a task"""
    task_breakdown : List[str] = Field(description= "Breakdown of the task handed to agent")