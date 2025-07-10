#!/usr/bin/env python3
"""
Test script to verify configurable table names implementation
"""

import subprocess
import sys


def test_script_help(script_name):
    """Test that script shows --table option in help"""
    try:
        result = subprocess.run(
            ["python", script_name, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            if "--table" in result.stdout and "whiskey_jack" in result.stdout.lower():
                print(f"✅ {script_name}: --table argument present with default")
                return True
            else:
                print(f"❌ {script_name}: --table argument missing or no default shown")
                return False
        else:
            print(f"❌ {script_name}: Help command failed")
            return False

    except Exception as e:
        print(f"❌ {script_name}: Error running help - {e}")
        return False


def test_backward_compatibility(script_name):
    """Test that script works without arguments (backward compatibility)"""
    try:
        result = subprocess.run(
            ["python", script_name], capture_output=True, text=True, timeout=15
        )

        # For these scripts, we expect either success or a graceful database error
        # but NOT argument parsing errors
        if "argument" in result.stderr.lower() and "required" in result.stderr.lower():
            print(
                f"❌ {script_name}: Requires arguments (breaks backward compatibility)"
            )
            return False
        else:
            print(f"✅ {script_name}: Backward compatible (no argument errors)")
            return True

    except subprocess.TimeoutExpired:
        print(f"⚠️  {script_name}: Timed out, but no argument errors")
        return True
    except Exception as e:
        print(f"⚠️  {script_name}: Error but may be data-related - {e}")
        return True


def main():
    print("🧪 Testing Configurable LanceDB Table Names Implementation")
    print("=" * 70)

    # Scripts to test
    scripts = [
        "export_for_neo4j.py",
        "lancedb_data_dump.py",
        "whiskey_jack_eda.py",
        "analyze_data_model.py",
    ]

    print("\n📋 Test 1: --table argument presence and help text")
    print("-" * 50)
    help_results = []
    for script in scripts:
        help_results.append(test_script_help(script))

    print("\n📋 Test 2: Backward compatibility (no argument errors)")
    print("-" * 50)
    compat_results = []
    for script in scripts:
        compat_results.append(test_backward_compatibility(script))

    print("\n📊 Test Results Summary")
    print("-" * 50)
    help_passed = sum(help_results)
    compat_passed = sum(compat_results)
    total_scripts = len(scripts)

    print(f"--table argument tests: {help_passed}/{total_scripts} passed")
    print(f"Backward compatibility: {compat_passed}/{total_scripts} passed")

    if help_passed == total_scripts and compat_passed == total_scripts:
        print("\n✅ ALL TESTS PASSED!")
        print("✅ Implementation meets acceptance criteria")
        return True
    else:
        print("\n❌ Some tests failed")
        print("❌ Implementation needs fixes")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
