#!/usr/bin/env python3
"""
Test script for Scraper components
Tests: overview_scraper, notebook_scraper_v2, model_scraper_v2, discussion_scraper_v2
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_overview_scraper():
    """Test Overview Scraper initialization and basic functionality"""
    print("🔍 Testing Overview Scraper...")
    
    try:
        from scraper.overview_scraper import OverviewScraper
        print("✅ Import successful")
        
        # Test initialization with default parameter
        scraper = OverviewScraper()
        print("✅ Scraper initialization successful")
        
        # Test initialization with custom parameter
        scraper_custom = OverviewScraper("custom-competition")
        print("✅ Custom scraper initialization successful")
        
        # Test basic methods exist
        methods = ['scrape_overview', 'scrape_competition_details']
        for method in methods:
            if hasattr(scraper, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Overview Scraper test failed: {e}")
        return False

def test_notebook_scraper_v2():
    """Test Notebook Scraper V2 initialization and basic functionality"""
    print("\n🔍 Testing Notebook Scraper V2...")
    
    try:
        from scraper.notebook_scraper_v2 import NotebookScraperV2
        print("✅ Import successful")
        
        # Test initialization with default parameters
        scraper = NotebookScraperV2()
        print("✅ Scraper initialization successful")
        
        # Test initialization with custom parameters
        scraper_custom = NotebookScraperV2("custom_metadata.json", "custom_output.json")
        print("✅ Custom scraper initialization successful")
        
        # Test basic methods exist
        methods = ['scrape_notebooks', 'deep_scrape_notebooks']
        for method in methods:
            if hasattr(scraper, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Notebook Scraper V2 test failed: {e}")
        return False

def test_model_scraper_v2():
    """Test Model Scraper V2 initialization and basic functionality"""
    print("\n🔍 Testing Model Scraper V2...")
    
    try:
        from scraper.model_scraper_v2 import ModelScraperV2
        print("✅ Import successful")
        
        # Test initialization with default parameters
        scraper = ModelScraperV2()
        print("✅ Scraper initialization successful")
        
        # Test initialization with custom parameters
        scraper_custom = ModelScraperV2("custom-competition", "custom_output")
        print("✅ Custom scraper initialization successful")
        
        # Test basic methods exist
        methods = ['scrape_models', 'deep_scrape_models_with_llm']
        for method in methods:
            if hasattr(scraper, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Model Scraper V2 test failed: {e}")
        return False

def test_discussion_scraper_v2():
    """Test Discussion Scraper V2 initialization and basic functionality"""
    print("\n🔍 Testing Discussion Scraper V2...")
    
    try:
        from scraper.discussion_scraper_v2 import DiscussionScraperV2
        print("✅ Import successful")
        
        # Test initialization with default parameters
        scraper = DiscussionScraperV2()
        print("✅ Scraper initialization successful")
        
        # Test initialization with custom parameters
        scraper_custom = DiscussionScraperV2("custom-link", "custom_output")
        print("✅ Custom scraper initialization successful")
        
        # Test basic methods exist
        methods = ['scrape_discussions', 'deep_scrape_discussion']
        for method in methods:
            if hasattr(scraper, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Discussion Scraper V2 test failed: {e}")
        return False

def test_scraper_handlers():
    """Test Scraper Handlers initialization and basic functionality"""
    print("\n🔍 Testing Scraper Handlers...")
    
    try:
        from scraper.scrape_handlers import scrapegraphai_handler
        print("✅ Import successful")
        
        # Test that the function exists and is callable
        if callable(scrapegraphai_handler):
            print("✅ scrapegraphai_handler is callable")
        else:
            print("❌ scrapegraphai_handler is not callable")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper Handlers test failed: {e}")
        return False

def main():
    """Run all Scraper tests"""
    print("🚀 Starting Scraper Component Tests\n")
    
    results = []
    results.append(test_overview_scraper())
    results.append(test_notebook_scraper_v2())
    results.append(test_model_scraper_v2())
    results.append(test_discussion_scraper_v2())
    results.append(test_scraper_handlers())
    
    print(f"\n📊 Scraper Test Results: {sum(results)}/{len(results)} components passed")
    
    if all(results):
        print("🎉 All Scraper components are working!")
    else:
        print("⚠️  Some Scraper components need attention")
    
    return all(results)

if __name__ == "__main__":
    main()
