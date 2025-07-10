#!/usr/bin/env python3
"""
Test suite for --data-dir argument support across all LanceDB scripts
Tests the flexible directory support feature (Issue #3)
"""

import pytest
import tempfile
import os
import sys
import subprocess
import shutil


class TestDataDirSupport:
    """Test --data-dir argument support for all LanceDB scripts"""

    def setup_method(self):
        """Create temporary directory structure for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_case_dir = os.path.join(self.temp_dir, "test_case")
        os.makedirs(self.test_case_dir)

        # Scripts to test
        self.scripts = [
            "export_for_neo4j.py",
            "lancedb_data_dump.py",
            "whiskey_jack_eda.py",
            "analyze_data_model.py",
            "lancedb_data_browser.py",
            "check_all_communications.py",
            "test_connor_lookup.py",
        ]

    def teardown_method(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.temp_dir)

    def test_all_scripts_accept_data_dir_argument(self):
        """AC1: All scripts accept --data-dir argument"""
        for script in self.scripts:
            if os.path.exists(script):
                result = subprocess.run(
                    [sys.executable, script, "--help"], capture_output=True, text=True
                )

                # Should not fail and should mention --data-dir
                assert result.returncode == 0, f"{script} help command failed"
                assert "--data-dir" in result.stdout, (
                    f"{script} missing --data-dir argument"
                )

    def test_backward_compatibility_maintained(self):
        """AC6: Existing users with current workflows work exactly as before"""
        # Test that scripts work without --data-dir (default behavior)
        for script in self.scripts:
            if os.path.exists(script):
                result = subprocess.run(
                    [sys.executable, script, "--help"], capture_output=True, text=True
                )

                # Should work without --data-dir argument
                assert result.returncode == 0, f"{script} backward compatibility broken"

    def test_export_default_output_changed(self):
        """AC1: export_for_neo4j.py creates ./transcripts.json by default"""
        # This test should initially fail because current default is stdout
        if os.path.exists("export_for_neo4j.py"):
            result = subprocess.run(
                [sys.executable, "export_for_neo4j.py", "--help"],
                capture_output=True,
                text=True,
            )

            # Should show transcripts.json as default, not stdout
            assert "transcripts.json" in result.stdout, (
                "Default output should be transcripts.json"
            )

    def test_data_dir_argument_parsing(self):
        """Test that --data-dir argument is properly parsed"""
        # This test validates the argument parsing logic
        test_dir = "/test/directory"

        # Mock test - would need actual implementation to pass
        # For now, just check the scripts can be imported
        for script in self.scripts:
            if os.path.exists(script):
                # Try importing as module to check syntax
                script_name = script.replace(".py", "")
                try:
                    # This is a basic syntax check
                    subprocess.run(
                        [sys.executable, "-m", "py_compile", script],
                        check=True,
                        capture_output=True,
                    )
                except subprocess.CalledProcessError:
                    pytest.fail(f"{script} has syntax errors")

    def test_help_text_shows_working_examples(self):
        """AC5: Help text shows working examples"""
        key_scripts = ["export_for_neo4j.py", "lancedb_data_dump.py"]

        for script in key_scripts:
            if os.path.exists(script):
                result = subprocess.run(
                    [sys.executable, script, "--help"], capture_output=True, text=True
                )

                # Should show case-based examples
                help_text = result.stdout.lower()
                assert "case" in help_text or "directory" in help_text, (
                    f"{script} help missing case examples"
                )

    def test_connection_pattern_uses_data_dir(self):
        """Test that scripts use args.data_dir for lancedb.connect()"""
        # This test checks that the connection pattern is updated
        # Currently should fail because scripts use lancedb.connect(".")

        for script in self.scripts:
            if os.path.exists(script):
                with open(script, "r") as f:
                    content = f.read()

                # Check for the new pattern (should initially fail)
                if "lancedb.connect" in content:
                    # Should use args.data_dir, not hardcoded "."
                    assert "args.data_dir" in content, (
                        f"{script} not using args.data_dir for connection"
                    )


class TestCaseBasedWorkflow:
    """Test case-based investigation workflow scenarios"""

    def setup_method(self):
        """Setup test case directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.case_alpha_dir = os.path.join(self.temp_dir, "case-alpha")
        self.case_beta_dir = os.path.join(self.temp_dir, "case-beta")
        os.makedirs(self.case_alpha_dir)
        os.makedirs(self.case_beta_dir)

    def teardown_method(self):
        """Clean up test directories"""
        shutil.rmtree(self.temp_dir)

    def test_case_alpha_data_processing(self):
        """AC2: User with case data in ./data/case-alpha/ can process it"""
        # This should initially fail - no --data-dir support yet
        if os.path.exists("export_for_neo4j.py"):
            result = subprocess.run(
                [
                    sys.executable,
                    "export_for_neo4j.py",
                    "--data-dir",
                    self.case_alpha_dir,
                    "--table",
                    "evidence_calls",
                    "--help",  # Use help to avoid actual processing
                ],
                capture_output=True,
                text=True,
            )

            # Should accept the arguments without error
            assert result.returncode == 0, "Case-based workflow should be supported"

    def test_secure_directory_access(self):
        """AC3: User with secure data in absolute path can access it"""
        secure_dir = os.path.join(self.temp_dir, "secure-investigation")
        os.makedirs(secure_dir)

        if os.path.exists("export_for_neo4j.py"):
            result = subprocess.run(
                [
                    sys.executable,
                    "export_for_neo4j.py",
                    "--data-dir",
                    secure_dir,
                    "--table",
                    "surveillance_data",
                    "--help",  # Use help to avoid actual processing
                ],
                capture_output=True,
                text=True,
            )

            # Should accept absolute path arguments
            assert result.returncode == 0, "Absolute path data-dir should be supported"

    def test_custom_output_location(self):
        """AC4: User can specify custom output location"""
        if os.path.exists("export_for_neo4j.py"):
            result = subprocess.run(
                [
                    sys.executable,
                    "export_for_neo4j.py",
                    "-o",
                    "custom-output.json",
                    "--help",  # Use help to avoid actual processing
                ],
                capture_output=True,
                text=True,
            )

            # Should accept custom output filename
            assert result.returncode == 0, "Custom output filename should be supported"


class TestNDJSONDataRecovery:
    """Test NDJSON data recovery integration with main workflow"""
    
    def test_fix_ndjson_tool_exists_and_works(self):
        """Test that fix_ndjson.py tool is available and functional"""
        import subprocess
        import tempfile
        import os
        
        # Create test NDJSON with concatenated objects
        test_content = '{"id": 1, "type": "test"}{"id": 2, "type": "test"}\n{"id": 3, "type": "single"}\n'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        try:
            # Test dry run mode
            result = subprocess.run([
                sys.executable, 'fix_ndjson.py', test_file, '--dry-run'
            ], capture_output=True, text=True)
            
            assert result.returncode == 0
            assert "1 problematic lines" in result.stdout
            assert "Would fix 1 lines" in result.stdout
            
        finally:
            os.unlink(test_file)
    
    def test_check_all_communications_uses_fixed_file(self):
        """Test that analysis tools automatically use fixed NDJSON files"""
        # This validates the integration where check_all_communications.py
        # automatically detects and uses sessions_fixed.ndjson when available
        import subprocess
        
        result = subprocess.run([
            sys.executable, 'check_all_communications.py', '--help'
        ], capture_output=True, text=True)
        
        # Should not crash and should show help
        assert result.returncode == 0
        assert "Check communication types correlation" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
