# Version Compatibility Guide

## Current Requirements (Tested & Working)

These are the exact versions from Connor's working environment:

```txt
lancedb==0.22.0
pylance==0.26.1  # CRITICAL: Required for .to_lance() method
duckdb==1.2.2  
pandas==2.2.3
pyarrow==20.0.0
streamlit (latest)
```

## ⚠️ CRITICAL DISCOVERY: PyLance Dependency

**The Missing Link**: LanceDB's `.to_lance()` method requires the `pylance` package!

```python
# This fails without pylance:
table.to_lance()  # ImportError: The lance library is required

# Error message says: "Please install with `pip install pylance`"
```

### Package Relationship:
- `lancedb` = Database wrapper/client
- `pylance` = Core Lance format reader/writer  
- `lancedb.table.to_lance()` requires `pylance` internally
- **Both are required** for our DuckDB SQL integration

## Upgrade Safety Analysis

### ✅ SAFE TO UPGRADE

**DuckDB** (`1.2.2` → latest)
- Very stable SQL API
- Our usage is basic: `STRING_AGG`, `FIRST`, `ORDER BY`
- Actively maintained with good backward compatibility
- **Recommendation**: Upgrade to latest

**Pandas** (`2.2.3` → latest) 
- We use basic operations: `.to_pandas()`, `.iloc[]`, `.str.len()`
- Pandas has stable API since 2.x
- **Recommendation**: Upgrade to latest

**Streamlit** (any → latest)
- We use standard components: `st.dataframe`, `st.selectbox`, etc.
- Streamlit maintains good backward compatibility
- **Recommendation**: Always use latest

### ⚠️ UPGRADE WITH CAUTION

**PyLance** (`0.26.1` → latest)
- **CRITICAL DEPENDENCY** for `.to_lance()` method
- Must be compatible with LanceDB version
- Version 0.26.1 is proven to work with LanceDB 0.22.0
- **Recommendation**: Keep at 0.26.1 unless testing thoroughly

**PyArrow** (`20.0.0` → latest)
- LanceDB depends on PyArrow internally
- PyLance also depends on PyArrow
- Version mismatches can cause serialization issues
- **Recommendation**: Upgrade gradually, test thoroughly

**LanceDB** (`0.22.0` → latest)
- API can change between versions
- Must be compatible with PyLance version
- Version 0.22.0 is proven to work with our data format
- **Recommendation**: Stay on 0.22.x unless specific need to upgrade

## Compatibility Matrix

| Package | Connor's Version | Latest (June 2025) | Upgrade Risk | Notes |
|---------|------------------|---------------------|--------------|-------|
| lancedb | 0.22.0 | 0.24+ | HIGH | Core API + PyLance dependency |
| pylance | 0.26.1 | 0.28+ | HIGH | **Required for .to_lance()** |
| pyarrow | 20.0.0 | 25+ | MEDIUM | Shared dependency |
| duckdb | 1.2.2 | 1.3+ | LOW | Stable SQL interface |
| pandas | 2.2.3 | 2.3+ | LOW | Stable DataFrame API |
| streamlit | Any | Latest | LOW | Good backward compatibility |

## Installation Strategies

### Strategy 1: Conservative (Recommended for Production)
```bash
pip install -r requirements.txt  # Use Connor's exact versions
```

**Complete requirements.txt:**
```txt
lancedb==0.22.0
pylance==0.26.1
duckdb==1.2.2
pandas==2.2.3
pyarrow==20.0.0
streamlit
```

### Strategy 2: Selective Upgrade
```bash
# Keep critical Lance ecosystem together
pip install lancedb==0.22.0 pylance==0.26.1 pyarrow==20.0.0

# Upgrade safe packages
pip install duckdb pandas streamlit --upgrade
```

### Strategy 3: Latest Everything (Development Only)
```bash
pip install -r requirements_latest.txt  # Use version ranges
```

**requirements_latest.txt:**
```txt
lancedb>=0.22.0,<0.25.0
pylance>=0.26.1,<0.30.0
duckdb>=1.2.2
pandas>=2.2.3
pyarrow>=20.0.0
streamlit>=1.28.0
```

## Clean Virtual Environment Setup

### Step-by-Step Installation
```bash
# 1. Create clean environment
python -m venv lancedb_env

# 2. Activate environment
# Windows:
lancedb_env\Scripts\activate
# Linux/Mac:
source lancedb_env/bin/activate

# 3. Install exact working versions
pip install lancedb==0.22.0
pip install pylance==0.26.1    # CRITICAL!
pip install duckdb==1.2.2
pip install pandas==2.2.3
pip install pyarrow==20.0.0
pip install streamlit

# OR install from requirements
pip install -r requirements.txt
```

## Testing Your Setup

Run this to verify compatibility:
```bash
python check_versions.py
python analyze_data_model.py         # Should complete without ImportError
python lancedb_data_dump.py     # Should work without errors
streamlit run lancedb_data_browser.py  # Should launch successfully
```

## Common Issues & Solutions

### Missing PyLance Error
```
ImportError: The lance library is required to use this function. 
Please install with `pip install pylance`.
```
**Solution:**
```bash
pip install pylance==0.26.1
```

### LanceDB Connection Errors
- **Cause**: Version mismatch between LanceDB, PyLance, and PyArrow
- **Solution**: Reinstall the Lance ecosystem together
```bash
pip uninstall lancedb pylance pyarrow
pip install lancedb==0.22.0 pylance==0.26.1 pyarrow==20.0.0
```

### DuckDB SQL Errors  
- **Cause**: Syntax changes in newer DuckDB versions
- **Solution**: Usually minor, check DuckDB changelog
- **Fallback**: Downgrade to 1.2.2

### Streamlit Caching Issues
- **Cause**: Cache serialization changes
- **Solution**: Clear cache and restart
```bash
streamlit cache clear
```

## Dependency Chain Analysis

```
Your Code
    ↓
lancedb.connect()     → Works with any version
    ↓
table.to_pandas()     → Works with any version  
    ↓
table.to_lance()      → REQUIRES pylance package!
    ↓
duckdb.query()        → Works with any version
```

**The Critical Path:**
- Connor's SQL aggregation uses `table.to_lance()`
- This method requires `pylance` package
- Without `pylance`, you get ImportError on line 59 of analyze_data_model.py

## Global Package Conflicts

### Identify Conflicts
```bash
pip list | grep -E "(lance|duck|pandas|arrow|streamlit)"
pip check  # Shows dependency conflicts
```

### Clean Slate Approach (Recommended)
```bash
# Create isolated environment
python -m venv lancedb_env
# Activate (see commands above)
# Install only what we need
pip install -r requirements.txt
```

## Recommendations

1. **For this project**: Use Connor's exact versions - they're a proven working set
2. **Critical insight**: `pylance` is NOT optional - it's required for SQL functionality
3. **For new projects**: Test the Lance ecosystem (lancedb + pylance + pyarrow) together
4. **For production**: Pin ALL Lance-related versions together
5. **Always test**: Run `analyze_data_model.py` after any Lance-related upgrades

## Package Summary

**The Lance Ecosystem (keep together):**
- lancedb==0.22.0
- pylance==0.26.1  
- pyarrow==20.0.0

**Independent packages (safe to upgrade):**
- duckdb>=1.2.2
- pandas>=2.2.3
- streamlit (latest)

The key insight: **PyLance is the missing piece** that enables LanceDB's `.to_lance()` method, which is essential for our DuckDB SQL integration. This is why your scripts failed in the clean environment - not because of version conflicts, but because of a missing required dependency that wasn't obvious from the LanceDB documentation alone.