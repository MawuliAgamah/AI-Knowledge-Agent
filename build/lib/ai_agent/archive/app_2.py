import os
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain import PromptTemplate

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


loader = PyPDFLoader(
    "/Users/mawuliagamah/gitprojects/langchain/data/CS_Behaviours_2018.pdf")
documents = loader.load()

# Split the data into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
documents = text_splitter.split_documents(documents)


vectordb = Chroma.from_documents(
    documents, embedding=OpenAIEmbeddings(openai_api_key=api_key), persist_directory='./db')
vectordb.persist()  # Save the data to the disk

qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectordb.as_retriever(search_kwargs={'k': 7}),
    return_source_documents=True
)


# Create a prompt template

template = """Answer the question based on the context below. If the
question cannot be answered using the information provided answer
with "I don't know".

Context: Large Language Models (LLMs) are the latest models used in NLP.
Their superior performance over smaller models has made them incredibly
useful for developers building NLP enabled applications. These models
can be accessed via Hugging Face's `transformers` library, via OpenAI
using the `openai` library, and via Cohere using the `cohere` library.

Question: {query}

Answer: """

prompt_template = PromptTemplate(
    input_variables=["query"],
    template=template)


def main():
    # we can now execute queries against our Q&A chain
    result = qa_chain({'query': 'Based on this,how do i write my cv.'})
    parsed_result = result['result']
    return print(parsed_result)


if __name__ == "__main__":
    main()
