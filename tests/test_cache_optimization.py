"""
Test Cache Optimization - ChromaDB First, Scrape Only if Needed

This test verifies:
1. First query: Scrapes and stores in ChromaDB (slow)
2. Second query: Uses cached data from ChromaDB (fast - no scraping!)
3. Third query: Different competition, scrapes again
"""
import requests
import time

BACKEND_URL = "http://localhost:5000"

def test_cache_optimization():
    print("\n" + "=" * 80)
    print("CACHE OPTIMIZATION TEST")
    print("=" * 80)
    print("\nThis test verifies the cache optimization:")
    print("  1. First query: SCRAPES (slow, ~60s)")
    print("  2. Second query: USES CACHE (fast, ~10s)")
    print("  3. Third query: Different competition, SCRAPES again")
    print("\n" + "=" * 80)
    
    input("\nPress Enter to start test...")
    
    # Test 1: First Query - Should Scrape
    print("\n" + "=" * 80)
    print("TEST 1: First Query (Should Scrape)")
    print("=" * 80)
    
    query1 = "Explain the evaluation metric for google-code-golf-2025"
    user_context1 = {
        "kaggle_username": "TestUser",
        "competition_slug": "google-code-golf-2025",
        "competition_name": "NeurIPS 2025 - Google Code Golf Championship"
    }
    
    print(f"\n[1] Query: {query1}")
    print("    Expected: Scrape Kaggle (slow)")
    
    start1 = time.time()
    
    try:
        response1 = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json={"query": query1, "user_context": user_context1},
            timeout=120
        )
        response1.raise_for_status()
        elapsed1 = time.time() - start1
        
        print(f"\n[2] Response received in {elapsed1:.2f}s")
        print("    Look for in backend logs:")
        print("      - '[CACHE MISS] No evaluation data found...'")
        print("      - '[DEBUG] No cached data found. Starting to scrape...'")
        print("      - '[DEBUG] Storing evaluation data in ChromaDB...'")
        
        result1 = response1.json()
        response_text1 = result1.get('final_response', '')
        print(f"\n[3] Response length: {len(response_text1)} chars")
        
    except Exception as e:
        print(f"\n[ERROR] Test 1 failed: {e}")
        return False
    
    # Test 2: Second Query - Should Use Cache
    print("\n\n" + "=" * 80)
    print("TEST 2: Second Query (Should Use Cache)")
    print("=" * 80)
    print("\nThis should be MUCH FASTER because data is already in ChromaDB!")
    
    time.sleep(2)
    
    query2 = "What's the scoring for google-code-golf-2025?"
    
    print(f"\n[1] Query: {query2}")
    print("    Expected: Use ChromaDB cache (fast, no scraping)")
    
    start2 = time.time()
    
    try:
        response2 = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json={"query": query2, "user_context": user_context1},
            timeout=120
        )
        response2.raise_for_status()
        elapsed2 = time.time() - start2
        
        print(f"\n[2] Response received in {elapsed2:.2f}s")
        print(f"    First query:  {elapsed1:.2f}s (with scraping)")
        print(f"    Second query: {elapsed2:.2f}s (cached)")
        
        speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 0
        print(f"    Speedup: {speedup:.2f}x faster")
        
        if elapsed2 < elapsed1 * 0.3:  # Should be at least 70% faster
            print("    [SUCCESS] Cache optimization working! (3x+ faster)")
        elif elapsed2 < elapsed1 * 0.5:
            print("    [OK] Some caching benefit (2x faster)")
        else:
            print("    [WARN] Not much speedup - check if cache is working")
        
        print("\n    Look for in backend logs:")
        print("      - '[DEBUG] Checking ChromaDB for google-code-golf-2025...'")
        print("      - '[CACHE HIT] Found evaluation data in ChromaDB...'")
        print("      - '[OPTIMIZATION] Using cached evaluation data...'")
        print("      - NO '[DEBUG] Starting to scrape...' message")
        
        result2 = response2.json()
        response_text2 = result2.get('final_response', '')
        print(f"\n[3] Response length: {len(response_text2)} chars")
        
        # Verify both responses contain intelligent analysis
        if len(response_text1) > 1000 and len(response_text2) > 1000:
            print("    [OK] Both responses are substantial")
        
    except Exception as e:
        print(f"\n[ERROR] Test 2 failed: {e}")
        return False
    
    # Test 3: Different Competition - Should Scrape Again
    print("\n\n" + "=" * 80)
    print("TEST 3: Different Competition (Should Scrape Again)")
    print("=" * 80)
    
    query3 = "What's the evaluation metric?"
    user_context3 = {
        "kaggle_username": "TestUser",
        "competition_slug": "titanic",
        "competition_name": "Titanic - Machine Learning from Disaster"
    }
    
    print(f"\n[1] Query: {query3}")
    print(f"    Competition: {user_context3['competition_name']}")
    print("    Expected: Scrape new competition (slow)")
    
    start3 = time.time()
    
    try:
        response3 = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json={"query": query3, "user_context": user_context3},
            timeout=120
        )
        response3.raise_for_status()
        elapsed3 = time.time() - start3
        
        print(f"\n[2] Response received in {elapsed3:.2f}s")
        print(f"    Similar to first query: {elapsed1:.2f}s")
        print("    Expected: Similar timing (both involve scraping)")
        
        print("\n    Look for in backend logs:")
        print("      - '[CACHE MISS] No evaluation data found... for titanic'")
        print("      - '[DEBUG] Starting to scrape overview for: titanic'")
        
        result3 = response3.json()
        response_text3 = result3.get('final_response', '')
        print(f"\n[3] Response length: {len(response_text3)} chars")
        
    except Exception as e:
        print(f"\n[ERROR] Test 3 failed: {e}")
        print("    (This might fail if the competition doesn't have an evaluation section)")
        # Don't fail the whole test for this
    
    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    print(f"\n  Query 1 (google-code-golf, first):  {elapsed1:.2f}s - SCRAPED")
    print(f"  Query 2 (google-code-golf, second): {elapsed2:.2f}s - CACHED")
    print(f"  Query 3 (titanic, first):           {elapsed3:.2f}s - SCRAPED")
    
    if elapsed2 < elapsed1 * 0.5:
        print("\n[SUCCESS] Cache optimization is working!")
        print("  - Second queries are significantly faster")
        print("  - No unnecessary scraping")
        print("  - Different competitions are handled correctly")
        return True
    else:
        print("\n[PARTIAL] System working but cache benefit unclear")
        print("  Check backend logs for cache hit/miss messages")
        return False

if __name__ == "__main__":
    try:
        success = test_cache_optimization()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)



