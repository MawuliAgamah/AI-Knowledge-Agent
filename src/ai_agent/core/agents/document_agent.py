"""Agent responsible for populating a document agent"""
import os
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core import prompts, output_parsers
from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from ai_agent.core.config.config import config, OllamaConfig , OpenAIConfig
from dotenv import load_dotenv

import asyncio
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
    
    async def doc_summary_by_map_reduce_async(self, llm, chunks):
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import asyncio
        import time
        start_time = time.time()

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
        semaphore = asyncio.Semaphore(10)
        async def process_chunk(chunk):
            async with semaphore:  # Rate limiting
                try:
                    return await map_chain.ainvoke({"text": chunk})
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    return None

        map_start_time = time.time()
        tasks = [process_chunk(chunk) for chunk in chunks]
        summaries = await asyncio.gather(*tasks)
        map_duration = time.time() - map_start_time
        print(f"✓ Map phase completed in {map_duration:.2f} seconds")

        summaries = [s for s in summaries if s is not None]

        # Combine summaries
        try:
            reduce_start_time = time.time()
            final_summary = await reduce_chain.ainvoke(
                {"summaries": "\n\n".join(summaries)}
            )
            reduce_duration = time.time() - reduce_start_time
            
            total_duration = time.time() - start_time
            print(f"✓ Document summary generated")
            print(f"Total execution time: {total_duration:.2f} seconds")
            print(f"Map phase: {map_duration:.2f} seconds")
            print(f"Reduce phase: {reduce_duration:.2f} seconds")
            return final_summary
        except Exception as e:
            print(f"Error in reduce step: {e}")
            return None

    async def doc_title_by_map_reduce_async(self, llm, chunks):
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import asyncio
        import time
        start_time = time.time()
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
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create the title of the document:
             """),
            ("human", """Synthesize these summaries of all the documents summaries of the document given to you into a single title of for the document.
        Summaries: {summaries}""")
        ])

        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()

        # Map: Generate individual summaries for each chunk
        semaphore = asyncio.Semaphore(10)
        async def process_chunk(chunk):
            async with semaphore:  # Rate limiting
                try:
                    return await map_chain.ainvoke({"text": chunk})
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    return None

        map_start_time = time.time()
        tasks = [process_chunk(chunk) for chunk in chunks]
        summaries = await asyncio.gather(*tasks)
        map_duration = time.time() - map_start_time
        print(f"✓ Map phase completed in {map_duration:.2f} seconds")

        summaries = [s for s in summaries if s is not None]

        # Combine summaries
        try:
            reduce_start_time = time.time()
            final_summary = await reduce_chain.ainvoke(
                {"summaries": "\n\n".join(summaries)}
            )
            reduce_duration = time.time() - reduce_start_time
            
            total_duration = time.time() - start_time
            print(f"✓ Document summary generated")
            print(f"Total execution time: {total_duration:.2f} seconds")
            print(f"Map phase: {map_duration:.2f} seconds")
            print(f"Reduce phase: {reduce_duration:.2f} seconds")
            return final_summary
        except Exception as e:
            print(f"Error in reduce step: {e}")
            return None


from typing import Optional
class DocumentAgent:
    """Class creates a large language model used within the document pipeline"""

    def __init__(self, config, model = None, llm = None, utils:Optional[DocumentAgentUtilities] = None):
        self.config = config
        self.utils = utils

    def generate_document_summary(self, chunks):
        summary = asyncio.run(self.utils.doc_summary_by_map_reduce_async(llm=self.config.llm, chunks=chunks)) # type: ignore
        console.print("[bold green]✓[/bold green] Document summary generated")
        return summary

    def generate_document_title(self,chunks):
        title = asyncio.run(self.utils.doc_title_by_map_reduce_async(llm=self.config.llm, chunks=chunks)) # type: ignore
        print(title)
        console.print("[bold green]✓[/bold green] Document Title generated")
        return title  
    
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
    config = OpenAIConfig() 
    doc_agent = DocumentAgent(config=config, utils=model_utils)

    path =   '/Users/mawuliagamah/obsidian vaults/Software Company/BookShelf/Books/The Art of Doing Science and Engineering.md'

    chunks = quick_doc_loader(path)

    # doc_agent.generate_document_summary(chunks)
    doc_agent.generate_document_title(chunks)
   


