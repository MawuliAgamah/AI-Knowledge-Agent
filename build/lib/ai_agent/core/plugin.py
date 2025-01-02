from .utils.chroma_utils import get_chroma_client


class Agent:

    def __init__(self):
        client = None

    def set_up_chroma():
        client = get_chroma_client()

    def embed_document(self, document):
        client = get_chroma_client()
        print(client)
        # Can we get this to run in parallel?
        # okayyy
        print(document)
