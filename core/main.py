from config import llm_config
from core.agents.document_agent import DocumentAgent 
from core.document import Document 


if __name__ == '__main__':
    
    # Create the language model users throughout the application 
    docuemnt_llm = DocumentAgent(config= llm_config)
    document = Documnet(path = "PATH")

    # Build the document up with the help of an LLM for use in RAG
    document = document.build(llm = docuemnt_llm)





