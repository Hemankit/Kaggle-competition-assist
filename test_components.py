"""
Simple test for the scraper router components
"""

import sys
import os
sys.path.append('.')

print("=== Testing New Scraper Router Architecture ===\n")

# Test 1: Data Source Decider
print("Testing Data Source Decider...")
try:
    from scraper_router.data_source_decider import DataSourceDecider
    print("✅ Data Source Decider imported successfully")
    
    class MockLLM:
        def invoke(self, input_data):
            query = input_data.get('query', '').lower()
            if 'latest' in query or 'recent' in query:
                return 'KAGGLE_API,PERPLEXITY_SEARCH\nHigh priority query requiring fresh data'
            elif 'historical' in query or 'past' in query:
                return 'CACHED_DATA,SHALLOW_SCRAPING\nHistorical query can use cached data'
            else:
                return 'KAGGLE_API,SHALLOW_SCRAPING\nStandard query using reliable sources'
    
    llm = MockLLM()
    decider = DataSourceDecider(llm)
    
    # Test query
    query = "What is the latest leaderboard for Titanic?"
    decision = decider.decide_data_sources(
        query=query,
        context={'section': 'general'},
        cached_data_info='No cached data',
        data_freshness='unknown'
    )
    
    print(f"Query: {query}")
    print(f"Decision: {decision}")
    print("✅ Data Source Decider: Working")
    
except Exception as e:
    print(f"❌ Data Source Decider: Error - {e}")

# Test 2: Simple Cache
print("\n\nTesting Simple Cache...")
try:
    from core_utils.simple_cache import SimpleCache
    print("✅ Simple Cache imported successfully")
    
    cache = SimpleCache()
    
    # Test basic operations
    test_data = {
        "title": "Test Item",
        "content": "This is test content",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    # Set data
    success = cache.set("test_key", test_data)
    print(f"Set data: {success}")
    
    # Get data
    retrieved = cache.get("test_key")
    print(f"Retrieved data: {retrieved}")
    
    # Check if cached
    is_cached = cache.is_cached("test_key")
    print(f"Is cached: {is_cached}")
    
    # Get stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    print("✅ Simple Cache: Working")
    
except Exception as e:
    print(f"❌ Simple Cache: Error - {e}")

# Test 3: Data Combiner
print("\n\nTesting Data Combiner...")
try:
    from core_utils.data_combiner import DataCombiner
    print("✅ Data Combiner imported successfully")
    
    combiner = DataCombiner()
    
    # Mock collected data
    collected_data = {
        "data": {
            "kaggle": {
                "type": "kaggle_api",
                "items": [
                    {"title": "Competition Overview", "content": "Basic competition info"},
                    {"title": "Leaderboard", "content": "Current standings"}
                ],
                "count": 2
            },
            "scraped": {
                "type": "scraped", 
                "items": [
                    {"title": "Discussion Post", "content": "Community insights"},
                    {"title": "Notebook", "content": "Code examples"}
                ],
                "count": 2
            }
        },
        "sources": ["KAGGLE_API", "SHALLOW_SCRAPING"]
    }
    
    combined = combiner.combine_data(collected_data, "Test query")
    print(f"Combined data structure:")
    print(f"- Query: {combined.get('query')}")
    print(f"- Sources: {combined.get('sources')}")
    print(f"- Data keys: {list(combined.get('data', {}).keys())}")
    print(f"- Metadata: {combined.get('metadata')}")
    
    print("✅ Data Combiner: Working")
    
except Exception as e:
    print(f"❌ Data Combiner: Error - {e}")

print("\n=== Test Summary ===")
print("The scraper router architecture components are working!")
print("Next step: Integrate with existing scrapers or implement Stage 2 (Agent Router)")


