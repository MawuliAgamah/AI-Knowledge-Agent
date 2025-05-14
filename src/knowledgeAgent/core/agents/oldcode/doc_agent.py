
class DocumentAgentUtilities:
    """Utiliy class for the Agent to use. Allows us to make the code base modular"""
    def __init__(self,) -> None:
        pass

    def doc_summary_by_map_reduce(self, llm, chunks):
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import time

        start_time = time.time()

        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:
        Text: {text}
        Create a summary that:
        1. Preserves specific terminology and key phrases
        2. Maintains important context and relationships
        3. Captures actionable insights and recommendations
        4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that:
            - Maintains semantic richness for vector similarity matching
            - Preserves key terminology and specific details
            - Creates clear thematic connections
            - Structures information in a retrievable way"""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval:
        Summaries: {summaries}
        Create a final summary that:
        1. Preserves specific terminology and key concepts
        2. Maintains relationships between ideas
        3. Structures information in clear thematic sections
        4. Keeps concrete examples and specific details""")
        ])

        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()

        # Map: Generate individual summaries for each chunk
        map_start_time = time.time()
        summaries = []
        for chunk in chunks:
            summary = map_chain.invoke({"text": chunk})
            summaries.append(summary)
        map_duration = time.time() - map_start_time
        print(f"✓ Map phase completed in {map_duration:.2f} seconds")

        # Reduce: Combine all summaries
        reduce_start_time = time.time()
        final_summary = reduce_chain.invoke({"summaries": "\n\n".join(summaries)})
        reduce_duration = time.time() - reduce_start_time
        
        total_duration = time.time() - start_time
        print(f"✓ Document summary generated")
        print(f"Total execution time: {total_duration:.2f} seconds")
        print(f"Map phase: {map_duration:.2f} seconds")
        print(f"Reduce phase: {reduce_duration:.2f} seconds")
        
        return final_summary
    
    async def doc_summary_by_map_reduce_async(self, llm, chunks):
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import asyncio
        import time
        start_time = time.time()

        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships 
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:
        Text: {text}
        Create a summary that:
        1. Preserves specific terminology and key phrases
        2. Maintains important context and relationships
        3. Captures actionable insights and recommendations
        4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that:
            - Maintains semantic richness for vector similarity matching
            - Preserves key terminology and specific details
            - Creates clear thematic connections
            - Structures information in a retrievable way"""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval:
        Summaries: {summaries}
        Create a final summary that:
        1. Preserves specific terminology and key concepts
        2. Maintains relationships between ideas
        3. Structures information in clear thematic sections
        4. Keeps concrete examples and specific details.
        5. Ensure the summary is no longer that 2 sentences.""")
        ])

        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()

        # Map: Generate individual summaries for each chunk
        semaphore = asyncio.Semaphore(10)
        async def process_chunk(chunk):
            async with semaphore:  # Rate limiting
                try:
                    return await map_chain.ainvoke({"text": chunk})
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    return None

        map_start_time = time.time()
        tasks = [process_chunk(chunk) for chunk in chunks]
        summaries = await asyncio.gather(*tasks)
        map_duration = time.time() - map_start_time
        print(f"✓ Map phase completed in {map_duration:.2f} seconds")

        summaries = [s for s in summaries if s is not None]

        # Combine summaries
        try:
            reduce_start_time = time.time()
            final_summary = await reduce_chain.ainvoke(
                {"summaries": "\n\n".join(summaries)}
            )
            reduce_duration = time.time() - reduce_start_time
            
            total_duration = time.time() - start_time
            print(f"✓ Document summary generated")
            print(f"Total execution time: {total_duration:.2f} seconds")
            print(f"Map phase: {map_duration:.2f} seconds")
            print(f"Reduce phase: {reduce_duration:.2f} seconds")
            return final_summary
        except Exception as e:
            print(f"Error in reduce step: {e}")
            return None

    async def doc_title_by_map_reduce_async(self, llm, chunks):
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import asyncio
        import time
        start_time = time.time()
        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships 
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:
        Text: {text}
        Create a summary that:
        1. Preserves specific terminology and key phrases
        2. Maintains important context and relationships
        3. Captures actionable insights and recommendations
        4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create the title of the document:
             """),
            ("human", """Synthesize these summaries of all the documents summaries of the document given to you into a single title of for the document.
        Summaries: {summaries}""")
        ])

        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()

        # Map: Generate individual summaries for each chunk
        semaphore = asyncio.Semaphore(10)
        async def process_chunk(chunk):
            async with semaphore:  # Rate limiting
                try:
                    return await map_chain.ainvoke({"text": chunk})
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    return None

        map_start_time = time.time()
        tasks = [process_chunk(chunk) for chunk in chunks]
        summaries = await asyncio.gather(*tasks)
        map_duration = time.time() - map_start_time
        print(f"✓ Map phase completed in {map_duration:.2f} seconds")

        summaries = [s for s in summaries if s is not None]

        # Combine summaries
        try:
            reduce_start_time = time.time()
            final_summary = await reduce_chain.ainvoke(
                {"summaries": "\n\n".join(summaries)}
            )
            reduce_duration = time.time() - reduce_start_time
            
            total_duration = time.time() - start_time
            print(f"✓ Document summary generated")
            print(f"Total execution time: {total_duration:.2f} seconds")
            print(f"Map phase: {map_duration:.2f} seconds")
            print(f"Reduce phase: {reduce_duration:.2f} seconds")
            return final_summary
        except Exception as e:
            print(f"Error in reduce step: {e}")
            return None


    def doc_summary_by_map_reduce_thread_pool(self, llm, chunks):
        """Process Document using the ThreadPool Executor"""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from concurrent.futures import ProcessPoolExecutor,as_completed
        import multiprocessing
        import time
            
        print('threadpool map reduce')
        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """
             You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:

        Text: {text}

        Create a summary that:
        1. Preserves specific terminology and key phrases
        2. Maintains important context and relationships
        3. Captures actionable insights and recommendations
        4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that is 
             no longer than one sentence."""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval. Summaries: {summaries}s""")])
        # Create map chain
        map_chain = map_prompt | llm | StrOutputParser()
        # Create reduce chain
        reduce_chain = reduce_prompt | llm | StrOutputParser()
        # Map: Generate individual summaries for each chunk\

        def process_chunk(chunk):
            return map_chain.invoke({"text": chunk})

        start_time = time.time()
        cpu_count = multiprocessing.cpu_count()
        optimal_workers = cpu_count - 1 

        futures = []
       
        with ProcessPoolExecutor(max_workers=optimal_workers) as executor:
            for chunk in chunks:

                future = executor.submit(process_chunk, chunk)
                futures.append(future)
        
        summaries = []
        for future in as_completed(futures):
            try:
                result = future.result()
                summaries.append(result)
            except Exception as e:
                print(f"An error occurred: {e}")

        # Reduce: Combine all summaries
        final_summary = reduce_chain.invoke({"summaries": "\n\n".join(summaries)})
        print(f"Processing time: {time.time() - start_time:.2f} seconds")
        return final_summary

    def doc_summary_by_map_reduce_multiprocess(self, llm, chunks):
        """Process Document using Multiprocess"""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        import multiprocess as mp
        import multiprocess.pool as mp_pool
        import time

        print('multiprocess map reduce')

        # Map prompt (summarizing individual chunks)
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a precise summarizer focused on extracting key concepts and information that would be valuable for retrieval augmented generation (RAG).
            Focus on:
            - Main concepts and their relationships
            - Key terminology and definitions
            - Core arguments and supporting evidence
            - Actionable insights and recommendations
            Maintain factual accuracy and specific details that could be relevant for future queries."""),
            ("human", """Analyze and summarize the following text, emphasizing elements that would be useful for future retrieval:
            Text: {text}
            Create a summary that:
            1. Preserves specific terminology and key phrases
            2. Maintains important context and relationships
            3. Captures actionable insights and recommendations
            4. Includes relevant examples or evidence""")
        ])

        # Reduce prompt (combining summaries)
        reduce_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a expert at synthesizing information for RAG systems. Your goal is to create a comprehensive summary that is 
            no longer than one sentence."""),
            ("human", """Synthesize these summaries into a single coherent summary optimized for RAG retrieval. Summaries: {summaries}s""")
        ])

        # Create chains
        map_chain = map_prompt | llm | StrOutputParser()
        reduce_chain = reduce_prompt | llm | StrOutputParser()

        def process_chunk(chunk):
            return map_chain.invoke({"text": chunk})

        start_time = time.time()
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        optimal_workers = cpu_count - 1

        print(f'Using {optimal_workers} workers')
        
        # Using Pool instead of ProcessPoolExecutor
        with mp_pool.Pool(processes=optimal_workers) as pool:
            try:
                # Map phase - process all chunks
                results = pool.map_async(process_chunk, chunks)
                
                # Wait for all results and get them
                summaries = results.get()
                
                # Filter out any None results
                summaries = [s for s in summaries if s is not None]
                
                if not summaries:
                    raise ValueError("No valid summaries were generated")
                
                # Reduce phase
                final_summary = reduce_chain.invoke({"summaries": "\n\n".join(summaries)})
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                raise
            finally:
                pool.close()
                pool.join()

        print(f"Processing time: {time.time() - start_time:.2f} seconds")
        return final_summary

    def doc_summary_by_clustering(self,document):
        """Generates a document summary using the clustering method"""
        pass

