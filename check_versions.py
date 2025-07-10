#!/usr/bin/env python3
"""
Check current package versions and compatibility
"""

import subprocess
import sys


def get_latest_versions():
    """Check latest available versions"""
    packages = ["lancedb", "pylance", "duckdb", "pandas", "pyarrow", "streamlit"]

    print("Current vs Latest Package Versions")
    print("=" * 60)

    for package in packages:
        try:
            # Get current version
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        current_version = line.split(":", 1)[1].strip()
                        break
                else:
                    current_version = "Not installed"
            else:
                current_version = "Not installed"

            # Get latest version
            result = subprocess.run(
                [sys.executable, "-m", "pip", "index", "versions", package],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "Available versions:" in line:
                        # Get the first version (latest)
                        versions_line = next(
                            (
                                l
                                for l in lines
                                if l.strip() and not l.startswith("Available")
                            ),
                            "",
                        )
                        if versions_line:
                            latest_version = versions_line.strip().split(",")[0].strip()
                        else:
                            latest_version = "Unknown"
                        break
                else:
                    latest_version = "Unknown"
            else:
                latest_version = "Unknown"

            print(
                f"{package:12} | Current: {current_version:12} | Latest: {latest_version}"
            )

        except Exception as e:
            print(f"{package:12} | Error checking versions: {e}")


def test_compatibility():
    """Test if our code works with current versions"""
    print("\n" + "=" * 60)
    print("Testing Compatibility with Current Versions")
    print("=" * 60)

    try:
        import lancedb

        print(f"✓ lancedb {lancedb.__version__} - OK")

        # Test connection
        db = lancedb.connect(".")
        tables = db.table_names()
        print(f"✓ LanceDB connection works - Found {len(tables)} tables")

    except Exception as e:
        print(f"✗ lancedb - ERROR: {e}")

    try:
        import duckdb

        print(f"✓ duckdb {duckdb.__version__} - OK")

        # Test basic query
        result = duckdb.query("SELECT 1 as test").to_df()
        print("✓ DuckDB queries work")

    except Exception as e:
        print(f"✗ duckdb - ERROR: {e}")

    try:
        import pandas as pd

        print(f"✓ pandas {pd.__version__} - OK")
    except Exception as e:
        print(f"✗ pandas - ERROR: {e}")

    try:
        import pyarrow as pa

        print(f"✓ pyarrow {pa.__version__} - OK")
    except Exception as e:
        print(f"✗ pyarrow - ERROR: {e}")

    try:
        import lance

        print("✓ pylance (lance) available - OK")

        # Test the critical .to_lance() method
        if "whiskey_jack" in tables:
            table = db.open_table("whiskey_jack")
            lance_data = table.to_lance()
            print("✓ .to_lance() method works - CRITICAL for SQL integration")

    except ImportError as e:
        print(f"✗ pylance - CRITICAL ERROR: {e}")
        print("  Install with: pip install pylance==0.26.1")
    except Exception as e:
        print(f"✗ pylance - ERROR: {e}")

    try:
        import streamlit as st

        print(f"✓ streamlit {st.__version__} - OK")
    except Exception as e:
        print(f"✗ streamlit - ERROR: {e}")


if __name__ == "__main__":
    get_latest_versions()
    test_compatibility()

    print("\n" + "=" * 60)
    print("Recommendations:")
    print("=" * 60)
    print("1. LanceDB: Stick to 0.22.x for stability (Connor's tested version)")
    print("2. PyLance: CRITICAL - Required for .to_lance() method (use 0.26.1)")
    print("3. DuckDB: Can upgrade to latest (actively maintained)")
    print("4. Pandas: Can upgrade to latest (stable API)")
    print("5. PyArrow: Upgrade carefully (LanceDB dependency)")
    print("6. Streamlit: Safe to upgrade to latest")
    print("")
    print("CRITICAL: Without pylance, SQL integration will fail with ImportError")
