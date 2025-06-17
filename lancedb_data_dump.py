#!/usr/bin/env python3
"""
Final Working LanceDB Explorer
Uses the existing whiskey_jack table in current directory
"""

import lancedb
import duckdb
import pandas as pd

def explore_existing_table():
    """Explore the existing whiskey_jack table"""
    print("🔗 Connecting to LanceDB in current directory...")
    
    try:
        # Connect to current directory
        db = lancedb.connect(".")
        tables = db.table_names()
        print(f"✅ Connected! Found tables: {tables}")
        
        # Open the whiskey_jack table
        table_name = "whiskey_jack"
        if table_name not in tables:
            print(f"❌ Table '{table_name}' not found. Available: {tables}")
            return False
        
        print(f"\n📊 Opening table: {table_name}")
        table = db.open_table(table_name)
        
        # Get schema
        schema = table.schema
        print(f"\n📋 Schema ({len(schema)} columns):")
        for field in schema:
            print(f"   - {field.name}: {field.type}")
        
        # Get row count
        try:
            count = table.count_rows()
            print(f"\n📊 Total rows: {count:,}")
        except Exception as e:
            print(f"📊 Row count error: {e}")
            count = None
        
        # Sample data
        print(f"\n👀 Sample data (first 5 rows):")
        sample = table.to_pandas().head(5)
        print(sample.to_string())
        
        # Check for expected columns
        expected_cols = ['session_id', 'timestamp', 'text', 'chunk_id', 'run_id']
        print(f"\n✅ Column check:")
        found_cols = []
        for col in expected_cols:
            if col in sample.columns:
                print(f"   ✓ {col}: Found")
                found_cols.append(col)
            else:
                print(f"   ✗ {col}: Missing")
        
        # Try Connor's SQL aggregation
        if all(col in found_cols for col in ['session_id', 'timestamp', 'text']):
            print(f"\n🔄 Testing Connor's SQL aggregation...")
            try:
                # Convert to Lance dataset for DuckDB
                whiskey_table = table.to_lance()
                
                sql = """
                SELECT 
                    session_id,
                    FIRST(timestamp) as timestamp,
                    STRING_AGG(text, ' ') as text
                FROM 
                    (SELECT * FROM whiskey_table ORDER BY timestamp, chunk_id ASC) 
                GROUP BY 
                    session_id
                """
                
                result_df = duckdb.query(sql).to_df()
                result_df = result_df.drop_duplicates(subset=['timestamp', 'text'], keep='first')
                
                print(f"✅ SQL aggregation successful!")
                print(f"📊 Aggregated {len(result_df)} unique sessions")
                
                # Show sample aggregated results
                print(f"\n📋 Sample aggregated session:")
                if not result_df.empty:
                    sample_session = result_df.iloc[0]
                    print(f"Session ID: {sample_session['session_id']}")
                    print(f"Timestamp: {sample_session['timestamp']}")
                    print(f"Text length: {len(sample_session['text'])} characters")
                    print(f"Text preview: {sample_session['text'][:200]}...")
                
                # Create session lookup
                session_text_lookup = {
                    row['session_id']: row['text'] 
                    for _, row in result_df.iterrows()
                }
                
                print(f"\n📝 Created session lookup with {len(session_text_lookup)} entries")
                
            except Exception as e:
                print(f"❌ SQL aggregation failed: {e}")
                print("💡 This might be due to missing columns or different schema")
        else:
            print(f"\n⚠️ Missing required columns for aggregation")
            print(f"Found: {found_cols}")
            print(f"Need: session_id, timestamp, text")
        
        # Show some statistics
        if not sample.empty:
            print(f"\n📈 Data Statistics:")
            if 'session_id' in sample.columns:
                unique_sessions = sample['session_id'].nunique()
                print(f"Unique sessions in sample: {unique_sessions}")
                print(f"Sample session IDs: {list(sample['session_id'].unique()[:5])}")
            
            if 'timestamp' in sample.columns:
                print(f"Timestamp range: {sample['timestamp'].min()} to {sample['timestamp'].max()}")
            
            if 'text' in sample.columns:
                text_lengths = sample['text'].str.len()
                print(f"Text length stats:")
                print(f"  - Min: {text_lengths.min()} chars")
                print(f"  - Max: {text_lengths.max()} chars")
                print(f"  - Mean: {text_lengths.mean():.0f} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Final Working LanceDB Explorer")
    print("=" * 50)
    
    success = explore_existing_table()
    
    if success:
        print("\n✅ Successfully explored the whiskey_jack table!")
        print("💡 You can now use:")
        print("   streamlit run final_working_browser.py")
    else:
        print("\n❌ Exploration failed")
        print("But we know the table exists - check error messages above")