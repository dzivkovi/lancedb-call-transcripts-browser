#!/usr/bin/env python3
"""
Check session ID correlation between Neo4j and LanceDB
"""

import argparse
import lancedb
import duckdb


def main():
    parser = argparse.ArgumentParser(
        description="Check session ID correlation between Neo4j and LanceDB"
    )
    parser.add_argument(
        "--table",
        default="whiskey_jack",
        help="LanceDB table name (default: whiskey_jack)",
    )
    args = parser.parse_args()

    print("🔍 Checking Session ID Correlation Between Neo4j and LanceDB")
    print("=" * 70)

    # Connect to LanceDB
    db = lancedb.connect(".")
    table = db.open_table(args.table)

    whiskey_table = table.to_lance()

    # Get unique session IDs from LanceDB
    print("\n📊 LanceDB Session IDs")
    print("-" * 50)

    session_sql = """
    SELECT DISTINCT session_id
    FROM whiskey_table
    ORDER BY session_id
    LIMIT 10
    """

    lancedb_sessions = duckdb.query(session_sql).fetchall()
    print("Sample LanceDB session_ids:")
    for session in lancedb_sessions:
        print(f"  {session[0]}")

    print(
        f"\nTotal unique LanceDB sessions: {len(duckdb.query('SELECT DISTINCT session_id FROM whiskey_table').fetchall())}"
    )

    # Test Connor's approach - get a mapping
    print("\n🔗 Testing Connor's Lookup Approach")
    print("-" * 50)

    # Create session text lookup like Connor did
    session_text_sql = """
    SELECT 
        session_id,
        STRING_AGG(text, ' ') as full_text
    FROM 
        (SELECT * FROM whiskey_table ORDER BY timestamp, chunk_id ASC) 
    GROUP BY 
        session_id
    ORDER BY session_id
    LIMIT 5
    """

    session_texts = duckdb.query(session_text_sql).fetchall()
    print("Sample session_id -> text mappings:")
    for session_id, text in session_texts:
        preview = text[:100] + "..." if len(text) > 100 else text
        print(f"\nSession: {session_id}")
        print(f"Text: {preview}")

    # Neo4j telephony session GUIDs (from our previous query)
    neo4j_guids = [
        "00fdfea0-8c72-487a-b726-513f6fafb338",
        "07792de9-41b7-4cfe-abfb-fe6a4d9dc601",
        "081da27f-8d7e-4ba4-861c-13d7d7233b49",
        "0b595ec8-e76a-484a-9005-ef62f50d8e09",
        "1babd75a-1e15-4823-87ac-ee2952a53af4",
    ]

    lancedb_session_ids = [session[0] for session in lancedb_sessions]

    print("\n📋 COMPARISON RESULTS")
    print("-" * 50)
    print("Neo4j sample sessionguids:")
    for guid in neo4j_guids:
        print(f"  {guid}")

    print("\nLanceDB sample session_ids:")
    for sid in lancedb_session_ids:
        print(f"  {sid}")

    # Check for any matches
    matches = set(neo4j_guids) & set(lancedb_session_ids)
    print(f"\n🎯 Direct matches found: {len(matches)}")
    if matches:
        print("Matching IDs:")
        for match in matches:
            print(f"  ✅ {match}")
    else:
        print("❌ No direct ID matches found")

    print("\n🔍 ANALYSIS")
    print("-" * 50)
    if matches:
        print("✅ Connor's approach will work! Session IDs match between systems.")
        print("You can use direct lookup: session_text_lookup.get(sessionguid)")
    else:
        print("❌ Connor's direct approach won't work. Session IDs don't match.")
        print("Need to create a mapping strategy or investigate ID generation.")

    print("\n✅ Analysis Complete!")


if __name__ == "__main__":
    main()
