import os
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI


class DocumentHandler():
    def __init__(self):
        # Path to the document
        self.document_path = "/Users/mawuliagamah/gitprojects/langchain/data/CS_Behaviours_2018.pdf"

    def process_document(self):
        # Load document using py dpf loader
        loader = PyPDFLoader(self.document_path)
        document = loader.load()
        text_splitter = CharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)
        documents = text_splitter.split_documents(document)
        return documents


class VectorDBManager():
    def __init__(self, document):
        self.document = document
        self.db_directory = "/Users/mawuliagamah/gitprojects/langchain/data"
        self.vectordb = None

    def initialize_vectordb(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        self.vectordb = Chroma.from_documents(
            self.document,
            embedding=OpenAIEmbeddings(openai_api_key=api_key),
            persist_directory="/Users/mawuliagamah/gitprojects/langchain/data"
        )
        self.vectordb.persist()  # Save the data to the disk
        return (print("saved to f'{self.db_directory}"))

    def get_vectordb(self):
        if self.vectordb is None:
            raise ValueError(
                "VectorDB has not been initialized. Call initialize_vectordb first.")
        return self.vectordb


class Model():
    def __init__(self, vectordb_manager):
        self.vectordb_manager = vectordb_manager

    def chat(self, prompt):
        vectordb = self.vectordb_manager.get_vectordb()
        retriever = vectordb.as_retriever(search_kwargs={'k': 7})
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(),
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain({'query': prompt})
        return print(result['result'])


def main():

    document_handler = DocumentHandler()
    processed_documents = document_handler.process_document()
    vectordb_manager = VectorDBManager(processed_documents)
    vectordb_manager.initialize_vectordb()
    model = Model(vectordb_manager)
    response = model.chat(input("Ask me something : "))
    return response


if __name__ == "__main__":
    main()
