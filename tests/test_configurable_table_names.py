#!/usr/bin/env python3
"""
Test suite for configurable LanceDB table names.
Tests that scripts accept --table argument and maintain backward compatibility.
"""

import subprocess
import os


class TestConfigurableTableNames:
    """Test that LanceDB scripts accept configurable table names."""

    def test_export_for_neo4j_default_table(self):
        """Test export_for_neo4j.py uses whiskey_jack by default (backward compatibility)."""
        # This test expects the script to fail gracefully if whiskey_jack table doesn't exist
        # but should show the --table option in help
        result = subprocess.run(
            ["python", "export_for_neo4j.py", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        assert result.returncode == 0
        assert "--table" in result.stdout
        assert "whiskey_jack" in result.stdout.lower()

    def test_export_for_neo4j_custom_table_argument(self):
        """Test export_for_neo4j.py accepts --table argument."""
        result = subprocess.run(
            ["python", "export_for_neo4j.py", "--table", "test_table", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        assert result.returncode == 0
        assert "--table" in result.stdout

    def test_lancedb_data_dump_default_table(self):
        """Test lancedb_data_dump.py uses whiskey_jack by default."""
        result = subprocess.run(
            ["python", "lancedb_data_dump.py", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        assert result.returncode == 0
        assert "--table" in result.stdout
        assert "whiskey_jack" in result.stdout.lower()

    def test_lancedb_data_dump_custom_table_argument(self):
        """Test lancedb_data_dump.py accepts --table argument."""
        result = subprocess.run(
            ["python", "lancedb_data_dump.py", "--table", "test_table", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        assert result.returncode == 0
        assert "--table" in result.stdout

    def test_whiskey_jack_eda_default_table(self):
        """Test whiskey_jack_eda.py uses whiskey_jack by default."""
        result = subprocess.run(
            ["python", "whiskey_jack_eda.py", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        assert result.returncode == 0
        assert "--table" in result.stdout
        assert "whiskey_jack" in result.stdout.lower()

    def test_whiskey_jack_eda_custom_table_argument(self):
        """Test whiskey_jack_eda.py accepts --table argument."""
        result = subprocess.run(
            ["python", "whiskey_jack_eda.py", "--table", "test_table", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        assert result.returncode == 0
        assert "--table" in result.stdout

    def test_all_scripts_have_table_argument(self):
        """Test that all major LanceDB scripts support --table argument."""
        scripts = [
            "export_for_neo4j.py",
            "lancedb_data_dump.py",
            "whiskey_jack_eda.py",
            "check_all_communications.py",
            "check_session_ids.py",
            "analyze_data_model.py",
            "test_connor_lookup.py",
        ]

        for script in scripts:
            if os.path.exists(script):
                result = subprocess.run(
                    ["python", script, "--help"],
                    capture_output=True,
                    text=True,
                    cwd=".",
                )
                assert result.returncode == 0, f"{script} should show help"
                assert "--table" in result.stdout, (
                    f"{script} should have --table argument"
                )

    def test_backward_compatibility_no_arguments(self):
        """Test scripts work without any arguments (backward compatibility)."""
        # These tests expect graceful failure if whiskey_jack doesn't exist
        # but should not crash due to missing --table argument
        scripts = ["export_for_neo4j.py", "lancedb_data_dump.py", "whiskey_jack_eda.py"]

        for script in scripts:
            if os.path.exists(script):
                result = subprocess.run(
                    ["python", script],
                    capture_output=True,
                    text=True,
                    cwd=".",
                    timeout=10,  # Prevent hanging
                )
                # Should either succeed or fail gracefully, not crash with argument errors
                # Error codes for missing database are OK, but not for missing arguments
                if result.returncode != 0:
                    assert (
                        "argument" not in result.stderr.lower()
                        or "required" not in result.stderr.lower()
                    )
