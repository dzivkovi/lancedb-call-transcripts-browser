#!/usr/bin/env python3
"""
Export LanceDB transcripts for Neo4j import
Flexible JSON export with stdout/file output options
"""

import argparse
import json
import sys
import lancedb
import duckdb


def main():
    parser = argparse.ArgumentParser(
        description="Export LanceDB transcripts to JSON for Neo4j import",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Current dir → transcripts.json
  %(prog)s --data-dir ./data/case-alpha       # Case data → transcripts.json
  %(prog)s --data-dir /secure/ops/case-beta --table phone_records
  %(prog)s -o custom-output.json              # Custom output filename
  %(prog)s -o -                               # Explicit stdout
        """,
    )

    parser.add_argument(
        "-o",
        "--output",
        default="transcripts.json",
        help='Output file (default: transcripts.json, use "-" for stdout)',
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress messages (stderr only)",
    )

    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2, use 0 for compact)",
    )

    parser.add_argument(
        "--table",
        default="whiskey_jack",
        help="LanceDB table name (default: whiskey_jack)",
    )

    parser.add_argument(
        "--data-dir",
        default=".",
        help="Directory containing LanceDB tables (default: current directory)",
    )

    args = parser.parse_args()

    # Progress messages go to stderr if outputting to stdout
    output_to_stdout = args.output == "-"
    log_file = sys.stderr if output_to_stdout else sys.stdout

    def log(msg):
        if not args.quiet:
            print(msg, file=log_file)

    log("🔄 Exporting LanceDB transcripts for Neo4j...")

    # Connect using battle-tested pattern
    db = lancedb.connect(args.data_dir)
    table = db.open_table(args.table)
    whiskey_table = table.to_lance()

    log(f"📊 Total rows in LanceDB: {table.count_rows():,}")

    # Aggregate transcripts using proven SQL pattern with type info
    sql = """
    SELECT 
        session_id, 
        STRING_AGG(text, ' ') as full_text,
        COUNT(*) as chunk_count,
        FIRST(session_type) as session_type,
        FIRST(content_type) as content_type,
        FIRST(target) as target,
        FIRST(timestamp) as first_timestamp
    FROM 
        (SELECT * FROM whiskey_table ORDER BY timestamp, chunk_id ASC) 
    GROUP BY 
        session_id
    ORDER BY session_id
    """

    log("🔄 Running aggregation query...")
    result = duckdb.query(sql).fetchall()

    # Create transcript dictionary with type information
    transcripts = {}
    total_chars = 0
    type_counts = {"Telephony": 0, "Messaging": 0, "Email": 0}

    for (
        session_id,
        full_text,
        chunk_count,
        session_type,
        content_type,
        target,
        first_timestamp,
    ) in result:
        transcripts[session_id] = {
            "text": full_text,
            "chunk_count": chunk_count,
            "char_count": len(full_text),
            "session_type": session_type,
            "content_type": content_type,
            "target": target,
            "timestamp": first_timestamp,
        }
        total_chars += len(full_text)
        type_counts[session_type] = type_counts.get(session_type, 0) + 1

    log("📊 Aggregation complete:")
    log(f"   - {len(transcripts)} unique sessions")
    log(f"   - {total_chars:,} total characters")
    log(f"   - Average: {total_chars // len(transcripts):,} chars per session")
    log(f"   - 📞 Telephony: {type_counts.get('Telephony', 0)} calls")
    log(f"   - 💬 Messaging: {type_counts.get('Messaging', 0)} texts")
    log(f"   - 📧 Email: {type_counts.get('Email', 0)} emails")

    # Prepare JSON output
    json_output = json.dumps(
        transcripts, indent=args.indent if args.indent > 0 else None
    )

    # Output to stdout or file
    if output_to_stdout:
        print(json_output)
        log(f"✅ Exported {len(transcripts)} sessions to stdout")
    else:
        # If using default filename, put it in the data directory for proper case organization
        output_file = args.output
        if args.output == "transcripts.json" and args.data_dir != ".":
            output_file = f"{args.data_dir}/transcripts.json"

        with open(output_file, "w") as f:
            f.write(json_output)
        log(f"✅ Exported to: {output_file}")
        log(f"📁 File size: {len(json_output) / 1024 / 1024:.1f} MB")

    # Show sample (only if not quiet and not stdout)
    if not args.quiet and not output_to_stdout:
        sample_id = list(transcripts.keys())[0]
        sample = transcripts[sample_id]
        log("\n📝 Sample transcript:")
        log(f"   Session: {sample_id}")
        log(f"   Type: {sample['session_type']} ({sample['content_type']})")
        log(f"   Target: {sample['target']}")
        log(f"   Preview: {sample['text'][:150]}...")

    if not output_to_stdout:
        log("\n✅ Ready for Neo4j import!")


if __name__ == "__main__":
    main()
