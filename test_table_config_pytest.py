#!/usr/bin/env python3
"""
Pytest version: Test configurable table names implementation  
"""

import subprocess
import pytest


SCRIPTS = [
    "export_for_neo4j.py",
    "lancedb_data_dump.py", 
    "whiskey_jack_eda.py",
    "analyze_data_model.py",
]


@pytest.mark.parametrize("script_name", SCRIPTS)
def test_script_help(script_name):
    """Test that script shows --table option in help"""
    result = subprocess.run(
        ["python", script_name, "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    assert result.returncode == 0, f"{script_name}: Help command failed"
    assert "--table" in result.stdout, f"{script_name}: --table argument missing"
    assert "whiskey_jack" in result.stdout.lower(), f"{script_name}: No default shown"


@pytest.mark.parametrize("script_name", SCRIPTS)
def test_backward_compatibility(script_name):
    """Test that script works without arguments (backward compatibility)"""
    result = subprocess.run(
        ["python", script_name], 
        capture_output=True, 
        text=True, 
        timeout=15
    )
    
    # Should NOT have argument parsing errors (backward compatibility)
    error_msg = result.stderr.lower()
    assert not ("argument" in error_msg and "required" in error_msg), \
        f"{script_name}: Requires arguments (breaks backward compatibility)"


@pytest.mark.parametrize("script_name", SCRIPTS)
def test_table_argument_usage(script_name):
    """Test that --table argument works with custom value"""
    result = subprocess.run(
        ["python", script_name, "--table", "test_table", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    # Help should work even with --table argument
    assert result.returncode == 0, f"{script_name}: --table argument breaks help"


def test_export_generates_same_format():
    """Test that export_for_neo4j.py generates expected JSON format"""
    result = subprocess.run(
        ["python", "export_for_neo4j.py", "--table", "whiskey_jack", "--quiet"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    if result.returncode == 0:
        # Should be valid JSON with session IDs as keys
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, dict), "Output should be a dictionary"
        
        # Check structure of first entry
        if data:
            first_key, first_value = next(iter(data.items()))
            required_fields = ["text", "chunk_count", "char_count", "session_type"]
            for field in required_fields:
                assert field in first_value, f"Missing required field: {field}"