# Knowledge Agent

A Python module for creating and managing knowledge graphs with AI.

## Installation

### From PyPI (once published)
```bash
pip install knowledgeAgent
```

### Development Installation (Editable Mode)
Clone the repository:
```bash
git clone https://github.com/yourusername/knowledgeAgent.git
cd knowledgeAgent
pip install -e .
```

This installs the package in "editable" mode, so changes to the source code will be immediately available without reinstalling.

## Usage

```python
from knowledgeAgent.core import module

# Create a knowledge graph
kg = module.KnowledgeGraphModule()

# Add data to the graph
agent = module.create_agent(
    sql_db="path/to/db.db",
    vector_db_path="path/to/vector_db",
    collection="my_collection",
    model_name="gpt-3.5-turbo"
)

# Load documents
agent = agent.load_documents(path_to_document=["document.md"])
```

## Development

### Prerequisites

```bash
# Start the required Nebula services for development
docker-compose up -d metad0 metad1 metad2 storaged0 storaged1 storaged2 graphd graphd1 graphd2

# Wait for about 30 seconds to ensure services are up
sleep 30

# Start the console
docker-compose up console
```

### Running Tests

```bash
python -m pytest
```

## License

MIT License




---

# First start the core services
docker-compose up -d metad0 metad1 metad2 storaged0 storaged1 storaged2 graphd graphd1 graphd2

# Wait for about 30 seconds to ensure services are up
sleep 30

# Then start the console
docker-compose up console





---

# Features









