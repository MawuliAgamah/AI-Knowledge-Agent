"""Agent responsible for populating a document agent"""
import os
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core import prompts, output_parsers
from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from ai_agent.core.config.config import config, OllamaConfig
from dotenv import load_dotenv

from rich.console import Console


console = Console()

load_dotenv()


meta_data_prompt = prompts.ChatPromptTemplate.from_messages([
    ("system", """The following is a part of a larger document.\n
        Extract the keywords, Tags and Questions on the chunk.\n
        Tags must start with a '#' and no list must be longer than 5 words.
        Format the document as so {format_instructions}"""),
    ("human", "{chunk}")
])


# Define your desired data structure.
from pydantic import BaseModel, Field
from typing import List

class MetaData(BaseModel):
    """
    ...
    """
    Keywords: List[str] = Field(
        description="List of keywords related to the document. The maximum is 5 items.",
        max_length=5
    )
    
    Tags: List[str] = Field(
        description="List of tags related to the document. The maximum is 5 items.",
        max_length=5
    )
    
    Questions: List[str] = Field(
        description="List of questions which can be asked to query the document. The maximum is 5 items.",
        max_length=5
    )


class DocumentAgentUtilities:
    """Utiliy class for the Agent to use. Allows us to make the code base modular"""
    def __init__(self,) -> None:
        pass

    def doc_summary_by_map_reduce(self,llm,chunks):
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        
        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:

        Text: {text}

        Create a summary that:
        1. Preserves specific terminology and key phrases
        2. Maintains important context and relationships
        3. Captures actionable insights and recommendations
        4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that:
            - Maintains semantic richness for vector similarity matching
            - Preserves key terminology and specific details
            - Creates clear thematic connections
            - Structures information in a retrievable way"""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval:

        Summaries: {summaries}

        Create a final summary that:
        1. Preserves specific terminology and key concepts
        2. Maintains relationships between ideas
        3. Structures information in clear thematic sections
        4. Keeps concrete examples and specific details""")
        ])
        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()
        # Map: Generate individual summaries for each chunk
        summaries = []
        for chunk in chunks:
            summary = map_chain.invoke({"text": chunk})
            summaries.append(summary)
        
        # Reduce: Combine all summaries
        final_summary = reduce_chain.invoke({"summaries": "\n\n".join(summaries)})
        print(final_summary)
        print("✓ Document summary generated")
        return final_summary
    
    async def doc_summary_by_map_reduce_async(self,llm,chunks):
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import asyncio
        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:
        Text: {text}
        Create a summary that:
        1. Preserves specific terminology and key phrases
        2. Maintains important context and relationships
        3. Captures actionable insights and recommendations
        4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that:
            - Maintains semantic richness for vector similarity matching
            - Preserves key terminology and specific details
            - Creates clear thematic connections
            - Structures information in a retrievable way"""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval:
        Summaries: {summaries}
        Create a final summary that:
        1. Preserves specific terminology and key concepts
        2. Maintains relationships between ideas
        3. Structures information in clear thematic sections
        4. Keeps concrete examples and specific details.
        5. Ensure the summary is no longer that 2 sentences.""")
        ])
        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()
        # Map: Generate individual summaries for each chunk

        # Process chunk with error handling
        semaphore = asyncio.Semaphore(10)
        async def process_chunk(chunk):
            async with semaphore:  # Rate limiting
                try:
                    return await map_chain.ainvoke({"text": chunk})
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    return None
                
        tasks = [process_chunk(chunk) for chunk in chunks]
        summaries = await asyncio.gather(*tasks)

        summaries = [s for s in summaries if s is not None]
        
        # Combine summaries
        try:
            final_summary = await reduce_chain.ainvoke(
                {"summaries": "\n\n".join(summaries)}
            )
            print(final_summary)
            print("✓ Document summary generated")
            return final_summary
        except Exception as e:
            print(f"Error in reduce step: {e}")
            return None

    def doc_summary_by_map_reduce_thread_pool(self, llm, chunks):
        """Process Document using the ThreadPool Executor"""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from concurrent.futures import ProcessPoolExecutor,as_completed
        import multiprocessing
        import time
            
        print('threadpool map reduce')
        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """
             You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:

        Text: {text}

        Create a summary that:
        1. Preserves specific terminology and key phrases
        2. Maintains important context and relationships
        3. Captures actionable insights and recommendations
        4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that is 
             no longer than one sentence."""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval. Summaries: {summaries}s""")])
        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()
        # Map: Generate individual summaries for each chunk\

        def process_chunk(chunk):
            return map_chain.invoke({"text": chunk})

        start_time = time.time()
        cpu_count = multiprocessing.cpu_count()
        optimal_workers = cpu_count - 1 

        futures = []
       
        with ProcessPoolExecutor(max_workers=optimal_workers) as executor:
            for chunk in chunks:

                future = executor.submit(process_chunk, chunk)
                futures.append(future)
        
        summaries = []
        for future in as_completed(futures):
            try:
                result = future.result()
                summaries.append(result)
            except Exception as e:
                print(f"An error occurred: {e}")

        # Reduce: Combine all summaries
        final_summary = reduce_chain.invoke({"summaries": "\n\n".join(summaries)})
        print(f"Processing time: {time.time() - start_time:.2f} seconds")
        return final_summary


    def doc_summary_by_map_reduce_multiprocess(self, llm, chunks):
        """Process Document using Multiprocess"""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import multiprocess as mp
        import multiprocess.pool as mp_pool
        import time

        print('multiprocess map reduce')

        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:
            Text: {text}
            Create a summary that:
            1. Preserves specific terminology and key phrases
            2. Maintains important context and relationships
            3. Captures actionable insights and recommendations
            4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that is 
            no longer than one sentence."""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval. Summaries: {summaries}s""")
        ])

        # Create chains
        map_chain = map_prompt | llm | StrOutputParser()
        reduce_chain = reduce_prompt | llm | StrOutputParser()

        def process_chunk(chunk):
            return map_chain.invoke({"text": chunk})

        start_time = time.time()
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        optimal_workers = cpu_count - 1

        print(f'Using {optimal_workers} workers')
        
        # Using Pool instead of ProcessPoolExecutor
        with mp_pool.Pool(processes=optimal_workers) as pool:
            try:
                # Map phase - process all chunks
                results = pool.map_async(process_chunk, chunks)
                
                # Wait for all results and get them
                summaries = results.get()
                
                # Filter out any None results
                summaries = [s for s in summaries if s is not None]
                
                if not summaries:
                    raise ValueError("No valid summaries were generated")
                
                # Reduce phase
                final_summary = reduce_chain.invoke({"summaries": "\n\n".join(summaries)})
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                raise
            finally:
                pool.close()
                pool.join()

        print(f"Processing time: {time.time() - start_time:.2f} seconds")
        return final_summary

    

    def doc_summary_by_clustering(self,document):
        """Generates a document summary using the clustering method"""
        pass


from typing import Optional
class DocumentAgent:
    """Class creates a large language model used within the document pipeline"""

    def __init__(self, config, model = None, llm = None, utils:Optional[DocumentAgentUtilities] = None):
        self.config = config
        self.utils = utils

    def generate_document_summary(self,document_object):
        # self.utils.doc_summary_by_clustering(document_object) # type: ignore
        self.utils.doc_summary_by_map_reduce(llm = self.config.llm ,chunks=document_object) # type: ignore
    
    def generate_document_summary_threadpool(self, document_object):
        # summary = asyncio.run(self.utils.doc_summary_by_map_reduce_async(llm=self.config.llm, chunks=document_object)) # type: ignore
        summary = self.utils.doc_summary_by_map_reduce_multiprocess(llm=self.config.llm, chunks=document_object) # type: ignore 
        print(summary)
        console.print("[bold green]✓[/bold green] Document summary generated")
        return summary

    def generate_document_summary_old(self,document_object):
        # chunks = document_object.contents('chunks')
        self.utils.doc_summary_by_map_reduce(document_object,chunks) # type: ignore


    def generate_document_title(self,document_object):
        """Generate the documents title"""
        pass 


    def make_chunk_metadata(self, chunk):
        """
        Generate metadata for each chunk
        """
        parser = output_parsers.JsonOutputParser(pydantic_object=MetaData)
       
        chain = meta_data_prompt | self.config.llm | parser
        output = chain.invoke(
            {
                "chunk": chunk,
                "format_instructions": parser.get_format_instructions()}
        )
        return output



def quick_doc_loader(path):
    from langchain_community.document_loaders import UnstructuredMarkdownLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    # Load the document
    loader = UnstructuredMarkdownLoader(file_path=path)
    docs = loader.load()
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100  # Added some overlap for better context
    )
    
    # Split the documents - need to split documents, not text
    split_docs = text_splitter.split_documents(docs)
    
    return split_docs


if __name__ == "__main__":    
    model_utils = DocumentAgentUtilities()
    config = OllamaConfig() 
    doc_agent = DocumentAgent(config=config, utils=model_utils)

    path =   '/Users/mawuliagamah/obsidian vaults/Software Company/BookShelf/Books/The Art of Doing Science and Engineering.md'

    chunks = quick_doc_loader(path)

    doc_agent.generate_document_summary_threadpool(chunks)



# from pathlib import Path
# import logging
# from log import logger
# import sys

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
