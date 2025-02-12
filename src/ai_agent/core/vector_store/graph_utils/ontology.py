from typing import Literal

ENTITIES = Literal[
   "CONCEPT",
   "TOPIC",
   "EXAMPLE",
   "REFERENCE",
   "EXPLANATION"
]

# Relationship types between entities
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

# Schema defining valid relationships between entity types
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