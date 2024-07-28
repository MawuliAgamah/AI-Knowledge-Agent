
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI



def main(query):

    qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectordb.as_retriever(search_kwargs={'k': 7}),
    return_source_documents=True)

    query = query = """
            My goal is to become a Grade 7 in the Civil Service within a year working as a data scientist. 

            I have attached several documents that include my current CV, job descriptions, skill requirements, and performance reviews. 

            Can you help me create a comprehensive year-long plan that outlines:
            1. The specific skills and qualifications I need to acquire.
            2. Relevant courses, certifications, or training programs.
            3. Key milestones and deadlines for achieving these goals.
            4. Strategies for improving my current performance and gaining relevant experience.
            5. Tips for crafting an effective CV and job application for Grade 7 positions.
            6. Any other recommendations to help me achieve my goal.

            Thank you!
            """

    # we can now execute queries against our Q&A chain
    result = qa_chain({'query': 'Text about?'})
    

    return print(result['result'])




if __name__ == "__main__":
    main()