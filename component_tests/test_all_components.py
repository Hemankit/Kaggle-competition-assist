#!/usr/bin/env python3
"""
Master test script that runs all component tests
"""

import sys
import os
import subprocess
import time

def run_test(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run {test_file}: {e}")
        return False

def main():
    """Run all component tests"""
    print("🚀 Starting Comprehensive Component Testing")
    print("=" * 60)
    
    # List of all test files
    test_files = [
        "test_kaggle_fetcher.py",
        "test_scrapers.py", 
        "test_hybrid_scraping_routing.py",
        "test_query_processing.py",
        "test_rag_pipeline.py",
        "test_orchestrators.py"
    ]
    
    results = {}
    start_time = time.time()
    
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            success = run_test(test_path)
            results[test_file] = success
            time.sleep(1)  # Brief pause between tests
        else:
            print(f"❌ Test file not found: {test_file}")
            results[test_file] = False
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_file:<35} {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall Results: {passed}/{total} test suites passed")
    print(f"⏱️  Total time: {duration:.2f} seconds")
    
    if passed == total:
        print("\n🎉 ALL COMPONENTS ARE WORKING! Ready for integration testing.")
    else:
        print(f"\n⚠️  {total - passed} components need attention before integration testing.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
