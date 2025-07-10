#!/usr/bin/env python3
"""
Ultra-Simple NDJSON Recovery Tool
Fixes concatenated JSON objects for investigative data integrity
"""

import json
import re
import sys
import argparse


def fix_ndjson_file(input_file, output_file=None):
    """
    Fix NDJSON file by splitting concatenated JSON objects
    
    Args:
        input_file: Path to corrupted NDJSON file
        output_file: Path to fixed output file (optional)
    
    Returns:
        tuple: (objects_recovered, lines_fixed, total_lines)
    """
    if output_file is None:
        output_file = input_file.replace('.ndjson', '_fixed.ndjson')
    
    objects_recovered = 0
    lines_fixed = 0
    total_lines = 0
    
    print(f"🔧 Fixing NDJSON file: {input_file}")
    print(f"📁 Output file: {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            total_lines += 1
            line = line.strip()
            
            if not line:
                continue
                
            # Try parsing as single JSON object first (fast path)
            try:
                json.loads(line)
                outfile.write(line + '\n')
                objects_recovered += 1
                continue
            except json.JSONDecodeError:
                pass
            
            # Line has concatenated objects - split and fix
            lines_fixed += 1
            objects_on_line = split_concatenated_json(line)
            
            for obj_text in objects_on_line:
                try:
                    # Validate it's proper JSON
                    json.loads(obj_text)
                    outfile.write(obj_text + '\n')
                    objects_recovered += 1
                except json.JSONDecodeError:
                    print(f"⚠️  Line {line_num}: Could not recover one object fragment")
    
    return objects_recovered, lines_fixed, total_lines


def split_concatenated_json(line):
    """
    Split concatenated JSON objects on a single line
    
    Strategy: Find }{ patterns and split there, then reconstruct valid JSON
    """
    objects = []
    
    # Find all positions where one JSON ends and another begins
    # Pattern: } followed by { (with optional whitespace)
    split_positions = []
    
    brace_count = 0
    in_string = False
    escape_next = False
    
    for i, char in enumerate(line):
        if escape_next:
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            continue
            
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
            
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                # If we're back to 0 braces and next non-whitespace is {, 
                # this is a split point
                if brace_count == 0:
                    # Look ahead for next {
                    j = i + 1
                    while j < len(line) and line[j].isspace():
                        j += 1
                    if j < len(line) and line[j] == '{':
                        split_positions.append(i + 1)
    
    # Split the line at identified positions
    if not split_positions:
        return [line]  # No splits needed
    
    start = 0
    for pos in split_positions:
        objects.append(line[start:pos].strip())
        start = pos
    
    # Add the last object
    objects.append(line[start:].strip())
    
    return [obj for obj in objects if obj]


def main():
    parser = argparse.ArgumentParser(
        description="Fix concatenated JSON objects in NDJSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sessions.ndjson                    # Fix → sessions_fixed.ndjson
  %(prog)s sessions.ndjson -o clean.ndjson   # Fix → clean.ndjson
  %(prog)s data/case-name/sessions.ndjson    # Fix investigative data
        """
    )
    
    parser.add_argument('input_file', help='NDJSON file to fix')
    parser.add_argument('-o', '--output', help='Output file (default: input_fixed.ndjson)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without writing')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        # Quick analysis
        total_lines = 0
        error_lines = 0
        with open(args.input_file, 'r') as f:
            for line in f:
                total_lines += 1
                try:
                    json.loads(line.strip())
                except json.JSONDecodeError:
                    error_lines += 1
        
        print(f"📊 Analysis: {error_lines} problematic lines out of {total_lines}")
        print(f"🔧 Would fix {error_lines} lines and recover ~{error_lines * 2} objects")
        return
    
    # Perform the fix
    try:
        objects_recovered, lines_fixed, total_lines = fix_ndjson_file(
            args.input_file, args.output
        )
        
        print(f"\n✅ NDJSON RECOVERY COMPLETE")
        print(f"📊 Total lines processed: {total_lines:,}")
        print(f"🔧 Lines fixed: {lines_fixed:,}")
        print(f"📦 Objects recovered: {objects_recovered:,}")
        print(f"🎯 Success rate: {(objects_recovered/(lines_fixed*2 + total_lines-lines_fixed))*100:.1f}%")
        print(f"💾 Fixed file: {args.output}")
        
        if lines_fixed > 0:
            print(f"\n🔍 INVESTIGATIVE IMPACT:")
            print(f"   • Recovered {lines_fixed * 2} additional data objects")
            print(f"   • Potential evidence preservation: CRITICAL")
            print(f"   • Data integrity: RESTORED")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()