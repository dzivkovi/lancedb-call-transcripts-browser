# LanceDB Data Model Documentation

## Overview

This document explains the data structure of the `whiskey_jack` LanceDB table containing phone call transcripts that have been processed through a text chunking and vector embedding pipeline.

## Table Schema

The LanceDB table contains **325 rows** across **13 columns**:

| # | Column Name | Data Type | Description |
|---|-------------|-----------|-------------|
| 0 | text | string | The actual transcript text (chunked) |
| 1 | vector | fixed_size_list<item: float>[1024] | Vector embedding (1024 dimensions) |
| 2 | logical_key | string | Unique identifier for the chunk |
| 3 | chunk_id | int64 | Order of chunk within session (0-10) |
| 4 | run_id | int64 | Processing run identifier |
| 5 | timestamp | int64 | Unix timestamp of the call |
| 6 | target | string | Call participant identifier |
| 7 | line | string | Phone line identifier |
| 8 | session_id | string | Unique call session identifier |
| 9 | product_id | string | Product/service identifier |
| 10 | session_type | string | Type of session (e.g., "Telephony") |
| 11 | content_type | string | Content format (e.g., "audio/x-wav") |
| 12 | fifteen_minutes_of_week | int64 | Time bucketing for analytics |

## Data Statistics

- **Total Records**: 325 text chunks
- **Unique Sessions**: 251 phone calls
- **Participants**: 6 unique callers
- **Time Range**: February 2020 to January 2023
- **Text Length**: 2-1,931 characters per chunk (average: 355 chars)
- **Chunk Range**: 0-10 chunks per session

## Key Participants

- @Eagles Maintenance and Landscaping (business)
- @William Eagle
- @Kenzie Hawk  
- @Fred Merlin
- @Richard (Benny) Eagle

## Raw Data vs Aggregated Sessions

### Raw Data Browser Shows:
**Individual text CHUNKS** - each row represents one piece of a conversation.

Example from session `d4f60749-2577-49eb-be5d-1977c84aa2a2`:
```
Chunk 1: "Eagles Maintenance and Landscaping. Hi, Carrie. Is Bill there? Oh, hi, Bev. He's out back talking to..."
Chunk 2: "...Benny. Okay, I'll try him later. If I don't get him, will you tell him to call me? Sure. Thanks. Bye. Adios."
```

### Session Transcripts Shows:
**Complete conversations** - all chunks combined using SQL aggregation.

Example aggregated session:
```
Session: 61ba61fb-e22c-4f78-a56f-ed6b7e2ee126
Participant: @William Eagle
Complete Text: "Hey brother wanted to tell you that Kenzie's doin a great job with the expansion here. Her new promotion is goin great guns."
```

## Data Processing Pipeline

```
1. Raw Phone Call Recordings
   ↓
2. Speech-to-Text Transcription  
   ↓
3. Text Chunking (SentenceChunker)
   ↓
4. Vector Embedding (multilingual-e5-large-instruct)
   ↓
5. LanceDB Storage with Metadata
```

### Chunking Strategy
- **Model**: multilingual-e5-large-instruct (512 token context window)
- **Chunker**: chonkie's SentenceChunker
- **Overlap**: No overlap between chunks
- **Purpose**: Each chunk gets its own 1024-dimensional vector embedding

## Why Chunking?

1. **Model Limitations**: Embedding models have token limits (512 tokens for multilingual-e5-large-instruct)
2. **Semantic Search**: Enables fine-grained search within conversations
3. **RAG Applications**: Better for Retrieval Augmented Generation
4. **Context Matching**: Can find specific parts of conversations
5. **Scalability**: More efficient for large datasets

## SQL Aggregation Example

To reconstruct complete conversations from chunks:

```sql
SELECT 
    session_id,
    FIRST(timestamp) as first_timestamp,
    STRING_AGG(text, ' ') as full_text,
    COUNT(*) as chunk_count,
    FIRST(target) as participant
FROM 
    (SELECT * FROM whiskey_table ORDER BY timestamp, chunk_id ASC) 
GROUP BY 
    session_id
ORDER BY first_timestamp DESC
```

## Use Cases

### Raw Data Browser
- Debug chunking quality
- Analyze individual text segments  
- Study embedding effectiveness
- Quality control on text processing
- Examine chunk boundaries

### Session Transcripts
- Read complete conversations
- Human-readable call analysis
- Export full call transcripts
- Business intelligence on customer calls
- Conversation flow analysis

## Vector Embeddings

- **Dimensions**: 1024 float values per chunk
- **Model**: intfloat/multilingual-e5-large-instruct
- **Purpose**: Semantic search and similarity matching
- **Storage**: Each vector is ~4KB (1024 × 4 bytes)

## Time Information

- **Timestamps**: Unix epoch format (e.g., 1581080007)
- **Readable Range**: 2020-02-06 17:08:33 to 2023-01-03 13:13:11
- **Bucketing**: `fifteen_minutes_of_week` for time-based analytics

## Sample Data

### Chunk Example
```json
{
  "text": "Hello? Hi. Listen, I called Ray and he said he'll call his guy in Columbia...",
  "session_id": "a2d66017-92f2-4259-ac46-ef10058ceab1",
  "chunk_id": 0,
  "timestamp": 1581260062,
  "target": "@William Eagle",
  "participant_count": 1,
  "text_length": 355
}
```

### Aggregated Session Example  
```json
{
  "session_id": "61ba61fb-e22c-4f78-a56f-ed6b7e2ee126",
  "participant": "@William Eagle", 
  "chunk_count": 1,
  "total_text_length": 123,
  "full_text": "Hey brother wanted to tell you that Kenzie's doin a great job with the expansion here. Her new promotion is goin great guns.",
  "timestamp": "2020-02-06 12:08:33"
}
```

## Accessing the Data

### Python Connection
```python
import lancedb
import duckdb

# Connect to database
db = lancedb.connect(".")
table = db.open_table("whiskey_jack")

# Get raw chunks
df = table.to_pandas()

# Aggregate sessions
lance_data = table.to_lance()
sessions = duckdb.query("SELECT session_id, STRING_AGG(text, ' ') FROM lance_data GROUP BY session_id").to_df()
```

### Browser Interface
- **Raw Data Browser**: `streamlit run lancedb_data_browser.py`
- **Excel-style navigation** with pagination
- **Export capabilities** for CSV downloads
- **Search functionality** across all text content

This data model enables both detailed chunk-level analysis and high-level conversation review, making it suitable for various business intelligence and AI applications.