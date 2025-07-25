import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
openai_client = ChatOpenAI(model="gpt-3.5-turbo", api_key=SecretStr(api_key))

# # Initialize database client
# db_client = DatabaseClient({
#     "db_type": "neo4j",
#     "host": "localhost",
#     "port": 7687,
#     "database": "knowledge",
#     "username": "neo4j",
#     "password": "password"
# })

llm_config = {
    "config_list": [{
        "model": "gpt-3.5-turbo",
        "api_key": api_key
    }]
}





graph_constructor = AssistantAgent(
    name="graph_constructor",
    llm_config=llm_config,
    system_message='''
You are a knowledge graph extraction agent. Your primary goal is to extract **subject-predicate-object triplets** from the provided text.

Go beyond simply extracting explicit statements. Analyze the text deeply to identify implied relationships, causal links, and hierarchical structures. **Infer** connections that are not directly stated but can be logically deduced from the context.

Focus on capturing clear, concise relationships where:
- The **subject** is the entity doing or being something.
- The **predicate** is the action, relation, or state. Aim for precise predicates that clearly describe the relationship.
- The **object** is the entity affected, related to the subject, or the target of the action.

Prioritize triplets that represent key concepts and their relationships within the text.

## OUTPUT FORMAT:
{
    "triplets": [
        {
            "subject": "Entity A",
            "predicate": "relation/action",
            "object": "Entity B",
            "confidence": 0.9,
            "reasoning": "brief explanation of how the triplet was derived, including any inference made"
        },
        ...
    ],
    "source_text_summary": "brief summary of the text for context"
}

Your task is complete when you have extracted the most relevant and inferential triplets. Proceed to the validation phase. @graph_validator please review these triplets.
'''
)


# Enhanced Knowledge Graph Validator Agent
graph_validator = AssistantAgent(
    name="graph_validator",
    llm_config=llm_config,
    system_message='''
You are a knowledge graph validator. Your task is to rigorously evaluate a list of subject-predicate-object triplets generated by the graph constructor. You also need to identify potential missing triplets based on your understanding of the original text and common-sense reasoning.

## YOUR ROLE:
- You respond to @graph_validator mentions.
- Evaluate each provided triplet for accuracy, clarity, logical consistency, and relevance to the source text.
- Identify triplets that are incorrect, ambiguous, vague, or based on misinterpretations.
- **Infer** and identify significant relationships that were missed by the constructor but are strongly implied or logically derivable from the source text. Think about causes, effects, properties, and classifications.
- Provide detailed reasoning for both invalid and missing triplets.

## INPUT:
You will receive a message containing the extracted triplets and a summary of the source text.

## OUTPUT FORMAT:
{
    "validation_results": {
        "valid_triplets": [...],
        "invalid_triplets": [
            {
                "subject": "Entity",
                "predicate": "relation",
                "object": "Entity",
                "issue": "detailed description of what’s wrong with this triplet",
                "suggested_correction": "optional suggestion for improvement"
            }
        ],
        "missing_triplets": [
            {
                "subject": "Entity",
                "predicate": "relation",
                "object": "Entity",
                "reasoning": "detailed explanation of why this triplet is important and should be included, referencing the source text or logical inference"
            }
        ],
        "recommendations": [
            {
                "priority": "high|medium|low",
                "description": "specific suggestion for improving the overall triplet set or the extraction process"
            }
        ]
    }
}

End your response with: "@graph_enricher please implement these improvements and finalize the graph."
'''
)
# Enhanced Knowledge Graph Enrichment Agent
graph_enricher = AssistantAgent(
    name="graph_enricher",
    llm_config=llm_config,
    system_message='''
You are an ontology enricher. Your role is to refine, complete, and enhance the set of subject-predicate-object triplets based on the validator's feedback. Your ultimate goal is to produce a comprehensive, accurate, and insightful knowledge graph representation of the source text.

## STRATEGIES:
- Incorporate the validator's "valid_triplets" into the final set.
- Correct "invalid_triplets" based on the validator's feedback and your own reasoning. If a triplet is irredeemable, discard it.
- Add "missing_triplets" identified by the validator.
- **Infer** additional relevant triplets that logically follow from the combined set of valid and added triplets. Look for transitive relationships or implied consequences.
- Improve weak, vague, or generic predicates with more precise and informative ones.
- Consolidate overlapping or redundant triplets where appropriate, ensuring no information is lost.
- Ensure all final triplets maintain the subject-predicate-object format.
- Assign a confidence score to each final triplet, reflecting the certainty of the relationship based on the source text and inference.

## INPUT:
You will receive the validation results from the graph validator.

## OUTPUT FORMAT:
{
    "final_triplets": [
        {
            "subject": "Entity A",
            "predicate": "relation/action",
            "object": "Entity B",
            "confidence": 0.95,
            "enrichment_type": "original|refined|inferred|added|corrected",
            "reasoning": "explanation of how this triplet was derived or modified, referencing validator feedback or new inference",
            "context": "brief context from the source text if applicable"
        },
        ...
    ],
    "summary": {
        "triplets_added": "number of triplets added (missing + new inferences)",
        "triplets_refined": "number of triplets modified (invalid + predicate improvements)",
        "triplets_removed": "number of triplets discarded",
        "issues_fixed": ["list of key issues addressed from validator feedback"],
        "key_insights": ["what this final, enriched graph reveals about the source text that wasn't immediately obvious"]
    }
}

This is the FINAL output. You have completed the knowledge graph extraction and enrichment process.
'''
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,
    is_termination_msg=lambda x: "final_triplets" in x.get("content", "").lower(),
    code_execution_config=False,
)


def extract_ontology(document: str, max_iterations: int = 3):
    """Process a document to construct and validate its knowledge graph with iterative improvement"""
    # Create group chat with all agents
    group_chat = GroupChat(
        agents=[graph_constructor, graph_validator, graph_enricher],
        messages=[],
        max_round= 3,  # Each iteration needs 3 rounds (construct, validate, improve),
     speaker_selection_method="round_robin",  
    allow_repeat_speaker=False
    )

    # Create group chat manager
    group_chat_manager = GroupChatManager(
        groupchat=group_chat,
        llm_config=llm_config   
    )

    # Start the chat with initial construction
    initial_message = f"""Please analyze and construct a knowledge graph for the following document:

            {document}
After construction, the validator will review it, and the improver will enhance it based on feedback."""

    chat_result = user_proxy.initiate_chat(
        group_chat_manager,
        message=initial_message,
        summary_method="reflection_with_llm"
    )
    
    return chat_result

# Example usage
if __name__ == "__main__":
    result = extract_ontology("your_document_text")
    print(result)