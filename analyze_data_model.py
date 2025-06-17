#!/usr/bin/env python3
"""
Analyze LanceDB Data Model
Show the difference between raw chunks and aggregated sessions
"""

import lancedb
import duckdb
import pandas as pd
from datetime import datetime

def analyze_data_model():
    """Analyze the LanceDB data structure"""
    
    print("=" * 80)
    print("LANCEDB DATA MODEL ANALYSIS")
    print("=" * 80)
    
    # Connect
    db = lancedb.connect(".")
    table = db.open_table("whiskey_jack")
    
    print("\n1. TABLE SCHEMA")
    print("-" * 40)
    schema = table.schema
    for i, field in enumerate(schema):
        print(f"{i:2d}. {field.name:25} | {str(field.type):30} | Nullable: {field.nullable}")
    
    print(f"\nTotal columns: {len(schema)}")
    print(f"Total rows: {table.count_rows():,}")
    
    # Load sample data
    df = table.to_pandas()
    
    print("\n2. RAW DATA STRUCTURE")
    print("-" * 40)
    print("This is what you see in 'Raw Data Browser':")
    print("Each row = ONE TEXT CHUNK from a conversation")
    
    # Show sample chunks from one session
    sample_session = df['session_id'].iloc[0]
    session_chunks = df[df['session_id'] == sample_session].sort_values(['timestamp', 'chunk_id'])
    
    print(f"\nExample: Session {sample_session}")
    print(f"This session has {len(session_chunks)} chunks:")
    
    for i, (_, chunk) in enumerate(session_chunks.iterrows()):
        print(f"\nChunk {i+1} (chunk_id: {chunk['chunk_id']}):")
        print(f"  Timestamp: {datetime.fromtimestamp(chunk['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Text: {chunk['text'][:100]}...")
        print(f"  Length: {len(chunk['text'])} characters")
    
    print("\n3. AGGREGATED SESSION STRUCTURE")
    print("-" * 40)
    print("This is what you see in 'Complete Session Transcripts':")
    print("Multiple chunks are combined into one complete conversation")
    
    # Show aggregation SQL
    lance_data = table.to_lance()
    
    sql = """
    SELECT 
        session_id,
        COUNT(*) as chunk_count,
        FIRST(timestamp) as first_timestamp,
        STRING_AGG(text, ' ') as full_text,
        FIRST(target) as participant
    FROM 
        (SELECT * FROM lance_data ORDER BY timestamp, chunk_id ASC) 
    GROUP BY 
        session_id
    ORDER BY first_timestamp
    LIMIT 3
    """
    
    aggregated = duckdb.query(sql).to_df()
    
    print(f"\nExample aggregated sessions:")
    for i, (_, session) in enumerate(aggregated.iterrows()):
        print(f"\nSession {i+1}: {session['session_id']}")
        print(f"  Participant: {session['participant']}")
        print(f"  Chunks combined: {session['chunk_count']}")
        print(f"  Total text length: {len(session['full_text']):,} characters")
        print(f"  First timestamp: {datetime.fromtimestamp(session['first_timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Text preview: {session['full_text'][:150]}...")
    
    print("\n4. KEY DIFFERENCES")
    print("-" * 40)
    print("RAW DATA BROWSER:")
    print("  - Shows individual text CHUNKS")
    print("  - Each row = one piece of a conversation")
    print("  - May be partial sentences or phrases")
    print("  - Good for detailed analysis of chunking strategy")
    
    print("\nSESSION TRANSCRIPTS:")
    print("  - Shows COMPLETE conversations")
    print("  - All chunks for a session combined with STRING_AGG")
    print("  - Ordered by timestamp and chunk_id")
    print("  - Full readable conversation flow")
    
    print("\n5. DATA PIPELINE EXPLANATION")
    print("-" * 40)
    print("Original Process:")
    print("1. Raw phone call recordings")
    print("2. Speech-to-text transcription")
    print("3. Text chunking (using SentenceChunker)")
    print("4. Vector embedding (multilingual-e5-large-instruct)")
    print("5. Storage in LanceDB with metadata")
    
    print("\nChunking Strategy:")
    print("- Model: multilingual-e5-large-instruct (512 token context)")
    print("- Chunker: chonkie's SentenceChunker")
    print("- No overlap between chunks")
    print("- Each chunk gets its own vector embedding")
    
    print("\n6. COLUMN ANALYSIS")
    print("-" * 40)
    
    # Analyze key columns
    key_columns = ['session_id', 'text', 'chunk_id', 'timestamp', 'target', 'vector']
    
    for col in key_columns:
        if col in df.columns:
            print(f"\n{col}:")
            if col == 'session_id':
                unique_count = df[col].nunique()
                print(f"  - {unique_count} unique sessions")
                print(f"  - Example: {df[col].iloc[0]}")
            elif col == 'text':
                lengths = df[col].str.len()
                print(f"  - Chunk lengths: {lengths.min()}-{lengths.max()} chars (avg: {lengths.mean():.0f})")
                print(f"  - Example: {df[col].iloc[0][:100]}...")
            elif col == 'chunk_id':
                print(f"  - Range: {df[col].min()}-{df[col].max()}")
                print(f"  - Purpose: Ordering chunks within a session")
            elif col == 'timestamp':
                timestamps = pd.to_datetime(df[col], unit='s')
                print(f"  - Range: {timestamps.min()} to {timestamps.max()}")
                print(f"  - Purpose: Chronological ordering")
            elif col == 'target':
                unique_targets = df[col].unique()[:5]
                print(f"  - Participants: {len(df[col].unique())} unique")
                print(f"  - Examples: {', '.join(map(str, unique_targets))}")
            elif col == 'vector':
                vector_sample = df[col].iloc[0]
                if isinstance(vector_sample, list):
                    print(f"  - Dimensions: {len(vector_sample)}")
                    print(f"  - Type: Embedding vector for semantic search")
                    print(f"  - Example values: {vector_sample[:5]}...")
    
    print("\n7. STORAGE EFFICIENCY")
    print("-" * 40)
    print("Why chunk instead of storing full conversations?")
    print("1. Vector embedding models have token limits (512 for this model)")
    print("2. Chunking allows fine-grained semantic search")
    print("3. Can find specific parts of conversations")
    print("4. Better for RAG (Retrieval Augmented Generation)")
    print("5. Enables more precise context matching")
    
    print("\n8. USE CASES")
    print("-" * 40)
    print("Raw Data Browser:")
    print("- Debug chunking quality")
    print("- Analyze individual segments")
    print("- Study embedding effectiveness")
    print("- Quality control on processing")
    
    print("\nSession Transcripts:")
    print("- Read complete conversations")
    print("- Human-readable analysis")
    print("- Export full call transcripts")
    print("- Business intelligence on calls")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_data_model()