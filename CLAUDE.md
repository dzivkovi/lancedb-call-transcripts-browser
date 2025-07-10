# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This workspace contains LanceDB browser utilities for exploring the `whiskey_jack` database containing text chunks with vector embeddings. The database stores conversational transcripts that have been chunked and embedded for RAG (Retrieval Augmented Generation) applications.

## Database Structure

### LanceDB Setup
- **Database Path**: Current directory (`.`) 
- **Table Directory**: `./whiskey_jack.lance/` (this IS the table, not the database)
- **Table Name**: `whiskey_jack` (directory name without .lance extension)
- **Connection**: `lancedb.connect(".")` (NOT "./whiskey_jack.lance"!)

### Data Schema
Key columns in the whiskey_jack table:
- `session_id` - Unique identifier for conversation sessions
- `timestamp` - When the text chunk was created
- `text` - The actual text content (chunked)
- `chunk_id` - Identifier for the chunk within a session
- `run_id` - Identifier for processing runs
- Vector embeddings (created with `intfloat/multilingual-e5-large-instruct`)

### Chunking Strategy
- **Model**: multilingual-e5-large-instruct (512 token context window)
- **Chunker**: chonkie's SentenceChunker
- **Overlap**: No overlap between chunks

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running Applications
```bash
# Quick schema/data exploration
python simple_explorer.py

# Launch Streamlit browser
streamlit run lancedb_browser.py

# Extract session texts (client's approach)
python client_example.py
```

## Key Scripts

### simple_explorer.py
Basic command-line exploration tool that:
- Connects to LanceDB and lists tables
- Shows schema information
- Displays sample data
- Validates expected columns

### lancedb_browser.py
Comprehensive Streamlit application with:
- **Overview Tab**: Schema, row counts, sample data
- **Raw Data Tab**: Paginated browsing of chunks
- **Session Texts Tab**: Aggregated text by session (using DuckDB)
- **Search Tab**: Filtering and text search capabilities

### client_example.py
Implements the client's specific approach:
- Uses DuckDB for SQL queries on Lance data
- Aggregates text chunks by session_id and run_id
- Creates session text lookup dictionary
- Exports results to CSV

## Data Access Patterns

### Basic LanceDB Connection
```python
import lancedb
db = lancedb.connect("./whiskey_jack.lance")
table = db.open_table("whiskey_jack")
```

### Session Text Aggregation (Client Method)
```python
import duckdb
from lancedb import connect

db = connect("./whiskey_jack.lance")
whiskey_table = db.open_table("whiskey_jack").to_lance()

sql = """
SELECT 
    session_id,
    FIRST(timestamp) as timestamp,
    STRING_AGG(text, ' ') as text,
    run_id
FROM 
    (SELECT * FROM whiskey_table ORDER BY timestamp, chunk_id ASC) 
GROUP BY 
    session_id,
    run_id
"""

result = duckdb.query(sql).to_df()
```

### Simple Data Browsing
```python
# Get sample data
sample = table.to_pandas().head(10)

# Filter data
filtered = table.search().where("session_id = 'some_id'").to_pandas()

# Get schema
schema = table.schema
```

## Code Standards

### Python Style Guidelines
- Follow PEP 8 conventions
- Use type hints for function parameters and returns
- Docstrings required for all public functions (Google style)
- Maximum line length: 88 characters (Black formatter)

### Error Handling

```python
# Preferred pattern for database operations
try:
    result = table.search().where(condition).to_pandas()
except Exception as e:
    logger.error(f"Query failed: {e}")
    raise DatabaseQueryError(f"Failed to execute query: {e}")
```

### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)
# Use logger.debug() for detailed traces
# Use logger.info() for important operations
# Use logger.error() for exceptions
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test file
pytest tests/test_lancedb_operations.py
```

### Test Structure

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Mock external dependencies (LanceDB connections)
- Aim for 80% code coverage

## Environment Setup

### Required Environment Variables

```bash
# Optional: Custom LanceDB path
export LANCEDB_PATH="./whiskey_jack.lance"

# Optional: Logging level
export LOG_LEVEL="INFO"
```

### Python Version

- Required: Python 3.8+
- Recommended: Python 3.10+

## Development Notes

### Working Scripts (Verified)

- **`lancedb_data_dump.py`** - Successfully connects and explores data ✅
- **`lancedb_data_browser.py`** - Full Streamlit interface ✅
- **`test_all_methods.py`** - Tests different connection methods

### Legacy/Learning Scripts

- `simple_explorer.py`, `lancedb_browser.py` - Used wrong connection path
- `lance_direct_explorer.py` - Tried wrong package (lance vs lancedb)
- `create_table_from_lance.py` - Attempted to recreate existing table

### Common Issues & Solutions

- **Wrong connection path**: Use `lancedb.connect(".")` not `lancedb.connect("./whiskey_jack.lance")`
- **Missing tables**: The .lance directory IS the table, connect to parent
- **SQL queries fail**: Must use `.to_lance()` before DuckDB
- **Wrong package**: Use `lancedb` not `lance` or `pylance`

### Performance Considerations

- Use pagination for large datasets
- Cache database connections in Streamlit
- DuckDB SQL queries are efficient for aggregations
- Vector columns are `fixed_size_list<item: float>[1024]`
