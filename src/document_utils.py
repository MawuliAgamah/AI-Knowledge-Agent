from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
import glob 
from docx import Document as Doc
from gensim.parsing.preprocessing import remove_stopwords
from nltk.stem import *
import nltk
from langchain_community.document_loaders import TextLoader
# nltk.download('punkt')
# nltk.download('wordnet')


# ------------------------
from prompts.document_prompts import map_template,reduce_template  


# The Document Class is concerned with building a docment 
class Document:
    def __init__self(self):
        self.document = None
        self.summary = None 
        self.meta_data = {}
     






    
def load_documents(document_path):
    #print("#------------------------------------------ Meta Data ------------------------------------------ ")
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















from langchain_community.document_loaders import Docx2txtLoader
def load_document_lngchn(path):
    loader = Docx2txtLoader(path)
    doc = loader.load()
    return doc


from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path("/Users/mawuliagamah/gitprojects/STAR/.env"))


from langchain.text_splitter import TokenTextSplitter
from langchain.chains import MapReduceDocumentsChain,ReduceDocumentsChain

from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from dotenv import load_dotenv
import os 



def create_document_summary(path):

    # Load the document here first 
    docoument = load_document_lngchn(path)
    # Split the document into chunks 
    document = split_document(document=docoument)


    map_prompt = PromptTemplate.from_template(map_template)
    model_name = "gpt-3.5-turbo"
    llm = ChatOpenAI(
        model=model_name,
        api_key = os.environ.get('OPENAI_API_KEY')
        )
    
    map_chain = LLMChain(prompt=map_prompt, llm=llm)

    reduce_prompt = PromptTemplate.from_template(reduce_template)

    reduce_chain = LLMChain(prompt=reduce_prompt, llm=llm)

    combine_documents_chain = StuffDocumentsChain(llm_chain= reduce_chain, document_variable_name="doc_summaries")

    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain = combine_documents_chain,
        collapse_documents_chain = combine_documents_chain
    )

    map_reduce_chain = MapReduceDocumentsChain(
    llm_chain=map_chain,
    document_variable_name="content",
    reduce_documents_chain=reduce_documents_chain
    )

    """This takes in our docuemnt and produces a summary of it using map reducece"""


    document_summary = map_reduce_chain.run(document)

    return document_summary  

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

"""
"Each document will be stored in this sort of dictionairy object, in the future this will be a class which. 
Holds document instances, the attributes will be as below, and then the things we do to the "
document_tamplate = {
    "document":"DOCUMENT_OBJECT",
    "summary":"DOCUMENT_SUMMARY",
    "metadata":{
        "file_name":"file_name",
        "document_type":"word document",
        "Category":"abc",
    }
}

"""





if __name__ == "__main__":
    # path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/*.docx"
    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"
    document_summary = create_document_summary(path)
    print(document_summary)

    #document_processor(path)


