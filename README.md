# LanceDB Transcript Analysis & Neo4j Integration Research

## Executive Summary

This repository documents a comprehensive investigation into connecting LanceDB call transcripts with the Neo4j POLE surveillance data model. Through systematic exploration and analysis, we've successfully established how to correlate transcripts with surveillance metadata and discovered key insights that will inform the next phase of graph database development.

### Key Discoveries
- ✅ **Direct correlation found** between Neo4j `sessionguid` and LanceDB `session_id`
- ✅ **100% match rate** for Telephony, Messaging, and Email sessions
- ✅ **71% of communications are under 50 words** - ideal for direct Neo4j integration
- ✅ **Neo4j 5's native GenAI features** can eliminate need for external vector processing

---

## Investigation Timeline & Tools

### Phase 1: LanceDB Exploration
Understanding the transcript database structure and access patterns

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| `analyze_data_model.py` | Initial data structure exploration | 325 chunks, 251 sessions, vector embeddings present |
| `lancedb_data_dump.py` | Console-based data exploration | Confirmed session aggregation approach |
| `lancedb_data_browser.py` | Professional Streamlit browser | Successfully visualized transcript data |

### Phase 2: Session Correlation Discovery
Investigating how to connect LanceDB transcripts with Neo4j surveillance data

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| `check_session_ids.py` | Compare session IDs between systems | **Breakthrough**: Direct ID correlation exists! |
| `test_connor_lookup.py` | Validate Connor's correlation approach | 100% success rate on sample data |
| `check_all_communications.py` | Analyze all communication types | Messaging, Email, and Telephony all correlate |

### Phase 3: Comprehensive Data Analysis
Understanding the nature and distribution of surveillance communications

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| `whiskey_jack_eda.py` | Exploratory Data Analysis | 50% are text messages (<20 words), 96% fit in single chunk |

---

## Quick Start Guide

### Installation
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Analysis Tools

#### 1. Basic Data Exploration
```bash
# View database structure and sample data
python analyze_data_model.py

# Console exploration with statistics
python lancedb_data_dump.py
```

#### 2. Professional Data Browser
```bash
# Launch interactive Streamlit application
streamlit run lancedb_data_browser.py
```

#### 3. Correlation Analysis (Key Discovery Scripts)
```bash
# Check session ID correlation - THE KEY DISCOVERY
python check_session_ids.py

# Test Connor's lookup approach
python test_connor_lookup.py

# Analyze all communication types
python check_all_communications.py
```

#### 4. Comprehensive Statistical Analysis
```bash
# Full exploratory data analysis
python whiskey_jack_eda.py
```

---

## Key Findings & Insights

### 1. Session Correlation Discovery
The investigation revealed that Neo4j `sessionguid` values directly match LanceDB `session_id` values, enabling seamless integration:

```python
# Connor's approach - validated through investigation
session_text_lookup = {session['session_id']: session['text'] for session in sessions}
transcript = session_text_lookup.get(neo4j_sessionguid)  # Works perfectly!
```

### 2. Communication Distribution
```
Total Sessions: 293 (across 325 chunks)

By Type:
├── Messaging (SMS/IM): 159 (60%)
├── Email: 50 (19%)
├── Telephony (Calls): 42 (16%)
└── Reports/Other: 14 (5%)

By Length:
├── Very Short (<20 words): 57% - Text messages
├── Short (20-50 words): 14% - Brief communications
├── Medium (50-200 words): 18% - Emails/short calls
└── Long (>200 words): 11% - Phone calls
```

### 3. Technical Architecture
```
Current State:
┌─────────────────┐          ┌──────────────────┐
│   Neo4j Graph   │ <--ID--> │  LanceDB Table   │
│  (Relationships)│  Match!  │  (Transcripts)   │
└─────────────────┘          └──────────────────┘

Next Phase:
┌─────────────────────────────────────────┐
│        Neo4j 5 with Native GenAI        │
│  • Relationships + Transcripts          │
│  • Vector Search + Full-text Search     │
│  • Single Database Solution             │
└─────────────────────────────────────────┘
```

---

## Documentation

| Document | Description |
|----------|-------------|
| `README.md` | This file - investigation overview and findings |
| `README_DATA_MODEL.md` | Detailed LanceDB schema documentation |
| `LANCEDB_CHEATSHEET.md` | Quick reference for LanceDB operations |
| `VERSION_COMPATIBILITY.md` | Package version requirements and issues |
| `CLAUDE.md` | AI assistant context for code understanding |

---

## Database Details

### LanceDB Structure
- **Database**: Current directory (`.`)
- **Table**: `whiskey_jack` (in `./whiskey_jack.lance/`)
- **Records**: 325 chunks from 251 unique sessions
- **Embeddings**: 1024-dimensional vectors (multilingual-e5-large-instruct)

### Connection Pattern
```python
import lancedb
import duckdb

# Connect to LanceDB
db = lancedb.connect(".")
table = db.open_table("whiskey_jack")

# Aggregate sessions using DuckDB SQL
whiskey_table = table.to_lance()
sql = """
SELECT session_id, STRING_AGG(text, ' ') as full_text
FROM whiskey_table 
GROUP BY session_id
"""
sessions = duckdb.query(sql).to_df()
```

---

## Next Steps

Based on this investigation, the next phase will focus on:

1. **Neo4j Integration**: Implementing the discovered correlation to enrich the POLE graph model
2. **Native Vector Search**: Leveraging Neo4j 5's GenAI capabilities for semantic search
3. **Unified Architecture**: Moving from dual-database to single Neo4j solution
4. **Advanced Analytics**: Topic extraction and conversation threading

*A comprehensive architectural design document has been prepared separately for strategic planning.*

---

## Technical Requirements

### Core Dependencies
```
lancedb==0.22.0       # Vector database
pylance==0.26.1       # Critical for .to_lance() method
duckdb==1.2.2         # SQL processing
pandas==2.2.3         # Data manipulation
pyarrow==20.0.0       # Arrow format support
streamlit             # Web interface
```

### Important Notes
- **Use `requirements.txt` for guaranteed compatibility**
- See `requirements_upgrade_notes.txt` for version flexibility research
- The `pylance` package is essential for SQL operations
- Virtual environment strongly recommended

---

**Investigation Period**: June 2025  
**Purpose**: Surveillance Data Integration Research  
**Result**: Successful correlation methodology established