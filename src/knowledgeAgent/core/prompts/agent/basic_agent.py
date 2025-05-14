from langchain_core.prompts import ChatPromptTemplate


basic_agent_prompt = """
    ROLE
    - You are an AI system with the aim of helping the user write documents.
     
    OBJECTIVE

     OUTPUT FORMAT
     - The format of the your thoughts should adhere to the specified format instructions: {format_instructions}.

     THE TASK TO REVIEW:
     {OBJECTIVE}
"""


