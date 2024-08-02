
import os 
import glob 
import logging

logging.basicConfig(filename='../logging/extract-log.txt', level=logging.INFO)
logging.basicConfig(filename='../logging/extract-error-log.txt', level=logging.ERROR)


from agents.document_agent import DocumentAgent
from config import config

# Import Langchain 
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


# Define all imports which are used by the class below 
from prompts.document_prompts import map_template,reduce_template  
from langchain.prompts import PromptTemplate
from langchain.chains import MapReduceDocumentsChain,ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

class DocumentBuilder:
    """
    Class that handles all tasks involved in constructing a document.
    loading, pre-processing, summarisation

    attr
    ----
    """
    def __init__(self):
        self.name = "word document builder" 

    
    def init(self,path):
        """
        initialises the document object setting the documents path attribute as the path.
        """
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
        page_contents = document_object.get_contents(contents = "page_contents") # Get page contents from the document object 
        page_contents = page_contents.lower()  # Make page contents lower case   
        stemmer = PorterStemmer() # Create stemmer
        lemmertizer = WordNetLemmatizer() # instantiate lemmertizer
        page_contents = ' '.join(lemmertizer.lemmatize(token) for token in nltk.word_tokenize(page_contents)) # Lemmertize 
        page_contents = remove_stopwords(page_contents) #  remove stop words 
        document_object = document_object.update(contents = "page_content", payload = page_contents) # Update the page contents of the documnet 
        logging.info("Document Pre-Processed") # Log on completion 
        return document_object  
    
    def chunk_document(self,document_object):
        """
        Chunks document into pieces

        params
        ------
        document_objecct : object
        """
        pass 


    def inject_summary(self,document_object,llm):
        """
        Generate a summary of the document using language model.

        params
        ------
        document_object : object
        document object which stores a document, and related meta data.

        llm : object
        language model used to summarise the document.

        returns
        ------
        The document object.
        """
        # Get contents of document and chunk it.
        docoument = document_object.get_contents("document") # Get the contents of the document contents from the document. This is a langchain document object.
        document = self.chunk_document(document=docoument) # Split the text of the document into chunks.

        # Implements map reduce using langchain
        map_prompt = PromptTemplate.from_template(map_template)
        map_chain = llm(prompt = map_prompt)
        reduce_prompt = PromptTemplate.from_template(reduce_template)
        reduce_chain = llm(prompt = reduce_prompt)
        combine_documents_chain = StuffDocumentsChain(llm_chain= reduce_chain, document_variable_name="doc_summaries")
        reduce_documents_chain = ReduceDocumentsChain(combine_documents_chain = combine_documents_chain, collapse_documents_chain = combine_documents_chain)
        map_reduce_chain = MapReduceDocumentsChain(llm_chain=map_chain,document_variable_name="content",reduce_documents_chain=reduce_documents_chain)
        document_summary = map_reduce_chain.run(document)

        # Update the document summary with the generated summary
        document_object = document_object.update("summary", payload = document_summary)

        return document_object  

        

        return document_object



class DocumentPipeline:
    """
    Class that serves as a higher level orchestrator.
    Uses the document builder to perform a sequence of operations on a document object 
    in order to construct a document for insertion into a  vector database.

    attr
    ----
    document_builder : object

    llm : object
    
    """
    def __init__(self,document_builder,llm):
        self.document_builder = document_builder
        self.llm = llm

    def build_document(self,path_to_document):
        """
        Sequence of operations to build a full document given
        the path to the document on file.

        params
        ------
        path_to_document : str
        path to the document on file
        """
        document_template = self.document_builder.init(path = path_to_document)
        document = self.document_builder.load(document_object = document_template)
        document = self.document_builder.pre_process(document_object = document)
        document = self.document_builder.inject_summary(document_object = document , llm = self.llm) # Create the document summary using a language model 
        return document 







if __name__ == "__main__":
    
    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"

    document_builder = DocumentBuilder()
    document_agent = DocumentAgent(config=config)

    pipeline = DocumentPipeline(document_builder = document_builder ,llm = document_agent)
    document_object = pipeline.build_document(path_to_document = path)

    print(document_object.contents)
