import logging 

logging.basicConfig(filename='../logging/extract-log.txt', level=logging.INFO)
logging.basicConfig(filename='../logging/extract-error-log.txt', level=logging.ERROR)

import utils.chroma_utils as chroma_utils

class DataBase:
    def __init__(self):
        self.client = None
        self.collections = []
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

    
    def get_collection(self,collection):
        client = self.client
        self.database.collections.append(collection)
        collection = client.get_or_create_collection(name = collection)
        return collection 


    def add_document(self,document_object,collection,doc_type):
        collection = self.get_collection(collection)
        if doc_type == ".docx":
            chunks = document_object.get_contents("chunks")
            for chunk in chunks:
                for idx,item in enumerate(chunk):
                    chroma_utils.add_items( collection = collection, 
                                           item = item.page_content, 
                                           metadata = {"source":item.metadata['source']} , 
                                           id_num=  str(idx) 
                                           )

            logging.info(f"Document added to collection")
        else:
            return print("non implemeted")

    def show_contents(self):
        print(self.database.collections)
        print(self.client.list_collections())
