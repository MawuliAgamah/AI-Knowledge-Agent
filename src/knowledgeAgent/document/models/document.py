

class Document:
    def __init__(self, text: str, metadata: dict):
        self.text = text
        self.metadata = metadata
        self.chunks = []
        self.citations = []

    def __str__(self):
        return self.text