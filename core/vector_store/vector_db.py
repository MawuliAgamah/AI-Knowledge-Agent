import logging 

logging.basicConfig(filename='../logging/extract-log.txt', level=logging.INFO)
logging.basicConfig(filename='../logging/extract-error-log.txt', level=logging.ERROR)

import utils.chroma_utils as chroma_utils
from llama_index import ChromaVectorStore 

from llama_index.core import (
    StorageContext,
    VectorStoreIndex
    )

class DataBase:
    def __init__(self):
        self.client = None
        self.collections = {}
        self.documents = {}
        self.path_to_db = "/Users/mawuliagamah/gitprojects/STAR/db/chroma"



class DataBaseHandler:
    """
    Class which handle all interactions with the database
    """
    def __init__(self,database,client):
        self.name = "database handler"
        self.database = database
        self.client = client
        logging.info("Created DB Handler")

    def create_collection(self):
        pass

    
    def get_collection(self,collection_name):
        client = self.client
        collection = client.get_or_create_collection(name = collection_name)
        self.database.collections['collection_name'] = collection
        return collection 


    def add_document(self,document_object,collection,doc_type):
        collection = self.get_collection(collection)
        if doc_type == ".docx":
            chunks = document_object.get_contents("chunks")
            for chunk in chunks:
                for idx,item in chunk.items():
                    chroma_utils.add_items( collection = collection, 
                                           item =item, 
                                           metadata = {item['metadata']}, 
                                           id_num=  str(idx) 
                                           )

            logging.info(f"Document added to collection")
            return self
        else:
            return print("non implemeted")

    def show_collection_contents(self):
        print(self.database.collections)
        print(self.client.list_collections())


    def create_or_load_vector_store_index(self,chroma_collecion):
        # Check if index exists
        vector_store = ChromaVectorStore(chroma_collection =  chroma_collecion)
        storage_context = StorageContext.from_defaults(vector_store = vector_store)

        index = VectorStoreIndex.from_vector_store(
            vector_store, 
            storage_context=storage_context
            )
        return index
    

    
    def search(self,index,query):
        """Query the database using llama index
        
        
        
        """
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return response



class DataBasePipeline:
    """Database pipeline creates a simple interface to interact with vector store and retreival
    
    """
    def __init__(self,llm):
        self.llm = llm




    #def document(self,query):
    #    return output