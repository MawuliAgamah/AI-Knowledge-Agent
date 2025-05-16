from langchain_core.prompts import ChatPromptTemplate
from langchain_core import prompts, output_parsers

TOPICS_EXTRACTION_PROMPT = prompts.ChatPromptTemplate.from_messages([
    ("system", """Analyze this text chunk from a larger document and identify the 3 most significant topics.
     There must be 3 topics.
    
    A good topic should:
    - Represent a major theme or subject matter discussed
    - Be broad enough to encompass multiple related points
    - Be specific enough to distinguish from other topics
    - Be expressed in 1-3 words when possible
    
    
    {format_instructions}"""),
    ("human", "{chunk}")
])

KEYWORD_EXTRACTION_PROMPT = prompts.ChatPromptTemplate.from_messages([
    ("system", """Analyze this text chunk from a larger document and identify the 2-3 most important keywords.
     There must be 3 keywords.
    A good keyword should:
    - Represent a specific concept, term, or entity mentioned
    - Be consistently prominent or crucial to understanding the text
    - Typically be a noun, proper noun, or technical term
    - Be expressed in 1-2 words when possible
    
    Format each keyword with a '#' prefix (e.g., #artificial_intelligence).
    For multi-word keywords, use underscores between words.
    
    {format_instructions}"""),
    ("human", "{chunk}")
])

