#!/usr/bin/env python3
"""
Comprehensive Exploratory Data Analysis for whiskey_jack LanceDB table
Consolidates all EDA approaches into a single, definitive analysis
"""

import lancedb
import duckdb
import sys
from datetime import datetime

# Try to import pandas for enhanced analysis, but work without it if needed
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    print("Note: pandas not available, using basic analysis")
    HAS_PANDAS = False

def main():
    print("🔍 Comprehensive EDA - whiskey_jack LanceDB Table")
    print("=" * 70)
    
    # Connect to LanceDB
    db = lancedb.connect(".")
    table = db.open_table("whiskey_jack")
    
    # Basic table info
    print("\n📊 TABLE OVERVIEW")
    print("-" * 50)
    total_chunks = table.count_rows()
    print(f"Total chunks in table: {total_chunks:,}")
    
    # Schema information
    schema = table.schema
    field_names = [field.name for field in schema]
    print(f"\nSchema fields ({len(field_names)}):")
    for field in field_names:
        print(f"  - {field}")
    
    # Convert to Lance format for DuckDB
    whiskey_table = table.to_lance()
    
    # Basic statistics using DuckDB
    print("\n📈 CHUNK-LEVEL STATISTICS")
    print("-" * 50)
    
    stats_sql = """
    SELECT 
        COUNT(DISTINCT session_id) as unique_sessions,
        COUNT(DISTINCT run_id) as unique_runs,
        COUNT(DISTINCT CONCAT(session_id, '|', run_id)) as unique_session_runs,
        COUNT(*) as total_chunks,
        AVG(LENGTH(text)) as avg_chunk_length,
        MIN(LENGTH(text)) as min_chunk_length,
        MAX(LENGTH(text)) as max_chunk_length,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY LENGTH(text)) as median_chunk_length
    FROM whiskey_table
    """
    
    stats = duckdb.query(stats_sql).fetchone()
    print(f"Unique session IDs: {stats[0]:,}")
    print(f"Unique run IDs: {stats[1]:,}")
    print(f"Unique session-run combinations: {stats[2]:,}")
    print(f"Total chunks: {stats[3]:,}")
    print(f"Average chunk length: {stats[4]:.0f} characters")
    print(f"Median chunk length: {stats[7]:.0f} characters")
    print(f"Min chunk length: {stats[5]} characters")
    print(f"Max chunk length: {stats[6]} characters")
    
    # Chunk distribution
    print("\nChunks per session distribution:")
    chunk_dist_sql = """
    SELECT 
        chunks_per_session,
        COUNT(*) as session_count
    FROM (
        SELECT 
            CONCAT(session_id, '|', run_id) as session_run,
            COUNT(*) as chunks_per_session
        FROM whiskey_table
        GROUP BY session_id, run_id
    )
    GROUP BY chunks_per_session
    ORDER BY chunks_per_session
    """
    
    chunk_dist = duckdb.query(chunk_dist_sql).fetchall()
    total_sessions = sum(count for _, count in chunk_dist)
    for chunks, count in chunk_dist[:10]:  # Show first 10
        pct = count/total_sessions*100
        print(f"  {chunks} chunk{'s' if chunks > 1 else ''}: {count} sessions ({pct:.1f}%)")
    
    # Reconstruct full sessions
    print("\n🔄 FULL SESSION RECONSTRUCTION")
    print("-" * 50)
    print("Aggregating chunks into complete sessions...")
    
    # IMPORTANT: Group by both session_id AND run_id for accurate reconstruction
    session_sql = """
    SELECT 
        session_id,
        run_id,
        STRING_AGG(text, ' ') as full_text,
        COUNT(*) as chunk_count,
        MIN(timestamp) as first_timestamp,
        MAX(timestamp) as last_timestamp,
        STRING_AGG(content_type, ', ') as content_types
    FROM 
        (SELECT * FROM whiskey_table ORDER BY timestamp, chunk_id ASC) 
    GROUP BY 
        session_id, run_id
    ORDER BY 
        MIN(timestamp)
    """
    
    sessions = duckdb.query(session_sql).fetchall()
    print(f"✓ Reconstructed {len(sessions):,} complete sessions")
    
    # Analyze sessions
    print("\n📝 SESSION-LEVEL ANALYSIS")
    print("-" * 50)
    
    # Process all sessions
    session_stats = []
    very_short = []  # <20 words
    short = []       # 20-50 words
    medium = []      # 50-200 words
    long = []        # >200 words
    
    total_words = 0
    total_chars = 0
    
    for session in sessions:
        session_id, run_id, full_text, chunk_count, first_ts, last_ts, content_types = session
        
        char_count = len(full_text)
        word_count = len(full_text.split())
        
        total_words += word_count
        total_chars += char_count
        
        session_data = {
            'session_id': session_id,
            'run_id': run_id,
            'word_count': word_count,
            'char_count': char_count,
            'chunk_count': chunk_count,
            'text_preview': full_text[:200]
        }
        
        # Categorize by word count
        if word_count < 20:
            very_short.append(session_data)
        elif word_count < 50:
            short.append(session_data)
        elif word_count < 200:
            medium.append(session_data)
        else:
            long.append(session_data)
        
        session_stats.append(session_data)
    
    # Calculate statistics
    avg_words = total_words / len(sessions) if sessions else 0
    avg_chars = total_chars / len(sessions) if sessions else 0
    avg_chunks = total_chunks / len(sessions) if sessions else 0
    
    print(f"Average session length: {avg_chars:.0f} characters, {avg_words:.0f} words")
    print(f"Average chunks per session: {avg_chunks:.1f}")
    print(f"Total content volume: {total_words:,} words, {total_chars:,} characters")
    
    # Content type breakdown
    print("\n📱 CONTENT TYPE ANALYSIS")
    print("-" * 50)
    print(f"Very short (<20 words) - Text messages: {len(very_short):,} ({len(very_short)/len(sessions)*100:.1f}%)")
    print(f"Short (20-50 words) - Short texts/calls: {len(short):,} ({len(short)/len(sessions)*100:.1f}%)")
    print(f"Medium (50-200 words) - Brief conversations: {len(medium):,} ({len(medium)/len(sessions)*100:.1f}%)")
    print(f"Long (>200 words) - Phone calls: {len(long):,} ({len(long)/len(sessions)*100:.1f}%)")
    
    # Show examples
    print("\n💬 SAMPLE TEXT MESSAGES (Very Short Sessions)")
    print("-" * 50)
    for i, session in enumerate(very_short[:5]):
        print(f"\nExample {i+1} - Session {session['session_id'][:8]}... ({session['word_count']} words):")
        text = session['text_preview'].strip()
        if len(text) > 150:
            text = text[:150] + "..."
        print(f'  "{text}"')
    
    # Volume distribution
    print("\n📊 WORD DISTRIBUTION BY CONTENT TYPE")
    print("-" * 50)
    
    very_short_words = sum(s['word_count'] for s in very_short)
    short_words = sum(s['word_count'] for s in short)
    medium_words = sum(s['word_count'] for s in medium)
    long_words = sum(s['word_count'] for s in long)
    
    print(f"Text messages: {very_short_words:,} words ({very_short_words/total_words*100:.1f}% of total)")
    print(f"Short messages: {short_words:,} words ({short_words/total_words*100:.1f}% of total)")
    print(f"Brief conversations: {medium_words:,} words ({medium_words/total_words*100:.1f}% of total)")
    print(f"Phone calls: {long_words:,} words ({long_words/total_words*100:.1f}% of total)")
    
    # Advanced statistics if pandas available
    if HAS_PANDAS and session_stats:
        print("\n📊 DETAILED STATISTICS (with pandas)")
        print("-" * 50)
        
        df = pd.DataFrame(session_stats)
        
        print("\nWord count percentiles:")
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        for p in percentiles:
            val = df['word_count'].quantile(p/100)
            print(f"  {p}th percentile: {val:.0f} words")
        
        print(f"\nStandard deviation: {df['word_count'].std():.1f} words")
        print(f"Variance: {df['word_count'].var():.1f}")
    
    # Key insights and summary
    print("\n🔍 KEY INSIGHTS & SUMMARY")
    print("-" * 50)
    
    # Call duration estimates
    avg_call_duration = avg_words / 150  # 150 words/minute
    long_call_avg = sum(s['word_count'] for s in long) / len(long) if long else 0
    long_call_duration = long_call_avg / 150
    
    print(f"• Dataset contains {len(sessions):,} sessions from {total_chunks:,} chunks")
    print(f"• Average session: {avg_words:.0f} words ({avg_call_duration:.1f} minutes @ 150 wpm)")
    print(f"• Average phone call: {long_call_avg:.0f} words ({long_call_duration:.1f} minutes)")
    
    print(f"\n• Content breakdown:")
    print(f"  - {len(very_short)/len(sessions)*100:.0f}% are text messages (<20 words)")
    print(f"  - {len(long)/len(sessions)*100:.0f}% are phone calls (>200 words)")
    print(f"  - {(len(short)+len(medium))/len(sessions)*100:.0f}% are short calls/mixed content")
    
    print(f"\n• Volume metrics:")
    print(f"  - Total: {total_words:,} words (~{total_words/250:.0f} pages @ 250 words/page)")
    print(f"  - Text messages: {very_short_words/total_words*100:.0f}% of words despite being {len(very_short)/len(sessions)*100:.0f}% of sessions")
    print(f"  - Phone calls: {long_words/total_words*100:.0f}% of words from just {len(long)/len(sessions)*100:.0f}% of sessions")
    
    print(f"\n• Chunking efficiency:")
    print(f"  - Average {avg_chunks:.1f} chunks per session")
    print(f"  - {sum(1 for s in session_stats if s['chunk_count'] == 1)/len(sessions)*100:.0f}% of sessions fit in a single chunk")
    print(f"  - Using multilingual-e5-large-instruct embeddings (512 token window)")
    
    # Data quality notes
    print("\n⚠️ DATA QUALITY NOTES")
    print("-" * 50)
    print("• Timestamps appear to be Unix epoch (1970-01-01) - may need conversion")
    print("• Multiple run_ids per session_id suggest multiple processing runs")
    print(f"• Unique session-run combinations: {len(sessions):,}")
    
    print("\n✅ Analysis Complete!")

if __name__ == "__main__":
    main()