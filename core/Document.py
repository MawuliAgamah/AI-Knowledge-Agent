
import os 
import glob 
import logging

logging.basicConfig(filename='../logging/extract-log.txt', level=logging.INFO)
logging.basicConfig(filename='../logging/extract-error-log.txt', level=logging.ERROR)

from agents.document_agent import DocumentAgent
from config import config


from langchain_community.document_loaders import Docx2txtLoader


from gensim.parsing.preprocessing import remove_stopwords
import nltk
from nltk.stem import *



class Document:
    """The Document Object Class"""
    def __init__(self,path):
        self.contents = {
        "id":None,
        "path":path,
        "document": None,
        "summary": None,
        "metadata": {
            "title":None,
            "Topic":None,
            "Filename":None,
            "document_type": None,
            "category": None,
        }
        }

    
    def get_document(self):
        return self 

    def get_contents(self,contents):
        if contents == "document":
            return self.contents['document']
        elif contents == "path":
            return self.contents['path']
        elif contents == "summary":
            return self.contents['summary']
        elif contents == "page_contents":
            return self.contents['document'][0].page_content

    def update(self,contents,payload):
        if contents == "page_content":
            self.contents['document'][0].page_content = payload
            return self
        else:
            return ValueError('No implementation')


class DocumentBuilder:
    def __init__(self):
        self.name = "word document builder" 

    
    def init(self,path):
        document = Document(path = path)
        logging.info("Created document template")
        return document

    def load(self,document_object):
        """Load document into langchains data loader. Currently only handles Word Documents, Will deal with other cases """
        
        path_to_document = document_object.get_contents('path')

        loader = Docx2txtLoader(path_to_document)
        doc = loader.load()
        document_object.contents['document'] = doc

        logging.info("Document Loaded")
        return document_object
    
    def pre_process(self,document_object):
        
        # Get page contents from the document object 
        page_contents = document_object.get_contents(contents = "page_contents")
        # Make page contents lower case 
        page_contents = page_contents.lower()   
        
        stemmer = PorterStemmer()
        lemmertizer = WordNetLemmatizer()

        # Lemmertize and remove stop words 
        page_contents = ' '.join(lemmertizer.lemmatize(token) for token in nltk.word_tokenize(page_contents))
        page_contents = remove_stopwords(page_contents)

        # Update the page contents of the documnet 
        document_object = document_object.update(contents = "page_content", payload = page_contents)

        logging.info("Document Pre-Processed")
        return document_object  
    
    def chunk_document(self,dccument_object):
        pass 


    def summarise_document(self,document_object,llm):
        # Load document

        # Split Document into Chunks 


        return document_object



class DocumentPipeline():
    def __init__(self,document_builder,document_agent):
        self.document_builder = document_builder
        self.document_agent = document_agent


    
    def build_document(self,path_to_document):
        document_template = self.document_builder.init(path = path_to_document)
        document = self.document_builder.load(document_object = document_template)
        document = self.document_builder.pre_process(document_object = document)

        return document 







if __name__ == "__main__":
    
    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"

    document_builder = DocumentBuilder()
    document_agent = DocumentAgent(config=config)

    pipeline = DocumentPipeline(document_builder = document_builder ,document_agent = document_agent)
    document_object = pipeline.build_document(path_to_document = path)

    print(document_object.contents)
