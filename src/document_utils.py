from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
import glob 
from docx import Document
from gensim.parsing.preprocessing import remove_stopwords
from nltk.stem import *
import nltk
# nltk.download('punkt')
# nltk.download('wordnet')

# The Document Class is concerned with building a docment 
class Document:
    pass 


def load_documents():
    """
    Langchain Data loader 
    """
    #print("#------------------------------------------ Meta Data ------------------------------------------ ")
    documents = []
    for path in glob.glob("/Users/mawuliagamah/gitprojects/STAR/data/documents/word/*.docx"):
        loader = Docx2txtLoader(path)
        data = loader.load()
        documents.append(data)

        #for doc in data:
        #    print(doc.metadata)
    #print("#------------------------------------------ Actual Data ------------------------------------------ ")
    #print(documents)
    
    return documents


    



def load_documents2(document_path):
    """
    Langchain Data loader 
    """
    #print("#------------------------------------------ Meta Data ------------------------------------------ ")
    documents = []
    for path in glob.glob(document_path):
        word_doc = Document(path)
        documents.append(word_doc)
    
    # Convert document into a single string 
    return documents

def convert_to_plain_text(document,idx):
    fullText = []
    for para in document.paragraphs:
        fullText.append(para.text)

    fullText = '\n'.join(fullText)

    #with open(f"/Users/mawuliagamah/gitprojects/STAR/data/documents/txt/document{idx}.txt", "w", encoding="utf-8") as txt_file:
    #    txt_file.write(fullText)

    return fullText

def split_document(document):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 5)
    chunks = text_splitter.split_documents(document)
    #print(chunks)
    return chunks 




def pre_process(document):

    """Applies pre-processing step to all of our data """
    document = document.lower()
    #ps = nltk.stemmer.PorterStemmer()document = remove_stopwords(document)
    
    # Stemming 

    stemmer = PorterStemmer()
    lemmertizer = WordNetLemmatizer()

    #document = ' '.join(stemmer.stem(token) for token in nltk.word_tokenize(document))
    document = ' '.join(lemmertizer.lemmatize(token) for token in nltk.word_tokenize(document))
    document = remove_stopwords(document)


    # Make all text in the document lower case 
    return document  


def document_processor():
    docs = load_documents2()

    processed_documents = []
    for idx,doc in enumerate(docs):

        string = convert_to_plain_text(doc,idx)
        processed_string = pre_process(string)
        processed_documents.append(processed_string)
    
    return processed_documents
    

from langchain_community.document_loaders import TextLoader


def langchain_documnet_loader():
    pass 
    

    
if __name__ == "__main__":
    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/*.docx"
    document_processor(path)
