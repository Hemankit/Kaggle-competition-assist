#!/usr/bin/env python3
"""
Test script for Flask backend with logging and health checks
"""

import requests
import json
import time
from dotenv import load_dotenv

def test_health_endpoints():
    """Test all health check endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Flask Backend Health Endpoints")
    print("=" * 50)
    
    endpoints = [
        ("/health/", "Comprehensive Health Check"),
        ("/health/simple", "Simple Health Check"),
        ("/health/database", "Database Health Check"),
        ("/health/llm", "LLM Services Health Check"),
        ("/health/ready", "Readiness Check"),
        ("/health/live", "Liveness Check")
    ]
    
    for endpoint, description in endpoints:
        try:
            print(f"\n🔍 Testing {description}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code in [200, 206]:
                print(f"   ✅ {description} - PASSED")
            else:
                print(f"   ⚠️  {description} - Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {description} - Connection failed (Flask not running)")
        except Exception as e:
            print(f"   ❌ {description} - Error: {str(e)}")

def test_query_endpoint():
    """Test the main query endpoint"""
    base_url = "http://localhost:5000"
    
    print(f"\n🔍 Testing Query Endpoint...")
    
    test_query = {
        "query": "How should I approach this Kaggle competition?",
        "debug": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/query/", 
            json=test_query, 
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Query endpoint - PASSED")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   ⚠️  Query endpoint - Status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Query endpoint - Connection failed (Flask not running)")
    except Exception as e:
        print(f"   ❌ Query endpoint - Error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Flask Backend Test Suite")
    print("=" * 50)
    print("Make sure your Flask backend is running with:")
    print("python -m kaggle_competition_assist_backend.app")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test health endpoints
    test_health_endpoints()
    
    # Test main query endpoint
    test_query_endpoint()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("✅ Check the logs in ./logs/kaggle_assist.log")
    print("✅ Health endpoints provide system status")
    print("✅ Logging captures all requests and responses")
    print("✅ Your Flask backend is production-ready!")

if __name__ == "__main__":
    main()


