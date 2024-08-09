import sys
sys.path.append("..") 

from log import logger

def planner_agent(prompt_template,output_format):
    import json 
    from openai import OpenAI
    import json

    client = OpenAI(api_key = 'sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')

    chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={"type":"json_object"},
            messages=[
                {"role":"system","content":
                """You are a part of a team of language models. 
                   Your role is this team is a leader, meaning you give the other models instructions. 
                   You must Provide your output in valid JSON. 
                   The data schema should in this format: """ +
                 json.dumps(output_format)},

                {"role":"user","content":prompt_template}
                ]
            )
        
    finish_reason = chat_completion.choices[0].finish_reason
    data = chat_completion.choices[0].message.content
    output = json.loads(data)
    return output

from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import JsonOutputParser
import os 

from langchain_core.pydantic_v1 import ( 
    BaseModel, 
    Field
    )

from typing import (
    List, 
    Optional
    )

from langchain_core.prompts import ChatPromptTemplate

meta_data_prompt = ChatPromptTemplate.from_messages([
    ("system","""The following is a part of a larger document.\n
        Extract the keywords, Tags and Questions on the chunk.\n
        Tags must start with a '#' and no list must be longer than 5 words.
        Format the document as so {format_instructions}"""),
    ("human","{chunk}")
])



# Define your desired data structure.
class MetaData(BaseModel):
    """
    
    """
    Keywords: list[str]  = Field(description="List of keywords related to the document. The maximum is 5 items.")
    Tags: list[str] = Field(description="List of tags related to the document, The maximum is 5 items.")
    Questions: list[str] = Field(description="List of questions which can be asked to query the document,The maximum is 5 items.")



class DocumentAgent:
    """
    Class creates a large language model used within the document pipeline

    attr
    ----
    config : dict
    dictionairy storing all of the configuration for the language model.
    """
    def __init__(self,config,llm):
        self.config = config
        self.model = "gpt-3.5-turbo"
        logger.info("Document Agent Initialised")
        self.llm = llm


    def map_reduce(self,map_prompt,reduce_prompt):
        pass

        #return map_reduce_output 

    def llm_chain(self,prompt):
        llm = self.llm(model = self.model, api_key = self.config['api_key'])
        output = LLMChain(prompt=prompt, llm=llm)
        logger.info(f"{output}")
        return output
    
    def make_metadata(self,chunk):
        parser = JsonOutputParser(pydantic_object=MetaData)
        llm = self.llm(model = self.model, api_key = self.config['api_key'])
        chain = meta_data_prompt | llm | parser 
        output = chain.invoke({"chunk":chunk,"format_instructions":parser.get_format_instructions()})
        # print(output)
        return output

