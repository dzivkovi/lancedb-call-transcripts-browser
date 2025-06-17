# LanceDB Quick Reference Cheatsheet

## The Big Discovery

**The `.lance` directory IS the table, not the database!**

- Connect to parent directory: `lancedb.connect(".")`
- Table name = directory name without `.lance`

## Correct Usage

```python
import lancedb
import duckdb

# 1. Connect to directory containing .lance folders
db = lancedb.connect(".")  # NOT "./whiskey_jack.lance"!

# 2. List tables (strips .lance extension)
tables = db.table_names()  # ['whiskey_jack']

# 3. Open table
table = db.open_table("whiskey_jack")

# 4. Read data
df = table.to_pandas()
count = table.count_rows()
schema = table.schema

# 5. SQL with DuckDB
data = table.to_lance()  # Critical step!
result = duckdb.query("SELECT * FROM data").to_df()
```

## Common Mistakes

```python
# WRONG - Connecting to .lance directory
db = lancedb.connect("./whiskey_jack.lance")  # No tables!

# WRONG - Using wrong package
import lance
dataset = lance.dataset()  # AttributeError

# WRONG - Forgetting .to_lance() for SQL
duckdb.query("SELECT * FROM table")  # Error
```

## Directory Structure

```
your_workspace/
├── whiskey_jack.lance/    # This is a TABLE
│   ├── data/*.lance       # Data fragments
│   ├── _transactions/     # Transaction logs
│   └── _versions/         # Version info
└── your_script.py         # Connect from here with "."
```

## Key Points

1. Use `lancedb` package, not `lance` or `pylance`
2. Connect to parent directory, not .lance folder
3. Use `.to_lance()` before SQL queries
4. Table name = folder name minus `.lance`

## Requirements

```txt
lancedb==0.22.0
duckdb==1.2.2
pandas==2.2.3
pyarrow==20.0.0
```

---
*Remember: When in doubt, connect to "." and list tables!*
