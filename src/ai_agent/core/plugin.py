"""


Author : Mawuli Agamah
Version : 0.1.0
License:

"""

from langchain_openai import ChatOpenAI
from utils.chroma_utils import get_client
from document.document import (
    DocumentPipeline,
    DocumentBuilder
)

from agents.document_agent import DocumentAgent
from config.config import config

from typing import List


class AgentModule:
    """
    ...
    """

    def __init__(self):
        self.client = None
        self.document_parser = None
        self.document_agent = None

    def set_up(self, path_to_vectordb, rag='vector'):
        """
        ...

        """
        if rag == 'vector':
            # ----------------------------------
            # initialise vector database
            # ----------------------------------
            self.client = get_client(path=path_to_vectordb)

            # ----------------------------------
            # initialise document agent
            # ----------------------------------

            self.document_agent = DocumentAgent(
                config=config,
                model="gpt-3.5-turbo",
                llm=ChatOpenAI
            )

            # ----------------------------------
            # initialise builder
            # ----------------------------------
            document_builder = DocumentBuilder()
            self.document_parser = (
                DocumentPipeline(
                    document_builder=document_builder,
                    llm=self.document_agent
                )
            )
            return self
        else:
            return ValueError('Only Vector DB implemented')

    def parse_document(self, path_to_document: List['str']):
        """

        ...

        """
        for doc in path_to_document:
            print(doc)
            document = self.document_parser.build_document(
                path_to_document=doc)
            print(document.contents['summary'])

        return self


def test():
    """
    ...
    """
    agent = AgentModule()
    path_to_note = [
        '/Users/mawuliagamah/obsidian vaults/Software Company/Learning/Machine Learning/Graph Neural Networks.md']

    agent = agent.set_up(
        path_to_vectordb='/Users/mawuliagamah/utilities/chroma')

    agent = agent.parse_document(path_to_document=path_to_note)


if __name__ == "__main__":
    test()
