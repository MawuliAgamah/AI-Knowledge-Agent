# AI Knowledge Agent

> An enterprise-grade Python framework for intelligent document processing and knowledge graph construction using multi-agent AI systems.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

KnowledgeAgent is an AI-powered system that transforms unstructured documents into intelligent knowledge graphs. The system leverages multiple Large Language Models working in collaboration to extract, validate, and enrich semantic relationships from text, creating a comprehensive knowledge representation suitable for advanced AI applications.

## 🏗️ Architecture 

### Multi-Agent Knowledge Extraction
- **Collaborative AI Pipeline**: Three specialized AutoGen agents work together:
  - `graph_constructor`: Extracts subject-predicate-object triplets with inference capabilities
  - `graph_validator`: Validates relationships and identifies missing connections
  - `graph_enricher`: Refines and enhances the final knowledge graph

### Intelligent Document Processing
- **Adaptive Chunking**: Context-aware segmentation that preserves document structure
  - Structured Markdown chunker respects heading hierarchies
  - Recursive character splitter for non-structured content
  - Automatic strategy selection based on content analysis
- **Multi-format Support**: Extensible parser framework for various document types

### Scalable Data Architecture
- **Multi-database Integration**: 
  - SQLite for document metadata and caching
  - Neo4j/Nebula Graph for knowledge graph storage
  - ChromaDB for vector embeddings and semantic search
- **Service-Oriented Design**: Modular services with clear separation of concerns

## Key Features

- **Multi-Agent AI System**: Collaborative LLM agents for robust knowledge extraction
- **Smart Document Processing**: Hierarchical chunking that preserves semantic context
- **Knowledge Graph Construction**: Automated extraction of entities and relationships
- **Semantic Search**: Vector-based similarity search across document collections
- **High-Performance Architecture**: Asynchronous processing with connection pooling
- **Enterprise-Ready**: Comprehensive logging, error handling, and configuration management

## 🏛️ System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        KC[KnowledgeGraphClient]
    end
    
    subgraph "Service Layer"
        DS[DocumentService]
        LS[LLMService]
        KGS[KnowledgeGraphService]
    end
    
    subgraph "Processing Pipeline"
        DM[DocumentManager]
        DP[DocumentProcessor]
        AG[AutoGen Agents]
    end
    
    subgraph "Data Layer"
        SQL[(SQLite)]
        NEO[(Neo4j/Nebula)]
        VDB[(ChromaDB)]
    end
    
    KC --> DS
    KC --> LS
    KC --> KGS
    
    DS --> DM
    DS --> DP
    KGS --> AG
    
    DP --> SQL
    KGS --> NEO
    LS --> VDB
```

## 📋 Technical Requirements

- **Python**: 3.9+
- **LLM API**: OpenAI API key required
- **Optional**: Docker for graph database deployment

### Core Dependencies
- **AI/ML**: `langchain`, `langchain-openai`, `autogen`
- **Databases**: `neo4j-python`, `chromadb`, `sqlite3`
- **Processing**: `pydantic`, `nltk`, `unstructured`

## 🔧 Installation & Setup

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/knowledgeAgent.git
cd knowledgeAgent

# Install in development mode
pip install -e .

# Set up environment variables (SECURE)
cp config.example .env
# Edit .env file with your actual API keys and configuration
```

### Production Deployment
```bash
# Install from PyPI (when published)
pip install knowledgeAgent

# Start graph database services
docker-compose up -d

# Verify installation
python -c "from knowledgeAgent.api.client import KnowledgeGraphClient; print('✅ Installation successful')"
```

## 💻 Usage Examples

### Basic Document Processing
```python
from knowledgeAgent.api.client import KnowledgeGraphClient

# Initialize the client
client = KnowledgeGraphClient(
    graph_db_config={
        "db_type": "neo4j",
        "host": "localhost",
        "port": 7687,
        "database": "knowledge",
        "username": "neo4j",
        "password": "password"
    },
    llm_config={
        "model": "gpt-3.5-turbo",
        "temperature": 0.2,
        "api_key": "your-openai-api-key"
    }
)

# Process a document
document_id = client.add_document(
    document_path="research_paper.md",
    document_type="markdown"
)

# Extract knowledge graph
client.extract_document_ontology(document_id)
```

