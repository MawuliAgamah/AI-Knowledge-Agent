"""Agent responsible for populating a document agent"""
import os
from typing import List


from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core import prompts, output_parsers, pydantic_v1
from langchain.chains.llm import LLMChain

from ai_agent.core.log import logger
from ai_agent.core.config.config import config
from dotenv import load_dotenv

from rich.console import Console
console = Console()


# from pathlib import Path
# import logging
# from log import logger
# import sys

load_dotenv()
# import sys
# sys.path.append("..")

# import os

# def planner_agent(prompt_template, output_format):
#    """
#    ...
#    """
#    import json
#    from openai import OpenAI
#
#    client = OpenAI(
#        api_key='sk-proj-I87WN2uvwnxuyV0AECrhT3BlbkFJPGP9mlimlM7NDpQITH6b')
#
#    chat_completion = client.chat.completions.create(
#        model="gpt-3.5-turbo-1106",
#        response_format={"type": "json_object"},
#        messages=[
#            {"role": "system", "content":
#             """You are a part of a team of language models.
#                   Your role is this team is a leader,
#                   meaning you give the other models instructions.
#                   You must Provide your output in valid JSON.
#                  The data schema should in this format: """ +
#             json.dumps(output_format)},
#
#            {"role": "user", "content": prompt_template}
#        ]
#    )

#     finish_reason = chat_completion.choices[0].finish_reason
#    data = chat_completion.choices[0].message.content
#    output = json.loads(data)
#    return output


meta_data_prompt = prompts.ChatPromptTemplate.from_messages([
    ("system", """The following is a part of a larger document.\n
        Extract the keywords, Tags and Questions on the chunk.\n
        Tags must start with a '#' and no list must be longer than 5 words.
        Format the document as so {format_instructions}"""),
    ("human", "{chunk}")
])


# Define your desired data structure.
class MetaData(pydantic_v1.BaseModel):
    """
    ...
    """
    Keywords: List[str] = pydantic_v1.Field(
        description="""List of keywords related to the document.
                       The maximum is 5 items.""")

    Tags: List[str] = pydantic_v1.Field(
        description="""List of tags related to the document,
                        The maximum is 5 items.""")
    Questions: List[str] = pydantic_v1.Field(
        description="""List of questions which can be
                       asked to query the document,The maximum is 5 items.
                        """)


class DocumentAgent:
    """
    Class creates a large language model used within the document pipeline

    attr
    ----
    config : dict
    dictionairy storing all of the configuration for the language model.
    """

    def __init__(self, config, model, llm):
        self.config = config
        self.model = model
        #self.llm = ChatOllama(model = self.model, api_key=os.getenv("OPENAI_API_KEY"))
        self.llm = ChatOllama(model = 'llama3.2:latest')
        logger.info("\033[1;37mDocument Agent Initialised\033[0m \n")

    # def map_reduce(self, map_prompt, reduce_prompt):
    #    """
    #    ...
    #    """
        # return map_reduce_output

    def llm_chain(self, prompt):
        """
        ..
        """
    
        # llm = self.llm(model=self.model, api_key=self.config['api_key'])
        llm =  self.llm
        output = LLMChain(prompt=prompt, llm=llm)
        logger.info(f"{output}")
        return output

    def generate_document_summary(self,document_object):
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate

        """
        Generate a summary of the document using language model.
        
        params
        ------
        document_object : object
            document object which stores a document, and related meta data.
        
        llm : object
            language model used to summarise the document.
        
        returns
        ------
        The document object.
        """
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate
        
        # Extract the actual LLM from the DocumentAgent
        actual_llm = self.llm
        
        # Create prompt template for summarization
        prompt = ChatPromptTemplate.from_template("Summarize this content: {context}")
    
        # Create the chain using the actual LLM
        chain = create_stuff_documents_chain(actual_llm, prompt)
        
        # Get the chunked document
        chunks = document_object.get_contents("chunked_document")
        
        try:
            # Generate summary using the chain - note the changed input format
            document_summary = chain.invoke({
                "context": chunks
            })
            
            # The result might be in a different format now, so let's handle that
            if isinstance(document_summary, dict):
                summary_text = document_summary.get('output', '')
            else:
                summary_text = str(document_summary)
            
            # Update the document summary
            document_object = document_object.update(
                "summary", payload=summary_text
            )
            
            console.print("[bold green]✓[/bold green] Document summary generated")
            return document_object
            
        except Exception as e:
            console.print(f"[bold red]Error generating summary: {str(e)}[/bold red]")
            raise


    def generate_document_title(self,document_object):
        """Generate the documents title"""
        pass 

    def make_chunk_metadata(self, chunk):
        """
        Generate metadata for each chunk
        """
        parser = output_parsers.JsonOutputParser(pydantic_object=MetaData)
       
        chain = meta_data_prompt | self.llm | parser
        output = chain.invoke(
            {
                "chunk": chunk,
                "format_instructions": parser.get_format_instructions()}
        )
        return output



# DocumentAgent(llm = ChatOpenAI)