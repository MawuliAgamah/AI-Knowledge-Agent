from typing import Literal

# Best practice to use upper-case
ENTITIES = Literal[
    "CONCEPT",
    "TOPIC", 
    "EXAMPLE",
    "REFERENCE",
    "EXPLANATION"
]

RELATIONS = Literal[
    "PREREQUISITES",
    "BUILDS_ON",
    "SIMILAR_TO",
    "CONTRASTS_WITH", 
    "EXPLAINED_IN",
    "REFERENCED_BY",
    "EXAMPLE_IN",
    "BELONGS_TO",
    "RELATES_TO"
]

# Define which entities can have which relations
SCHEMA = {
    "CONCEPT": [
        "PREREQUISITES",
        "BUILDS_ON",
        "SIMILAR_TO",
        "CONTRASTS_WITH",
        "EXPLAINED_IN",
        "REFERENCED_BY",
        "EXAMPLE_IN",
        "BELONGS_TO",
        "RELATES_TO"
    ],
    "TOPIC": [
        "PREREQUISITES",
        "BUILDS_ON", 
        "SIMILAR_TO",
        "CONTRASTS_WITH",
        "EXPLAINED_IN",
        "BELONGS_TO",
        "RELATES_TO"
    ],
    "EXAMPLE": [
        "EXAMPLE_IN",
        "RELATES_TO",
        "BELONGS_TO"
    ],
    "REFERENCE": [
        "REFERENCED_BY",
        "RELATES_TO",
        "BELONGS_TO"
    ],
    "EXPLANATION": [
        "EXPLAINED_IN",
        "RELATES_TO",
        "BELONGS_TO"
    ]
}

# Define valid connections between specific entity types
validation_schema_rules = [
    ("CONCEPT", "PREREQUISITES", "CONCEPT"),
    ("CONCEPT", "BUILDS_ON", "CONCEPT"),
    ("CONCEPT", "SIMILAR_TO", "CONCEPT"),
    ("CONCEPT", "CONTRASTS_WITH", "CONCEPT"),
    ("CONCEPT", "EXPLAINED_IN", "EXPLANATION"),
    ("CONCEPT", "REFERENCED_BY", "REFERENCE"),
    ("CONCEPT", "EXAMPLE_IN", "EXAMPLE"),
    ("CONCEPT", "BELONGS_TO", "TOPIC"),
    ("CONCEPT", "RELATES_TO", "CONCEPT"),
    
    ("TOPIC", "PREREQUISITES", "TOPIC"),
    ("TOPIC", "BUILDS_ON", "TOPIC"),
    ("TOPIC", "SIMILAR_TO", "TOPIC"),
    ("TOPIC", "CONTRASTS_WITH", "TOPIC"),
    ("TOPIC", "EXPLAINED_IN", "EXPLANATION"),
    ("TOPIC", "BELONGS_TO", "TOPIC"),
    ("TOPIC", "RELATES_TO", "TOPIC"),
    
    ("EXAMPLE", "EXAMPLE_IN", "CONCEPT"),
    ("EXAMPLE", "RELATES_TO", "CONCEPT"),
    ("EXAMPLE", "BELONGS_TO", "TOPIC"),
    
    ("REFERENCE", "REFERENCED_BY", "CONCEPT"),
    ("REFERENCE", "RELATES_TO", "CONCEPT"),
    ("REFERENCE", "BELONGS_TO", "TOPIC"),
    
    ("EXPLANATION", "EXPLAINED_IN", "CONCEPT"),
    ("EXPLANATION", "RELATES_TO", "CONCEPT"),
    ("EXPLANATION", "BELONGS_TO", "TOPIC")
]