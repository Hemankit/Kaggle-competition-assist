#!/usr/bin/env python3
"""
Test script for Kaggle_Fetcher components
Tests: kaggle_api_client, kaggle_fetcher
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_kaggle_api_client():
    """Test Kaggle API client initialization and basic functionality"""
    print("🔍 Testing Kaggle API Client...")
    
    try:
        from Kaggle_Fetcher.kaggle_api_client import KaggleAPIClient
        print("✅ Import successful")
        
        # Test initialization
        client = KaggleAPIClient()
        print("✅ Client initialization successful")
        
        # Test basic methods exist
        methods = ['get_competition_list', 'get_competition_details', 'get_leaderboard', 'get_datasets', 'get_notebooks']
        for method in methods:
            if hasattr(client, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Kaggle API Client test failed: {e}")
        return False

def test_kaggle_fetcher():
    """Test Kaggle fetcher initialization and basic functionality"""
    print("\n🔍 Testing Kaggle Fetcher...")
    
    try:
        from Kaggle_Fetcher.kaggle_fetcher import KaggleFetcher
        print("✅ Import successful")
        
        # Test initialization
        fetcher = KaggleFetcher()
        print("✅ Fetcher initialization successful")
        
        # Test basic methods exist
        methods = ['fetch_competition_data', 'fetch_leaderboard', 'fetch_datasets', 'fetch_notebooks']
        for method in methods:
            if hasattr(fetcher, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Kaggle Fetcher test failed: {e}")
        return False

def main():
    """Run all Kaggle_Fetcher tests"""
    print("🚀 Starting Kaggle_Fetcher Component Tests\n")
    
    results = []
    results.append(test_kaggle_api_client())
    results.append(test_kaggle_fetcher())
    
    print(f"\n📊 Kaggle_Fetcher Test Results: {sum(results)}/{len(results)} components passed")
    
    if all(results):
        print("🎉 All Kaggle_Fetcher components are working!")
    else:
        print("⚠️  Some Kaggle_Fetcher components need attention")
    
    return all(results)

if __name__ == "__main__":
    main()
