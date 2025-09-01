#!/usr/bin/env python3
"""
Test runner script for DraftIQ.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all tests with coverage reporting."""
    print("🧪 Running DraftIQ Test Suite...")
    print("=" * 50)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Test command with coverage
    test_cmd = [
        "python", "-m", "pytest",
        "app/tests/",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--asyncio-mode=auto",  # Auto async mode
        "--cov=app",  # Coverage for app module
        "--cov-report=term-missing",  # Show missing lines
        "--cov-report=html:htmlcov",  # HTML coverage report
        "--cov-fail-under=60",  # Fail if coverage < 60%
    ]
    
    try:
        print("Running tests with coverage...")
        result = subprocess.run(test_cmd, check=True)
        
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/")
        print("🎯 Coverage target: 60%")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("   pip install pytest pytest-asyncio httpx")
        return 1


def run_specific_test(test_file: str):
    """Run a specific test file."""
    print(f"🧪 Running {test_file}...")
    print("=" * 50)
    
    test_cmd = [
        "python", "-m", "pytest",
        f"app/tests/{test_file}",
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    try:
        result = subprocess.run(test_cmd, check=True)
        print(f"\n✅ {test_file} passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_file} failed with exit code {e.returncode}")
        return e.returncode


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if test_file.endswith(".py"):
            return run_specific_test(test_file)
        else:
            print(f"❌ Invalid test file: {test_file}")
            print("Usage: python run_tests.py [test_file.py]")
            return 1
    else:
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())
