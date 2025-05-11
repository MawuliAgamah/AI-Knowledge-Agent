# Knowledge Agent

A Python module for creating and managing knowledge graphs with AI.

## Installation

### From PyPI (once published)
```bash
pip install knowledge_agent
```

### Development Installation (Editable Mode)
Clone the repository:
```bash
git clone https://github.com/yourusername/knowledge_agent.git
cd knowledge_agent
pip install -e .
```

This installs the package in "editable" mode, so changes to the source code will be immediately available without reinstalling.

## Usage

```python
from knowledge_agent.core import module

# Create a knowledge graph
kg = module.KnowledgeGraph(name="my_graph")

# Add data to the graph
kg.add_data(source="my_document.txt")

# Query the knowledge graph
results = kg.query("What is AI?")
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









