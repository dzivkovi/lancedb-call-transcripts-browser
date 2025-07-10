# Configurable LanceDB Table Names

## Problem / Metric
All LanceDB scripts hardcode `"whiskey_jack"` as the table name, preventing reuse with other datasets. This affects 9 scripts that all use identical connection patterns.

## Goal
Enable scripts to work with any LanceDB table while maintaining backward compatibility and keeping the solution ultra-simple.

## Scope (M/S/W)
- [M] Add `--table` argument to all scripts with `whiskey_jack` default
- [M] Update export_for_neo4j.py (already has argparse)
- [M] Update 7 simple utility scripts (single hardcoded reference each)
- [S] Update lancedb_data_browser.py (requires refactoring cached functions)
- [W] Environment variables, config files, or auto-detection (over-engineering)

## Acceptance Criteria
| # | Given | When | Then |
|---|-------|------|------|
| 1 | Any script | Run without --table argument | Uses whiskey_jack (backward compatible) |
| 2 | Any script | Run with --table other_dataset | Connects to other_dataset.lance table |
| 3 | export_for_neo4j.py | Run with --table gantry | Exports gantry session data |
| 4 | All scripts | --help flag | Shows table argument documentation |

## Technical Design

**Ultra-simple pattern for all scripts:**
```python
# Before (hardcoded)
table = db.open_table("whiskey_jack")

# After (configurable)
table = db.open_table(args.table)
```

**Argument parsing addition:**
```python
parser.add_argument('--table', default='whiskey_jack', 
                   help='LanceDB table name (default: whiskey_jack)')
```

## Implementation Steps
1. Start with `export_for_neo4j.py` (easiest - already has argparse)
2. Add `--table` argument with default value
3. Replace hardcoded `"whiskey_jack"` with `args.table`
4. Test with existing and new datasets
5. Apply same pattern to 7 simple utility scripts
6. Refactor `lancedb_data_browser.py` (pass table name to cached functions)

## Testing Strategy
- Verify backward compatibility: all scripts work without arguments
- Test with new table: `python export_for_neo4j.py --table gantry`
- Ensure help text displays correctly

## Risks & Considerations
- **Ultra-low risk**: Single-line changes for most scripts
- **Backward compatible**: Default value maintains current behavior
- **Consistent pattern**: Same approach across all scripts