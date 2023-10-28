import os
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
import streamlit as st
from PyPDF2 import PdfReader
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from htmlTemplates import css, bot_template, user_template

from dotenv import load_dotenv

load_dotenv()


def get_pdf_text(pdf_docs):
    text = ""
    # Read text from PDF and concatenate this to my text variable
    for pdf in pdf_docs:
        # Initialise PDF reader object
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            # Extract raw text from  that page of the PDF
            text += page.extract_text()  #  Append to our text string
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        # seperator="\n",
        chunk_size=5,
        chunk_overlap=3,
        length_function=len)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore_paid(text_chunks):
    print(text_chunks)
    embeddings = OpenAIEmbeddings()

    # vectorstore = FAISS.from_documents(text=text_chunks, embeddings=embeddings)

    return 1


def get_vectorstore_free(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_documents(text=text_chunks, embeddings=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retreiver(), memory=memory)
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.write(response)


def main():
    load_dotenv()
    st.set_page_config(page_title="docuTalk", page_icon="books")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    st.header("Upload PDF, Word Document and a blueprint")
    user_question = st.text_input("Ask a question: ")

    if user_question:
        handle_userinput(user_question)

    st.write(user_template.replace(
        "{{MSG}}", "Hi Chat Gpt"), unsafe_allow_html=True)
    st.write(bot_template.replace(
        "{{MSG}}", "Hello..."), unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Your documents")
        uploaded_docs = st.file_uploader(
            "Upload files", accept_multiple_files=True)

        if st.button("Process"):
            with st.spinner("Processing:"):
                # Get PDF Text
                # raw_text = get_pdf_text(uploaded_docs)
               # st.write(raw_text.__len__())
                # Get the Text Chunk
               # text_chunks = get_text_chunks(raw_text)
                # st.write(text_chunks)
                # Create Vector Store
                pass
               # vectorstore = get_vectorstore_paid(text_chunks)
            # Create conversation chain
                # st.session_state.conversation = get_conversation_chain(
                #    vectorstore)


if __name__ == "__main__":
    main()


# API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
# ENDPOINT = "https://api-inference.huggingface.co/models/<MODEL_ID>"
# headers = {"Authorization": "Bearer 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"}


# # def query(payload):
# #    response = requests.post(API_URL, headers=headers, json=payload)
# #    return response.json()


# # output = query({"inputs": "The answer to the universe is", })
# template = """ Question: {question}\n Answer: """
# # user question
# # question = "Which NFL team won the Super Bowl in the 2010 season?"
# # initialize Hub LLM
# hub_llm = HuggingFaceHub(repo_id='google/flan-t5-xxl')
# # create prompt template > LLM chain
# llm_chain = LLMChain.from_string(template=template, llm=hub_llm)


# def query(payload):
#     data = json.dumps(payload)
#     response = requests.request("POST", API_URL, headers=headers, data=data)
#     return json.loads(response.content.decode("utf-8"))


# # ask the user question about NFL 2010
# print(llm_chain.run(template))
