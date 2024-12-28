

import os
from langchain.chat_models import ChatOpenAI


class TaskPlanner:

    """
    Takes query and breaks it down into sub queries 


    """

    def __init__(self):
        self.name = 'Planner'

    def step_back(self):
        """Implements step back prompting """

    def decompose_task(self):
        from core.prompts.prompt import UserPrompt
        from openai import OpenAI
        import json

        prompt_template = f"""
        Analyze the following career development prompt:

        {UserPrompt}

        Please provide a structured breakdown of this prompt into smaller sub-tasks.

        For each sub-task, create a detailed sub-prompt that can be used as input by another language model to query a database to get relevant information. 
        
        Keep this in mind when generating prompts. 

        The output should be a JSON list of objects, each containing the following fields:
        - "task_number": The identifier for a task, for example "Task 1"
        - "task_description": A description of the task

        At the start of each tasks description, ensure you are reminding the LLM to consider the data at hand

        """

        example_json = {
            "tasks": [
                {
                    "tasknumber": "Task 1",
                    "task_description": "Identify specific technical and soft skills required for a Role"
                },
                {
                    "tasknumber": "Task 2",
                    "task_description": "Determine any gaps between current skillset and desired qualifications"
                },
                {
                    "tasknumber": "Task 3",
                    "task_description": "Recommend relevant courses, certifications, and training programs"
                },
                {
                    "tasknumber": "Task 4",
                    "task_description": "Prioritize learning objectives based on impact and time investment"
                },
                {
                    "tasknumber": "Task 5",
                    "task_description": "Outline key milestones and set realistic deadlines"
                }
            ]
        }

        client = OpenAI(
            api_key='sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Provide output in valid JSON. The data schema should in this format: " +
                    json.dumps(example_json)},
                {"role": "user", "content": prompt_template}
            ]
        )

        finish_reason = chat_completion.choices[0].finish_reason
        data = chat_completion.choices[0].message.content
        output = json.loads(data)
        return output


class Agent():
    def __init__(self, role, llm):
        self.role = role
        self.llm = llm
        self.key = os.environ.get('OPENAI_API_KEY')

    def get_llm(self):
        return self.llm()
