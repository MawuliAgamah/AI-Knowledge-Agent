# Project Overview

## MVP (v0)
- [ ] User Feedback System
  - Enable editing of summaries and metadata before vector DB insertion
- [ ] Document Comparison Tool
  - Compare/contrast document pairs
- [ ] Frontend Development
  - Human-in-the-loop interface

## Core Features (In Progress)

- [] Architecture
  -[] dockerise applicaiton 

- [ ] Database Pipeline
  - [x] Base pipeline implementation
  - [x] Database code centralization
  - [ ] Singleton pattern implementation
  - [ ] Collection handling improvement
  - [ ] Document metadata enhancement

- [ ] Document Processing
  - [ ] Title generation via LLM
  - [ ] Metadata for full documents
  - [ ] Semantic chunking
  - [ ] Improved document handling/upload
  - [ ] Duplicate prevention system

- [ ] Agent System Enhancement
  - [ ] Configuration system
  - [ ] Design pattern implementation
  - [ ] Conversational memory
  - [ ] Runtime environment
  - [ ] Function calling integration

- [ ] Retrieval System
  - [x] LlamaIndex with ChromaDB
  - [ ] Hybrid retrieval (BM25 + Reciprocal Rank)
  - [ ] Collection management features
    - [ ] Document listing
    - [ ] Collection overview
    - [ ] Collection summaries

## Future Enhancements
- [ ] Web scraping system
- [ ] Markdown structural formatting
- [ ] Multi-output synthesis
- [ ] Vector DB planning integration

## Technical Debt
### Bugs
- Slow startup time investigation
- Multiple execution instances
- Logger optimization

### Testing
- [ ] DocumentHandler unit tests
- [ ] Agent system integration tests

### Code Quality
- [ ] Prompt template organization
- [ ] Markdown to LangChain conversion
- [ ] Codebase cleanup

## Development Commands
```bash
# Clean pycache files
find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf
```