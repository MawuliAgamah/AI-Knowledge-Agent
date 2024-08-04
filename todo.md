# Things im working on and need to implement 


# Features 

## Minimum Valuable Product (v0). 

[] User Feedback
    - Once model has created a summary and created meta-data,   
        allow the user to edit these components before then inserting them into the vector database.

[] Document Comparison 
    - Given two documents comopare and contrast them.


[] Build front-end
    [] **Human in the loop :** User 

## Bells and Whistles
[] Scrape data from the web given a search query, and retreive those documents


## To Do : 


- [] Implement llama index retrival with ChromaDB.

- [] Add titles to the document object using the LLM. 
      Entry point -> Document.py
         class DocumentHandler().

- [] Fix meta data on documents, currently meta data is only for chunks.
      Entry point -> Document.py
         class DocumentHandler().

- [] Improve the current implementation of the Agents.
      Entry Point -> Agent.py

        [] Improve the configuration handling of agents.
        [] Determine the design pattern for agents and how they should fit into the application.
        [] Give agents conversational memory.

- [] Can we create a runtime for agents? what does this even mean.

     So agents have an environment in which they exist and operate.
     This could be asyncronuse so they aren't just responding to 
     inputs from the user, but are constantly working and optimising outputs.

- [] Testing
    [] Write unit tests for document handler class.


- [] Implement semantic chunking (Research dependent).



# Currently Working On : 

Document Retreival:

    - Implement llama index retrival with ChromaDB 
        ** Entry point :  : VectorDataBase.py**
            DataBaseHandler -> 








# Thoughts and Ideas : 

- ** Markdown as structure ** 
    We want our documents to have structure. Should we get the LLM to 
    rewrite the document, keeping it as is , but adding structure VIA markdown?