### Advanced Configuration
```python
# Enterprise configuration with custom chunking
client = KnowledgeGraphClient(
    graph_db_config=GraphDatabaseConfig(
        db_type="neo4j",
        host="production-server.com",
        port=7687,
        database="enterprise_kg",
        pool_size=20,
        max_overflow=30
    ),
    db_config={
        "db_type": "sqlite",
        "db_location": "/data/cache/documents.db"
    },
    llm_config={
        "model": "gpt-4",
        "temperature": 0.1,
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    log_level="DEBUG"
)
```

## 🧠 AI Engineering Highlights

### Multi-Agent Collaboration
The system implements a sophisticated multi-agent architecture where specialized AI agents collaborate to ensure high-quality knowledge extraction:

```python
# Three agents work in sequence:
# 1. Constructor extracts initial triplets
# 2. Validator checks accuracy and finds missing relationships  
# 3. Enricher refines and enhances the final output

def extract_ontology(document: str) -> dict:
    """Multi-agent knowledge extraction with validation"""
    group_chat = GroupChat(
        agents=[graph_constructor, graph_validator, graph_enricher],
        max_round=3,
        speaker_selection_method="round_robin"
    )
    # ... implementation details
```

### Intelligent Chunking Strategy
Context-aware document segmentation that preserves semantic meaning:

```python
class StructuredMarkdownChunker:
    """Respects document hierarchy for optimal chunking"""
    
    def chunk_section(self, section: MarkdownSection, max_size: int):
        # Recursive chunking that maintains context
        # Preserves header hierarchies and relationships
        # Falls back to character-based splitting when needed
```

## 🏗️ Architecture Patterns Implemented

- **Service-Oriented Architecture**: Clear separation between document processing, LLM operations, and knowledge graph management
- **Factory Pattern**: Extensible document parser system for multiple file formats
- **Strategy Pattern**: Pluggable chunking algorithms based on content type
- **Observer Pattern**: Event-driven processing pipeline with comprehensive logging
- **Repository Pattern**: Abstract database operations for multiple storage backends

## 📊 Performance & Scalability

- **Async Processing**: Non-blocking document processing pipeline
- **Connection Pooling**: Efficient database connection management
- **Caching Layer**: SQLite-based caching for processed documents
- **Batch Processing**: Optimized for large document collections
- **Memory Management**: Streaming document processing for large files

## 🧪 Testing & Quality Assurance

```bash
# Run the test suite
python -m pytest

# Run with coverage
python -m pytest --cov=src/knowledgeAgent

# Integration tests
python -m pytest tests/integration/
```

## 📈 Development Roadmap

- [ ] GraphQL API for advanced querying
- [ ] Real-time document processing with WebSocket support
- [ ] Advanced visualization dashboard
- [ ] Multi-language document support
- [ ] Distributed processing with Celery
- [ ] ML-based document classification

## 🤝 Architecture Decisions

### Why Multi-Agent Systems?
- **Validation**: Multiple perspectives ensure higher accuracy
- **Specialization**: Each agent optimized for specific tasks
- **Iterative Improvement**: Self-correcting knowledge extraction

### Database Strategy
- **SQLite**: Fast caching and development
- **Neo4j/Nebula**: Optimized graph traversal and queries  
- **ChromaDB**: Semantic similarity and vector operations


## 📄 License

MIT License - see [LICENSE.txt](LICENSE.txt) for details.

## 🏢 Enterprise Features

- **Audit Logging**: Complete processing trail for compliance
- **Multi-tenant Support**: Isolated knowledge graphs per organization
- **API Rate Limiting**: Configurable LLM usage controls
- **Backup & Recovery**: Automated data backup strategies
- **Monitoring**: Comprehensive metrics and health checks

---

*Built with modern AI engineering practices, emphasizing scalability, maintainability, and production-readiness.*









