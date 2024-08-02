
from agents.document_agent import DocumentAgent 
from Document import DocumentPipeline , DocumentBuilder
from config.config import llm_config

if __name__ == '__main__':

    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"
    document_builder = DocumentBuilder()
    document_agent = DocumentAgent(config=llm_config) # Instantiate the document agent with the configuration
    pipeline = DocumentPipeline(document_builder = document_builder ,llm = document_agent) # Instanstiate a document pipeline with a docment builder and the
    document_object = pipeline.build_document(path_to_document = path) # Create a document object for a single document 

    print(document_object.contents)

    # Work station API which we can then use in a DJANGO application 
    #work_station = WorkStation()
    #work_station.inject_document("path")
    #work_station.enhance(query = "query")