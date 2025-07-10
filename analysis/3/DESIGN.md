# Flexible Directory Support + Standard Output Contract for POLE Investigations

## Problem / Metric

Current LanceDB scripts are hardcoded to work only from project root directory (`lancedb.connect(".")`), limiting their use for:
- Case-based investigations stored in separate directories (e.g., `./data/case-alpha/`, `/secure/investigations/operation-x/`)
- POLE-model policing workflows where each case has its own data directory
- Consolidation with other investigation tools (neo4j-for-surveillance-poc-3) requiring consistent CLI patterns
- PII-sensitive investigations requiring data isolation in specific directories

**Current State**: Scripts only work from project root with tables in current directory
**Target State**: Scripts work with any directory structure while maintaining standard output contracts

**File Organization** (to be implemented before this feature):
```
data/
└── whiskey-jack/              # Consolidated case directory
    ├── sessions.ndjson        # Input: surveillance metadata
    ├── whiskey_jack.lance/    # LanceDB table
    └── transcripts.json       # Output: for Neo4j import
```

## Goal

Enable LanceDB investigation scripts to:
1. Access LanceDB tables from any directory location on disk
2. Provide standard output file contract (`transcripts.json`) across all investigations  
3. Support case-based investigation workflows for policing/POLE model
4. Maintain full backward compatibility with existing usage
5. Establish foundation for unified CLI patterns across investigation tools

## Scope (M/S/W)

- [M] Add `--data-dir` argument to all 4 core LanceDB scripts with current directory default
- [M] Change default output from stdout to `transcripts.json` (standard investigation contract)
- [M] Update connection pattern to use configurable directory path
- [M] Enhanced help text with working examples for case-based investigations
- [M] Update tests to verify directory flexibility and new defaults
- [S] Documentation updates in CLAUDE.md for new usage patterns
- [S] Example case directory structures in documentation
- [W] Complex directory auto-discovery or configuration files
- [W] Integration with other tools (will be separate issue)
- [W] GUI or interactive directory selection

## Acceptance Criteria

| # | Given | When | Then |
|---|-------|------|------|
| 1 | User in project root with existing whiskey_jack table | Runs `python export_for_neo4j.py` | Creates `./transcripts.json` with standard format |
| 2 | User with case data in `./data/case-alpha/` containing `evidence_calls.lance/` | Runs `python export_for_neo4j.py --data-dir ./data/case-alpha --table evidence_calls` | Creates `./transcripts.json` from case-alpha data |
| 3 | User with secure data in `/secure/investigations/operation-x/` | Runs `python export_for_neo4j.py --data-dir /secure/investigations/operation-x --table surveillance_data` | Accesses secure directory and creates `./transcripts.json` |
| 4 | User wants custom output location | Runs `python export_for_neo4j.py -o custom-output.json` | Creates `./custom-output.json` instead of default |
| 5 | User runs help command | Runs `python export_for_neo4j.py --help` | Shows working examples with whiskey_jack data, case directories, and transcripts.json output |
| 6 | Existing users with current workflows | Run any existing commands without modification | All scripts work exactly as before (backward compatibility) |
| 7 | All 4 scripts (export_for_neo4j.py, lancedb_data_dump.py, whiskey_jack_eda.py, analyze_data_model.py) | Support `--data-dir` argument | All accept directory path and connect to LanceDB tables in specified location |

## Technical Design

**Core Changes:**
1. **Add `--data-dir` argument** to ArgumentParser in all scripts:
   ```python
   parser.add_argument(
       "--data-dir", 
       default=".",
       help="Directory containing LanceDB tables (default: current directory)"
   )
   ```

2. **Update connection pattern**:
   ```python
   # Before: db = lancedb.connect(".")
   # After:  db = lancedb.connect(args.data_dir)
   ```

3. **Change default output** in export_for_neo4j.py:
   ```python
   # Before: default="-" (stdout)
   # After:  default="transcripts.json"
   ```

4. **Enhanced help examples**:
   ```
   Examples:
     %(prog)s                                    # Current dir → transcripts.json
     %(prog)s --data-dir ./data/case-alpha       # Case data → transcripts.json  
     %(prog)s --data-dir /secure/ops/case-beta --table phone_records
     %(prog)s -o custom-output.json              # Custom output filename
   ```

**Standard Usage Patterns for Investigators:**
- **Project Root**: `python export_for_neo4j.py` → `./transcripts.json`
- **Case Directory**: `python export_for_neo4j.py --data-dir ./data/case-alpha --table evidence_calls` → `./transcripts.json`
- **Secure Location**: `python export_for_neo4j.py --data-dir /secure/investigations/operation-x --table surveillance_data` → `./transcripts.json`

## Implementation Steps

1. **Update export_for_neo4j.py**:
   - Add `--data-dir` argument with "." default
   - Change `-o` default from "-" to "transcripts.json"
   - Update connection: `lancedb.connect(args.data_dir)`
   - Enhance help text with case-based examples

2. **Update lancedb_data_dump.py**:
   - Add `--data-dir` argument with "." default
   - Update connection: `lancedb.connect(args.data_dir)`
   - Add help examples

3. **Update whiskey_jack_eda.py**:
   - Add `--data-dir` argument with "." default  
   - Update connection: `lancedb.connect(args.data_dir)`
   - Add help examples

4. **Update analyze_data_model.py**:
   - Add `--data-dir` argument with "." default
   - Update connection: `lancedb.connect(args.data_dir)`
   - Add help examples

5. **Update test suites**:
   - Add tests for `--data-dir` argument presence and functionality
   - Verify new default output behavior
   - Test backward compatibility maintained
   - Add tests for case-based directory usage

6. **Update documentation**:
   - Add new usage patterns to CLAUDE.md
   - Document standard investigation workflows
   - Update requirements.txt if needed

## Testing Strategy

**Unit Tests:**
- Verify `--data-dir` argument parsing and defaults
- Test connection with different directory paths
- Verify new output defaults work correctly
- Ensure backward compatibility maintained

**Integration Tests:**
- Create test case directories with sample LanceDB tables
- Verify scripts work from project root and case directories
- Test with absolute and relative paths
- Validate output file creation in correct locations

**Manual Testing:**
- Test case-based investigation workflow end-to-end
- Verify help text shows clear working examples
- Test with sensitive data directories (permissions)

## Risks & Considerations

**Risks:**
- Directory path handling across different operating systems
- Permission issues with secure investigation directories
- Breaking changes if default output behavior changes unexpectedly

**Mitigations:**
- Use os.path operations for cross-platform compatibility
- Clear error messages for permission/access issues
- Comprehensive backward compatibility testing
- Gradual rollout with existing users

**Dependencies:**
- Existing LanceDB table structure must remain compatible
- File system permissions for investigation directories
- Integration patterns with future neo4j-for-surveillance-poc-3 consolidation

**Future Considerations:**
- Foundation for unified CLI patterns across investigation tools
- Potential integration with case management systems
- Advanced directory discovery for complex investigation structures

---
*(generated automatically – refine or replace before work starts)*