#!/usr/bin/env python3
"""
Evaluation-first tests for investigate_case.py - Ultra-Simple Investigation Dashboard
"""

import subprocess
import pytest
import os
import time


class TestInvestigateCase:
    """Test suite for investigate_case.py functionality"""

    def test_investigate_case_script_exists(self):
        """Test that investigate_case.py script exists"""
        assert os.path.exists("investigate_case.py"), (
            "investigate_case.py script must exist"
        )

    def test_investigate_case_help(self):
        """Test that investigate_case.py shows proper help"""
        result = subprocess.run(
            ["python", "investigate_case.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0, "Help command should succeed"
        assert "--case-dir" in result.stdout, "Should show --case-dir argument"
        assert "--summary" in result.stdout, "Should show --summary argument"
        assert "--compare" in result.stdout, "Should show --compare argument"

    def test_investigate_case_gantry_full_dashboard(self):
        """
        Acceptance Criteria #1: Given Gantry case directory with sessions.ndjson and LanceDB
        When runs `investigate_case.py --case-dir ./data/gantry`
        Then gets stunning HTML dashboard in <10 seconds
        """
        start_time = time.time()

        result = subprocess.run(
            ["python", "investigate_case.py", "--case-dir", "./data/gantry"],
            capture_output=True,
            text=True,
            timeout=15,  # Allow some buffer over 10 seconds
        )

        execution_time = time.time() - start_time

        # Performance requirement: <10 seconds
        assert execution_time < 10, (
            f"Dashboard generation took {execution_time:.2f}s, must be <10s"
        )

        # Command should succeed
        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Should generate HTML dashboard
        dashboard_path = "./data/gantry/investigation_dashboard.html"
        assert os.path.exists(dashboard_path), "HTML dashboard should be generated"

        # Check dashboard content
        with open(dashboard_path, "r") as f:
            dashboard_content = f.read()

        # Should contain investigation dashboard title
        assert "Investigation Dashboard" in dashboard_content, (
            "Dashboard should have proper title"
        )

        # Should contain required sections
        assert "data-quality" in dashboard_content, "Should have data quality section"
        assert "timeline" in dashboard_content, "Should have timeline section"
        assert "players" in dashboard_content, "Should have key players section"
        assert "patterns" in dashboard_content, "Should have patterns section"
        assert "content" in dashboard_content, (
            "Should have content intelligence section"
        )
        assert "recommendations" in dashboard_content, (
            "Should have recommendations section"
        )

        # Dashboard should be self-contained (embedded CSS)
        assert "<style>" in dashboard_content, "Should have embedded CSS"
        # JavaScript is optional for basic dashboard - not required for MVP

        # File size requirement: <5MB
        file_size = os.path.getsize(dashboard_path) / (1024 * 1024)  # Convert to MB
        assert file_size < 5, f"Dashboard file is {file_size:.2f}MB, must be <5MB"

    def test_investigate_case_data_quality_assessment(self):
        """
        Acceptance Criteria #3: Given case with data quality issues
        When runs investigation command
        Then dashboard clearly shows data gaps and reliability scores
        """
        result = subprocess.run(
            ["python", "investigate_case.py", "--case-dir", "./data/gantry"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Check that data quality metrics are in the output
        dashboard_path = "./data/gantry/investigation_dashboard.html"
        with open(dashboard_path, "r") as f:
            content = f.read()

        # Should show data quality score
        assert "data quality" in content.lower(), "Should show data quality assessment"
        assert "%" in content, "Should show percentage-based quality metrics"

        # Should show correlation rates
        assert "correlation" in content.lower(), "Should show correlation analysis"

        # Should show data gaps or missing data info
        assert any(
            term in content.lower() for term in ["missing", "gaps", "integrity"]
        ), "Should show data quality issues"

    def test_investigate_case_large_dataset_performance(self):
        """
        Acceptance Criteria #4: Given case with 67K+ sessions
        When runs investigation command
        Then dashboard loads quickly with key insights highlighted
        """
        # Test with gantry case (67K+ sessions)
        start_time = time.time()

        result = subprocess.run(
            ["python", "investigate_case.py", "--case-dir", "./data/gantry"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        execution_time = time.time() - start_time

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert execution_time < 10, (
            f"Large dataset processing took {execution_time:.2f}s, must be <10s"
        )

        # Should contain insights about the large dataset
        dashboard_path = "./data/gantry/investigation_dashboard.html"
        with open(dashboard_path, "r") as f:
            content = f.read()

        # Should show session count
        assert "67" in content or "67,783" in content, "Should show large session count"

        # Should highlight key insights
        assert "key" in content.lower() or "insights" in content.lower(), (
            "Should highlight key insights"
        )

    def test_investigate_case_summary_flag(self):
        """
        Acceptance Criteria #5: Given investigator needs case summary
        When runs with `--summary` flag
        Then gets 10-line terminal summary of key findings
        """
        result = subprocess.run(
            [
                "python",
                "investigate_case.py",
                "--case-dir",
                "./data/gantry",
                "--summary",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Should output to terminal (stdout)
        summary_lines = result.stdout.strip().split("\n")

        # Should be approximately 10 lines (allowing some flexibility)
        assert 8 <= len(summary_lines) <= 12, (
            f"Summary should be ~10 lines, got {len(summary_lines)}"
        )

        # Should contain key findings
        summary_text = result.stdout.lower()
        assert "sessions" in summary_text, "Summary should mention sessions"
        assert "data quality" in summary_text, "Summary should mention data quality"
        assert any(term in summary_text for term in ["key", "findings", "insights"]), (
            "Summary should contain key findings"
        )

    def test_investigate_case_comparison_mode(self):
        """
        Acceptance Criteria #6: Given multiple cases to compare
        When runs `--compare case1 case2`
        Then gets side-by-side comparison dashboard
        """
        # Skip if second case doesn't exist
        if not os.path.exists("./data/whiskey-jack"):
            pytest.skip("Second case directory not available for comparison test")

        result = subprocess.run(
            [
                "python",
                "investigate_case.py",
                "--compare",
                "./data/gantry",
                "./data/whiskey-jack",
            ],
            capture_output=True,
            text=True,
            timeout=20,  # Comparison might take longer
        )

        assert result.returncode == 0, f"Comparison command failed: {result.stderr}"

        # Should generate comparison dashboard
        comparison_path = "./comparison_dashboard.html"
        assert os.path.exists(comparison_path), (
            "Comparison dashboard should be generated"
        )

        # Check comparison content
        with open(comparison_path, "r") as f:
            content = f.read()

        # Should contain both case names
        assert "gantry" in content.lower(), "Should contain first case name"
        assert "whiskey" in content.lower(), "Should contain second case name"

        # Should show side-by-side comparison
        assert "comparison" in content.lower(), "Should indicate comparison mode"

    def test_investigate_case_wow_factor_requirements(self):
        """
        Test WOW factor requirements from success metrics:
        - Non-technical investigators understand case in <60 seconds
        - 5+ actionable insights generated automatically
        """
        result = subprocess.run(
            ["python", "investigate_case.py", "--case-dir", "./data/gantry"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        dashboard_path = "./data/gantry/investigation_dashboard.html"
        with open(dashboard_path, "r") as f:
            content = f.read()

        # Should be visually appealing (emojis, clear sections)
        assert "🔍" in content or "📊" in content, "Should use visual elements (emojis)"

        # Should have clear, non-technical language
        assert "investigation" in content.lower(), (
            "Should use investigative terminology"
        )
        assert "analysis" in content.lower(), "Should mention analysis"

        # Should provide actionable insights (recommendations section)
        assert "recommend" in content.lower() or "action" in content.lower(), (
            "Should provide actionable recommendations"
        )

    def test_investigate_case_zero_dependencies(self):
        """
        Test that investigate_case.py uses only built-in Python libraries
        and existing project dependencies (zero external dependencies)
        """
        # Read the investigate_case.py file when it exists
        if os.path.exists("investigate_case.py"):
            with open("investigate_case.py", "r") as f:
                code = f.read()

            # Should not import external visualization libraries
            forbidden_imports = ["matplotlib", "plotly", "seaborn", "bokeh", "altair"]
            for lib in forbidden_imports:
                assert f"import {lib}" not in code, (
                    f"Should not import {lib} (external dependency)"
                )

            # Should use only built-ins and existing project deps
            allowed_imports = [
                "html",
                "json",
                "datetime",
                "collections",
                "argparse",
                "lancedb",
                "duckdb",
                "os",
                "sys",
                "pathlib",
            ]

            # Extract import statements (basic check)
            import_lines = [
                line for line in code.split("\n") if line.strip().startswith("import ")
            ]
            for line in import_lines:
                # This is a basic check - real implementation would be more sophisticated
                assert any(allowed in line for allowed in allowed_imports), (
                    f"Import line may use unauthorized dependency: {line}"
                )

    def test_investigate_case_error_handling(self):
        """Test error handling for various edge cases"""

        # Test with non-existent directory
        result = subprocess.run(
            ["python", "investigate_case.py", "--case-dir", "./nonexistent"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode != 0, "Should fail with non-existent directory"
        error_output = (result.stderr + result.stdout).lower()
        assert "not found" in error_output or "does not exist" in error_output, (
            "Should show helpful error message"
        )

        # Test with invalid arguments
        result = subprocess.run(
            ["python", "investigate_case.py", "--invalid-arg"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode != 0, "Should fail with invalid arguments"

    def test_investigate_case_backward_compatibility(self):
        """Test that investigate_case.py doesn't break existing workflow"""
        # Should work with current data structure
        result = subprocess.run(
            ["python", "investigate_case.py", "--case-dir", "."],
            capture_output=True,
            text=True,
            timeout=15,
        )

        # Should either succeed or fail gracefully with helpful message
        if result.returncode != 0:
            # If it fails, should have helpful error message
            assert result.stderr.strip(), (
                "Should provide error message if command fails"
            )
        else:
            # If it succeeds, should generate output
            assert result.stdout.strip() or os.path.exists(
                "investigation_dashboard.html"
            ), "Should generate output if command succeeds"


class TestInvestigateTimeline:
    """Test timeline analysis functionality"""

    def test_timeline_analysis_exists(self):
        """Test that timeline analysis is implemented"""
        # This will be implemented as part of the solution
        pass

    def test_behavioral_insights_detection(self):
        """Test behavioral pattern detection"""
        # This will be implemented as part of the solution
        pass


class TestInvestigateNetworkAnalysis:
    """Test network analysis functionality"""

    def test_key_players_identification(self):
        """Test key players identification"""
        # This will be implemented as part of the solution
        pass

    def test_communication_patterns(self):
        """Test communication pattern analysis"""
        # This will be implemented as part of the solution
        pass


class TestInvestigateContentIntelligence:
    """Test content intelligence functionality"""

    def test_keyword_extraction(self):
        """Test keyword extraction"""
        # This will be implemented as part of the solution
        pass

    def test_suspicious_pattern_detection(self):
        """Test suspicious pattern detection"""
        # This will be implemented as part of the solution
        pass


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
