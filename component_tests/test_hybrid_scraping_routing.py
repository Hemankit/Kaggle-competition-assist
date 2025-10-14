#!/usr/bin/env python3
"""
Test script for Hybrid Scraping Routing components
Tests: agent_router, scraping_decider, deep_scraper_executor, result_structurer, chain_builder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_agent_router():
    """Test Agent Router initialization and basic functionality"""
    print("🔍 Testing Agent Router...")
    
    try:
        from hybrid_scraping_routing.agent_router import HybridScraperRouterAgent
        print("✅ Import successful")
        
        # Test initialization
        agent = HybridScraperRouterAgent()
        print("✅ Agent initialization successful")
        
        # Test basic methods exist
        methods = ['route_query', 'should_deep_scrape', 'execute_deep_scrape']
        for method in methods:
            if hasattr(agent, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Router test failed: {e}")
        return False

def test_scraping_decider():
    """Test Scraping Decider initialization and basic functionality"""
    print("\n🔍 Testing Scraping Decider...")
    
    try:
        from hybrid_scraping_routing.scraping_decider import ScrapingDecider
        print("✅ Import successful")
        
        # Test initialization
        decider = ScrapingDecider()
        print("✅ Decider initialization successful")
        
        # Test basic methods exist
        methods = ['should_deep_scrape']
        for method in methods:
            if hasattr(decider, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraping Decider test failed: {e}")
        return False

def test_deep_scraper_executor():
    """Test Deep Scraper Executor initialization and basic functionality"""
    print("\n🔍 Testing Deep Scraper Executor...")
    
    try:
        from hybrid_scraping_routing.deep_scraper_executor import DeepScraperExecutor
        print("✅ Import successful")
        
        # Test initialization
        executor = DeepScraperExecutor()
        print("✅ Executor initialization successful")
        
        # Test basic methods exist
        methods = ['execute_deep_scrape', 'deep_scrape_item']
        for method in methods:
            if hasattr(executor, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Deep Scraper Executor test failed: {e}")
        return False

def test_result_structurer():
    """Test Result Structurer initialization and basic functionality"""
    print("\n🔍 Testing Result Structurer...")
    
    try:
        from hybrid_scraping_routing.result_structurer import ResultStructurer
        print("✅ Import successful")
        
        # Test initialization
        structurer = ResultStructurer()
        print("✅ Structurer initialization successful")
        
        # Test basic methods exist
        methods = ['structure_results', 'annotate_with_metadata']
        for method in methods:
            if hasattr(structurer, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Result Structurer test failed: {e}")
        return False

def test_chain_builder():
    """Test Chain Builder initialization and basic functionality"""
    print("\n🔍 Testing Chain Builder...")
    
    try:
        from hybrid_scraping_routing.chain_builer import build_scraping_decision_chain
        print("✅ Import successful")
        
        # Test that the function exists and is callable
        if callable(build_scraping_decision_chain):
            print("✅ build_scraping_decision_chain is callable")
        else:
            print("❌ build_scraping_decision_chain is not callable")
        
        return True
        
    except Exception as e:
        print(f"❌ Chain Builder test failed: {e}")
        return False

def test_redis_cache():
    """Test Redis Cache initialization and basic functionality"""
    print("\n🔍 Testing Redis Cache...")
    
    try:
        from hybrid_scraping_routing.redis_cache import RedisCache
        print("✅ Import successful")
        
        # Test initialization
        cache = RedisCache()
        print("✅ Cache initialization successful")
        
        # Test basic methods exist
        methods = ['get_cache', 'update_cache', 'is_deep_scraped']
        for method in methods:
            if hasattr(cache, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis Cache test failed: {e}")
        return False

def main():
    """Run all Hybrid Scraping Routing tests"""
    print("🚀 Starting Hybrid Scraping Routing Component Tests\n")
    
    results = []
    results.append(test_agent_router())
    results.append(test_scraping_decider())
    results.append(test_deep_scraper_executor())
    results.append(test_result_structurer())
    results.append(test_chain_builder())
    results.append(test_redis_cache())
    
    print(f"\n📊 Hybrid Scraping Routing Test Results: {sum(results)}/{len(results)} components passed")
    
    if all(results):
        print("🎉 All Hybrid Scraping Routing components are working!")
    else:
        print("⚠️  Some Hybrid Scraping Routing components need attention")
    
    return all(results)

if __name__ == "__main__":
    main()
