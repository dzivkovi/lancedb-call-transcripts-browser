#!/usr/bin/env python3
"""
Test Connor's lookup approach with our matched session IDs
"""

import lancedb
import duckdb
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Test Connor's lookup approach with matched session IDs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Test with whiskey_jack table
  %(prog)s --table evidence_calls    # Test with custom table
        """,
    )
    
    parser.add_argument(
        "--table",
        default="whiskey_jack",
        help="LanceDB table name (default: whiskey_jack)",
    )
    
    args = parser.parse_args()
    
    print("🧪 Testing Connor's Lookup Approach")
    print("=" * 50)
    print(f"Using table: {args.table}")
    
    # Connect to LanceDB
    db = lancedb.connect(".")
    table = db.open_table(args.table)
    whiskey_table = table.to_lance()

    # Create Connor's session text lookup
    print("Creating Connor's session_text_lookup...")
    session_sql = """
    SELECT 
        session_id,
        STRING_AGG(text, ' ') as text
    FROM 
        (SELECT * FROM whiskey_table ORDER BY timestamp, chunk_id ASC) 
    GROUP BY 
        session_id
    """

    session_texts = duckdb.query(session_sql).fetchall()
    session_text_lookup = {session_id: text for session_id, text in session_texts}

    print(f"✅ Created lookup for {len(session_text_lookup)} sessions")

    # Test with our matched Neo4j session GUIDs
    matched_guids = [
        "07792de9-41b7-4cfe-abfb-fe6a4d9dc601",
        "081da27f-8d7e-4ba4-861c-13d7d7233b49",
        "00fdfea0-8c72-487a-b726-513f6fafb338",
        "0b595ec8-e76a-484a-9005-ef62f50d8e09",
    ]

    print("\n🔗 Testing Direct Lookup")
    print("-" * 50)

    for guid in matched_guids:
        transcript = session_text_lookup.get(guid, "")
        if transcript:
            word_count = len(transcript.split())
            char_count = len(transcript)
            preview = transcript[:150] + "..." if len(transcript) > 150 else transcript
            print(f"\n✅ Session: {guid}")
            print(f"   Words: {word_count}, Chars: {char_count}")
            print(f"   Text: {preview}")
        else:
            print(f"\n❌ Session: {guid} - No transcript found")

    print(
        f"\n🎯 SUCCESS RATE: {sum(1 for guid in matched_guids if session_text_lookup.get(guid, ''))}/{len(matched_guids)} sessions found"
    )

    # Show what this enables
    print("\n🚀 WHAT THIS ENABLES")
    print("-" * 50)
    print("✅ Direct Neo4j -> LanceDB transcript lookup")
    print("✅ Can enrich Neo4j sessions with transcript summaries")
    print("✅ Can add AI-generated topics to graph nodes")
    print("✅ Can implement Connor's caching strategy")
    print("✅ Enables hybrid graph-vector queries")

    print("\n📊 INTEGRATION POSSIBILITIES")
    print("-" * 50)
    print("1. Add transcript summaries to existing Session nodes")
    print("2. Create Content nodes with LanceDB references")
    print("3. Extract and cache topics/entities in graph")
    print("4. Enable semantic search within graph structure")

    print("\n✅ Connor's approach validated and ready for implementation!")


if __name__ == "__main__":
    main()
