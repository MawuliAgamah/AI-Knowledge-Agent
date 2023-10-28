from langchain.text_splitter import CharacterTextSplitter
from  langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma


class DocumentHandler():
    """
    This takes in URLS 
    Converts them to a langchain document ready to be stored 
    in the DB
 
    Args:
        document_path (str): The path to the document.
    Returns:
        document_path (str): The path to the document.
    """
    def __init__(self):
            #self.document_path = document_path
            self.document_path = "/Users/mawuliagamah/gitprojects/langchain/data/The Last Question.pdf"
            
    def process_document(self):
        loader = PyPDFLoader(self.document_path)
        document = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        documents = text_splitter.split_documents(document)        
        return documents


#class database():
#    """
#    Class to load in and read PDF files.
# 
#    Args:
#    
#    Returns:
#        string: 
#    """
#    def __init__(self):
#            self.data = []



#class model():
#    def __init__self(prompt):
#
#
#        self.prompt = prompt


# Instantiate the Data with an initial value
#my_object = Container()
# Instantiate the Data with an initial value









# Instantiate the class with an initial value
#database = database()


# 
#database.storeData()

#dbData = database.retrieveData() # Get the data



#model = languageModel(llm,dbData,return)
# Use the object's method to display the value
#model.answer()  # Output: 10
    

def main():
    document_handler = DocumentHandler()
    processed_documents = document_handler.process_document()
    print(processed_documents)

if __name__ == "__main__":
    main()
    