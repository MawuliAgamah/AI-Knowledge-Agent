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

# The Document Class is concerned with building a docment 
class Document:
    pass 




    
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
    



if __name__ == "__main__":
    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/*.docx"
    document_processor(path)
