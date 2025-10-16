"""
Final Pre-Launch Test Suite
Tests all major query types to ensure intelligent responses (no generic templates)
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BACKEND_URL = "http://18.219.148.57:5000"

# Test queries covering all major response types
TEST_QUERIES = [
    {
        "name": "Evaluation Metric",
        "query": "What is the evaluation metric for this competition?",
        "expected_keywords": ["accuracy", "metric", "score", "evaluation"],
        "avoid_keywords": ["Based on the competition name", "generic", "placeholder"]
    },
    {
        "name": "Data Files",
        "query": "What data files are available?",
        "expected_keywords": ["train.csv", "test.csv", "KB", "MB", "file"],
        "avoid_keywords": ["No data files found", "0.0 MB", "0 files"]
    },
    {
        "name": "Submission Format",
        "query": "What format should my submission file be in?",
        "expected_keywords": ["PassengerId", "Survived", "CSV", "submission", "format"],
        "avoid_keywords": ["generic", "Based on the competition"]
    },
    {
        "name": "Overview/Explanation",
        "query": "Tell me about this competition",
        "expected_keywords": ["Titanic", "predict", "survival", "passengers"],
        "avoid_keywords": ["This is a Kaggle competition focused on data science", "generic", "placeholder"]
    },
    {
        "name": "Strategy",
        "query": "What approaches work best for this competition?",
        "expected_keywords": ["feature engineering", "model", "approach", "strategy"],
        "avoid_keywords": ["Start with comprehensive EDA", "Begin with baseline models", "Data Exploration Phase"]
    },
    {
        "name": "Getting Started",
        "query": "How should I get started?",
        "expected_keywords": ["notebook", "data", "explore", "baseline"],
        "avoid_keywords": ["Familiarize yourself with the competition structure", "Set up your development environment"]
    },
    {
        "name": "Notebooks",
        "query": "Show me the top notebooks for this competition",
        "expected_keywords": ["notebook", "approach", "technique", "score"],
        "avoid_keywords": ["No notebooks found", "generic"]
    },
    {
        "name": "Code Review",
        "query": """Review my code:
```python
import pandas as pd
df = pd.read_csv('train.csv')
for i in range(len(df)):
    print(df.iloc[i]['Name'])
```""",
        "expected_keywords": ["loop", "iloc", "efficient", "direct column access"],
        "avoid_keywords": ["generic", "placeholder"]
    }
]

def test_query(query_info, session_id):
    """Test a single query and validate response"""
    print(f"\n{'='*80}")
    print(f"TEST: {query_info['name']}")
    print(f"{'='*80}")
    print(f"Query: {query_info['query'][:100]}...")
    
    # Prepare request
    payload = {
        "query": query_info["query"],
        "session_id": session_id,
        "context": {
            "competition_slug": "titanic",
            "competition_name": "Titanic - Machine Learning from Disaster",
            "kaggle_username": "test_user"
        }
    }
    
    try:
        # Send request
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sending request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json=payload,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Response received in {elapsed:.2f}s")
        
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
        
        data = response.json()
        # Backend returns 'final_response' not 'response'
        response_text = data.get("final_response", data.get("response", ""))
        
        # Print response preview (remove emojis for Windows console)
        print(f"\nResponse Preview:")
        print("-" * 80)
        preview = response_text[:300] + "..." if len(response_text) > 300 else response_text
        # Encode-safe print for Windows
        print(preview.encode('ascii', 'ignore').decode('ascii'))
        print("-" * 80)
        
        # Validate response
        print(f"\nValidation:")
        
        # Check for expected keywords
        found_expected = []
        for keyword in query_info["expected_keywords"]:
            if keyword.lower() in response_text.lower():
                found_expected.append(keyword)
        
        # Check for avoided keywords (generic templates)
        found_avoided = []
        for keyword in query_info["avoid_keywords"]:
            if keyword.lower() in response_text.lower():
                found_avoided.append(keyword)
        
        # Results
        print(f"  [OK] Expected keywords found: {len(found_expected)}/{len(query_info['expected_keywords'])}")
        if found_expected:
            print(f"       Found: {', '.join(found_expected)}")
        
        if found_avoided:
            print(f"  [WARN] Generic/Template keywords found: {found_avoided}")
        else:
            print(f"  [OK] No generic template keywords found")
        
        # Check response length (too short = likely template)
        if len(response_text) < 100:
            print(f"  [WARN] Response seems short ({len(response_text)} chars)")
        else:
            print(f"  [OK] Response length: {len(response_text)} chars")
        
        # Overall verdict
        is_intelligent = (
            len(found_expected) >= 2 and  # At least 2 expected keywords
            len(found_avoided) == 0 and    # No generic keywords
            len(response_text) >= 100       # Reasonable length
        )
        
        if is_intelligent:
            print(f"\n[PASS] Intelligent, context-aware response")
            return True
        else:
            print(f"\n[FAIL] Response appears generic or incomplete")
            return False
            
    except requests.Timeout:
        print(f"[ERROR] FAILED: Request timeout (>120s)")
        return False
    except Exception as e:
        print(f"[ERROR] FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*80)
    print("FINAL PRE-LAUNCH TEST SUITE")
    print("="*80)
    print(f"Backend: {BACKEND_URL}")
    print(f"Competition: titanic")
    print(f"Total Tests: {len(TEST_QUERIES)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    session_id = f"final_test_{int(time.time())}"
    
    results = {}
    
    for i, query_info in enumerate(TEST_QUERIES, 1):
        print(f"\n\n[TEST {i}/{len(TEST_QUERIES)}]")
        
        success = test_query(query_info, session_id)
        results[query_info["name"]] = success
        
        # Brief pause between tests
        if i < len(TEST_QUERIES):
            print("\nWaiting 3 seconds before next test...")
            time.sleep(3)
    
    # Final summary
    print("\n\n")
    print("="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("="*80)
    
    if passed == total:
        print("\n*** ALL TESTS PASSED! READY FOR LAUNCH! ***")
        print("\nNo generic template responses detected.")
        print("All responses are intelligent and context-aware.")
        print("\n*** YOU ARE GOOD TO POST ON LINKEDIN! ***")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed.")
        print("Review failed tests above before launching.")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

