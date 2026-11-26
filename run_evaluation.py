"""
Test Runner and System Verification Script
===========================================
Executes all unit tests and verifies end-to-end functionality.
"""

import unittest
import sys
import os

# Add root directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def run_all_tests():
    print("=" * 70)
    print("  RUNNING MULTI-VITAL EARLY WARNING SYSTEM UNIT TESTS")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover(os.path.join(PROJECT_ROOT, "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 70)
    if result.wasSuccessful():
        print(">>> ALL TESTS PASSED SUCCESSFULLY! (100% VERIFIED) <<<")
    else:
        print(f">>> TEST FAILURES: {len(result.failures)} failures, {len(result.errors)} errors <<<")
    print("=" * 70)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
