"""


Author : Mawuli Agamah
Version : 0.1.0
License:

"""

from .utils.chroma_utils import get_chroma_client
from .document.document import (
    DocumentPipeline,
    DocumentBuilder
)

from .agents.document_agent import DocumentAgent


from .config import config


class AgentModule:
    """
    ...

    """

    def __init__(self):
        self.client = None
        self.docParser = None

    def set_up(self, path_to_vectordb, rag='vector'):
        """
        ...

        """
        if rag == 'vector':
            # set up vector database
            self.client = get_chroma_client(path_to_vectordb=path_to_vectordb)

            # set up document parsers
            document_builder = DocumentBuilder()
            document_agent = DocumentAgent(config=config)
            self.docParser = DocumentPipeline(
                document_builder=document_builder, llm=document_agent)
            return self
        else:
            return ValueError('Only Vector DB implemented')

    def parse_documument(self, document):
        """

        ...

        """
        pipeline = DocumentPipeline()
        for doc in document:
            pipeline.build_document(path_to_document=document)
            # Embed document here
