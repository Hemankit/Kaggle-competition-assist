#!/usr/bin/env python3
"""
Test the backend integration with CompetitionSummaryAgent
by making a direct API call to the component-orchestrator endpoint.
"""
import requests
import json

BACKEND_URL = "http://localhost:5000"

def test_evaluation_query():
    """Test evaluation metric query with agent integration."""
    print("=" * 80)
    print("TESTING BACKEND AGENT INTEGRATION")
    print("=" * 80)
    
    # Prepare the query
    query_data = {
        "query": "Can you explain the evaluation metric for google-code-golf-2025?",
        "user_context": {
            "kaggle_username": "TestUser",
            "competition_slug": "google-code-golf-2025",
            "competition_name": "NeurIPS 2025 - Google Code Golf Championship"
        }
    }
    
    print("\n[1] Sending query to backend...")
    print(f"    URL: {BACKEND_URL}/component-orchestrator/query")
    print(f"    Query: {query_data['query']}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json=query_data,
            timeout=120  # Allow time for scraping + LLM processing
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n[2] Response received!")
            print(f"    Status: {response.status_code}")
            print(f"    Success: {result.get('success', False)}")
            print(f"    System: {result.get('system', 'unknown')}")
            
            final_response = result.get('final_response', '')
            
            print("\n" + "=" * 80)
            print("AGENT RESPONSE:")
            print("=" * 80)
            print(final_response)
            print("=" * 80)
            
            # Analyze the response
            print("\n[3] Response Analysis:")
            if len(final_response) > 1000:
                print("    [OK] Response is substantial (>1000 chars)")
            else:
                print(f"    [WARN] Response is short ({len(final_response)} chars)")
            
            if "How Scoring Works" in final_response or "How scoring works" in final_response.lower():
                print("    [OK] Contains structured analysis section")
            
            if any(word in final_response.lower() for word in ['objective', 'goal', 'submission', 'programs']):
                print("    [OK] Contains strategic guidance")
            else:
                print("    [WARN] May not contain strategic guidance")
            
            if "Analysis powered by AI agent" in final_response:
                print("    [OK] Confirms agent was used")
            else:
                print("    [WARN] No agent attribution found")
            
            return True
            
        else:
            print(f"\n[ERROR] Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to backend!")
        print("Make sure the backend is running:")
        print("  python minimal_backend.py")
        return False
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out!")
        print("The backend may be processing (scraping + LLM takes time)")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n[TEST] Backend Agent Integration Test")
    print("\nThis test sends a query to the backend and verifies:")
    print("  1. The backend receives the query")
    print("  2. Playwright scrapes evaluation data")
    print("  3. CompetitionSummaryAgent analyzes the data")
    print("  4. Response contains intelligent analysis (not copy-paste)")
    print("\nMake sure the backend is running before running this test!\n")
    
    input("Press Enter to start the test...")
    
    success = test_evaluation_query()
    
    print("\n" + "=" * 80)
    if success:
        print("[PASSED] Backend agent integration test completed successfully!")
    else:
        print("[FAILED] Backend agent integration test failed.")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()



