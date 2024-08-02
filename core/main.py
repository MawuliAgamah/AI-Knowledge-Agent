
from agents.document_agent import DocumentAgent 
from Document import DocumentPipeline , DocumentBuilder
from config import llm_config

if __name__ == '__main__':

    path = "/Users/mawuliagamah/gitprojects/STAR/data/documents/word/Job Adverts.docx"

    document_builder = DocumentBuilder()

    # Instantiate the document agent with the configuration
    document_agent = DocumentAgent(config=llm_config)

    # Instanstiate a document pipeline with a docment builder and the 
    pipeline = DocumentPipeline(document_builder = document_builder ,llm = document_agent)

    # Create a document object for a single document 
    document_object = pipeline.build_document(path_to_document = path)

    print(document_object.contents)





