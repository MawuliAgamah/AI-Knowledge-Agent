import os 
import glob 
import logging


# Create and configure logger
logging.basicConfig(filename='./extract-log.txt', level=logging.INFO)
logging.basicConfig(filename='./extract-error-log.txt', level=logging.ERROR)


from pathlib import Path
from dotenv import load_dotenv


load_dotenv(Path("/Users/mawuliagamah/gitprojects/STAR/.env"))

import nltk
from docx import Document as Doc
from gensim.parsing.preprocessing import remove_stopwords
from nltk.stem import *



from langchain.text_splitter import TokenTextSplitter
from langchain.chains import MapReduceDocumentsChain,ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain



from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter


from langchain_community.document_loaders import TextLoader


# ------------------------
from prompts.document_prompts import map_template,reduce_template  


from core.agents.document_agent import DocumentAgent



    
def load_documents(document_path):
    logging.info("Loading documents")

    documents = []
    for path in glob.glob(document_path):
        word_doc = Doc(path)
        documents.append(word_doc)
    return documents



def convert_to_plain_text(document,idx):
    fullText = []
    for para in document.paragraphs:
        fullText.append(para.text)
    fullText = '\n'.join(fullText)
    return fullText


# This uses langchain , will try my own implementation 
def split_document(document):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 5)
    chunks = text_splitter.split_documents(document)
    #print(chunks)
    return chunks 



def pre_process(document):
    document = document.lower()    
    stemmer = PorterStemmer()
    lemmertizer = WordNetLemmatizer()
    #document = ' '.join(stemmer.stem(token) for token in nltk.word_tokenize(document))
    document = ' '.join(lemmertizer.lemmatize(token) for token in nltk.word_tokenize(document))
    document = remove_stopwords(document)
    return document  



def load_document_lngchn(path):
    loader = Docx2txtLoader(path)
    doc = loader.load()
    return doc




def make_document(path):
    docoument = load_document_lngchn(path)
    document_template = {
    "id":None,
    "document": docoument,
    "summary": None,
    "metadata": {
        "path":path,
        "title":None,
        "Topic":None,
        "Filename":None,
        "document_type": None,
        "category": None,
    }}
    return document_template


def create_document_summary(document_object,llm):
    # path_to_document = document_object['metadata']['path']
    # Load the document here first 
    docoument = document_object['document']
    # Split the document into chunks 
    document = split_document(document=docoument)
    
    # LangChain Map Reduce
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(prompt=map_prompt, llm=llm)

    reduce_prompt = PromptTemplate.from_template(reduce_template)

    reduce_chain = LLMChain(prompt=reduce_prompt, llm=llm)

    combine_documents_chain = StuffDocumentsChain(llm_chain= reduce_chain, document_variable_name="doc_summaries")

    reduce_documents_chain = ReduceDocumentsChain(combine_documents_chain = combine_documents_chain, collapse_documents_chain = combine_documents_chain)
    map_reduce_chain = MapReduceDocumentsChain(llm_chain=map_chain,document_variable_name="content",reduce_documents_chain=reduce_documents_chain)
    
    document_summary = map_reduce_chain.run(document)
    document_object['summary'] = document_summary
    return document_object  


def create_document_summary(document_object,llm):


    # path_to_document = document_object['metadata']['path']
    # Load the document here first 
    docoument = document_object['document']
    # Split the document into chunks 
    document = split_document(document=docoument)
    
    # LangChain Map Reduce
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(prompt=map_prompt, llm=llm)

    reduce_prompt = PromptTemplate.from_template(reduce_template)

    reduce_chain = LLMChain(prompt=reduce_prompt, llm=llm)

    combine_documents_chain = StuffDocumentsChain(llm_chain= reduce_chain, document_variable_name="doc_summaries")

    reduce_documents_chain = ReduceDocumentsChain(combine_documents_chain = combine_documents_chain, collapse_documents_chain = combine_documents_chain)

    map_reduce_chain = MapReduceDocumentsChain(llm_chain=map_chain,document_variable_name="content",reduce_documents_chain=reduce_documents_chain)

    document_summary = map_reduce_chain.run(document)


    document_object['summary'] = document_summary

    return document_object  



def create_document_metadata(document):
    """Function to create the meta data for the document based on the summary of it """
    pass 



def document_processor(path):
    # Load documents and store them in a list ("Could be worth storing documents in a dictionary as such")
    # So we can begin to then incorperate document metadata 

    docs = load_documents(document_path=path)

    # Apply pre-processing to each of the documents we have 
    processed_documents = []
    for idx,doc in enumerate(docs):
        string = convert_to_plain_text(doc,idx)
        processed_string = pre_process(string)
        processed_documents.append(processed_string)


    """After doing some data cleaning , we will pass the document to the document summariser to produce meta data, a summary."""


    # Store documents to file as a txt.file and then load this into Lanchain 
    langchain_docs = []
    for idx,doc in enumerate(processed_documents):
        with open(f"/Users/mawuliagamah/gitprojects/STAR/data/documents/txt/processed_file_{idx}.txt", "w") as text_file:
           text_file.write(doc)
           loader = TextLoader(f"/Users/mawuliagamah/gitprojects/STAR/data/documents/txt/processed_file_{idx}.txt")
           data = loader.load()
           langchain_docs.append(data)

    # Return documents 
    return langchain_docs
    




""" We need a step before actually putting our document in the RAG database which allows us to 
    Do Analysis of the document. Summarise. Get The Metadata. We want to do some stuff before to enahnce 
    The Vector store stuff 

"""


from langchain_community.document_loaders import Docx2txtLoader

# The Document Class is concerned with building a docment 
class DocumentBuilder:
    def __init__self(self):
        self.name = "document builder" 
        
    def load_document_lngchn(path):
        loader = Docx2txtLoader(path)
        doc = loader.load()
        return doc


    def make_document(self):
        pass

    def chunk_document(self):
        self




class Document:
    def __init__(self,path,llm):
        self.document
        self.document_builder = DocumentBuilder()
        self.llm = llm


    def build(self,path):
        loaded_doc = self.document_builder.load_document()
        pass 


    def get_document():
        pass 






#llm = ChatOpenAI(model=model_name,api_key = os.environ.get('OPENAI_API_KEY'))
#model_name = "gpt-3.5-turbo"

if __name__ == "__main__":
    
    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"
    #llm = DocumentAgent()
    #document = Document(path = path, llm = llm )
    #document_object = document.build()

    model_name = "gpt-3.5-turbo"
    llm = ChatOpenAI(model=model_name,api_key = os.environ.get('OPENAI_API_KEY'))


    document_object = make_document(path)
    document_object = create_document_summary(document_object = document_object,llm = llm)
    document_object = create_document_metadata(document_object = document_object,llm = llm)


    print(document_object['summary'])
