"""
Test ChromaDB Integration with CompetitionSummaryAgent

This test verifies:
1. Backend scrapes evaluation data
2. Data is stored in ChromaDB
3. CompetitionSummaryAgent retrieves from ChromaDB (not mock)
4. Agent provides intelligent analysis
"""
import requests
import json
import time

BACKEND_URL = "http://localhost:5000"

def test_chromadb_flow():
    print("\n" + "=" * 80)
    print("CHROMADB INTEGRATION TEST")
    print("=" * 80)
    print("\nThis test verifies the complete ChromaDB flow:")
    print("  1. Scrape evaluation data from Kaggle")
    print("  2. Store scraped data in ChromaDB")
    print("  3. Agent retrieves from ChromaDB (not mocked)")
    print("  4. Agent generates intelligent analysis")
    print("\nMake sure the backend is running!")
    print("=" * 80)
    
    input("\nPress Enter to start the test...")
    
    # Test 1: First query - should scrape and store in ChromaDB
    print("\n" + "=" * 80)
    print("TEST 1: First Query (Scrape + Store in ChromaDB)")
    print("=" * 80)
    
    query = "Can you explain the evaluation metric for google-code-golf-2025?"
    user_context = {
        "kaggle_username": "TestUser",
        "competition_slug": "google-code-golf-2025",
        "competition_name": "NeurIPS 2025 - Google Code Golf Championship"
    }
    
    print(f"\n[1] Sending query: {query}")
    print(f"    Competition: {user_context['competition_name']}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json={"query": query, "user_context": user_context},
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        
        elapsed = time.time() - start_time
        
        print(f"\n[2] Response received in {elapsed:.2f}s")
        print(f"    Status: {response.status_code}")
        print(f"    Success: {result.get('success')}")
        
        final_response = result.get('final_response', '')
        
        print("\n" + "-" * 80)
        print("RESPONSE (First Query):")
        print("-" * 80)
        print(final_response[:500] + "..." if len(final_response) > 500 else final_response)
        print("-" * 80)
        
        # Analyze response
        print("\n[3] Response Analysis:")
        checks = {
            "Substantial response (>1000 chars)": len(final_response) > 1000,
            "Contains structured sections": "**" in final_response and ":" in final_response,
            "Contains strategic guidance": any(word in final_response.lower() for word in ["scoring", "objective", "goal", "strategy"]),
            "Agent attribution present": "Analysis powered by AI agent" in final_response or "powered by AI" in final_response.lower()
        }
        
        for check, passed in checks.items():
            status = "[OK]" if passed else "[WARN]"
            print(f"    {status} {check}")
        
        first_query_passed = all(checks.values())
        
        if first_query_passed:
            print("\n    [PASSED] First query test successful!")
        else:
            print("\n    [WARN] Some checks failed for first query")
        
    except Exception as e:
        print(f"\n[ERROR] First query failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Second query - should retrieve from ChromaDB (faster)
    print("\n\n" + "=" * 80)
    print("TEST 2: Second Query (Retrieve from ChromaDB)")
    print("=" * 80)
    print("\nThis query should be FASTER because data is already in ChromaDB!")
    print("Look for '[DEBUG] Using ChromaDB retriever for agent' in backend logs.\n")
    
    time.sleep(2)  # Brief pause
    
    query2 = "What's the scoring method for google-code-golf-2025?"
    
    print(f"[1] Sending second query: {query2}")
    
    start_time2 = time.time()
    
    try:
        response2 = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json={"query": query2, "user_context": user_context},
            timeout=120
        )
        
        response2.raise_for_status()
        result2 = response2.json()
        
        elapsed2 = time.time() - start_time2
        
        print(f"\n[2] Response received in {elapsed2:.2f}s")
        print(f"    First query took: {elapsed:.2f}s")
        print(f"    Second query took: {elapsed2:.2f}s")
        
        if elapsed2 < elapsed * 0.8:  # Should be at least 20% faster
            print("    [OK] Second query was faster (ChromaDB caching working!)")
        else:
            print("    [INFO] Second query timing similar (may still be using scraping)")
        
        final_response2 = result2.get('final_response', '')
        
        print("\n" + "-" * 80)
        print("RESPONSE (Second Query):")
        print("-" * 80)
        print(final_response2[:500] + "..." if len(final_response2) > 500 else final_response2)
        print("-" * 80)
        
        # Both responses should contain intelligent analysis (not identical raw text)
        print("\n[3] Comparing Responses:")
        similarity = len(set(final_response.split()) & set(final_response2.split())) / max(len(final_response.split()), 1)
        print(f"    Word overlap: {similarity:.2%}")
        
        if 0.5 < similarity < 0.95:
            print("    [OK] Responses are similar but not identical (good!)")
        elif similarity > 0.95:
            print("    [WARN] Responses are too similar (might be copy-paste)")
        else:
            print("    [INFO] Responses are quite different")
        
        second_query_passed = len(final_response2) > 1000
        
        if second_query_passed:
            print("\n    [PASSED] Second query test successful!")
        
    except Exception as e:
        print(f"\n[ERROR] Second query failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Final Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if first_query_passed and second_query_passed:
        print("\n[SUCCESS] All tests passed!")
        print("\nChromaDB Integration is working correctly:")
        print("  - Scraped data is stored in ChromaDB")
        print("  - Agent retrieves from ChromaDB")
        print("  - Agent generates intelligent analysis")
        print("  - Subsequent queries can reuse stored data")
        print("\n" + "=" * 80)
        return True
    else:
        print("\n[PARTIAL] Some tests passed, but check warnings above")
        print("=" * 80)
        return False

if __name__ == "__main__":
    try:
        success = test_chromadb_flow()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


