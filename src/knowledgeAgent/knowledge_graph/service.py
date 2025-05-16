



class KnowledgeGraphService:
    """Service for knowledge graph operations"""
    
    def __init__(self,db_client,llm_service=None):
        self.llm_service = llm_service
        self.db_client = db_client


    def extract_ontology(self, document_id):
        """Extract ontology from document"""

        document = self.db_client.get_document(document_id)
       # get document from database
       
        chunks = document.textChunks
        for text in chunks:
            print(text)
            
    
      
    
       
       # extract ontology from document

       # save ontology to database


    
