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

[Priority] [Status] [Descrption]

 [1] [in_progress] Implement llama index retrival with ChromaDB. 
        [] Improve retreival - Considering other retreival methods i.e. BM25, Reciprocal Rank

- [2] Make a pipeline to handle all data base related code. 

- [] Implement the database related code as a singleton pattern.;

- [2] Improve how we handle collections, this should be a singleton
     This is so that we only have one instance of a collection.

- [4] Add titles to the document object using the LLM. 
      Entry point -> Document.py
         class DocumentHandler().

- [2] Fix meta data on documents, currently meta data is only for chunks.
      Entry point -> Document.py
         class DocumentHandler().

- [3] Improve the current implementation of the Agents.
      Entry Point -> Agent.py

        [] Improve the configuration handling of agents.
        [] Determine the design pattern for agents and how they should fit into the application.
        [] Give agents conversational memory.

- [5] Can we create a runtime for agents? what does this even mean.

     So agents have an environment in which they exist and operate.
     This could be asyncronuse so they aren't just responding to 
     inputs from the user, but are constantly working and optimising outputs.

- [4] Testing
    [] Write unit tests for document handler class.


- [5] Implement semantic chunking (Research dependent).



# Currently Working On : 

Document Retreival:

    - Implement llama index retrival with ChromaDB 
        ** Entry point :  : VectorDataBase.py**
            DataBaseHandler -> 








# Thoughts and Ideas : 

- ** Markdown as structure ** 
    We want our documents to have structure. Should we get the LLM to 
    rewrite the document, keeping it as is , but adding structure VIA markdown?

- How can we truly innovate here?
    Can we peice together multiple outputs?