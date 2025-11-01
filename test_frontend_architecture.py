#!/usr/bin/env python3
"""
Frontend Architecture Detection Test
This shows how to identify which architecture is running from the frontend.
"""

import requests
import json
from datetime import datetime

def test_architecture_detection():
    """Test how to identify the backend architecture from frontend."""
    
    print("🔍 Frontend Architecture Detection Test")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Method 1: Health Check
    print("\n1️⃣ Health Check Method:")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend Status: {data.get('status', 'unknown')}")
            print(f"   🔧 New System Available: {data.get('new_system_available', False)}")
            print(f"   🔧 Old System Available: {data.get('old_system_available', False)}")
            print(f"   🔧 Kaggle API Available: {data.get('kaggle_api_available', False)}")
            
            # Determine architecture
            if data.get('new_system_available'):
                print("   🎯 ARCHITECTURE: NEW Multi-Agent System")
            elif data.get('old_system_available'):
                print("   🎯 ARCHITECTURE: OLD Multi-Agent System")
            else:
                print("   🎯 ARCHITECTURE: No Multi-Agent System")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Method 2: API Endpoint Testing
    print("\n2️⃣ API Endpoint Method:")
    
    # Test legacy endpoint
    print("\n   Testing Legacy Endpoint (/api/query):")
    try:
        response = requests.post(f"{base_url}/api/query", json={
            'query': 'Test query for architecture detection',
            'context': {'section': 'general'}
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            print("   🎯 ARCHITECTURE: OLD (Legacy endpoint working)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test new endpoint
    print("\n   Testing New Endpoint (/api/v2/query):")
    try:
        response = requests.post(f"{base_url}/api/v2/query", json={
            'query': 'Test query for architecture detection',
            'context': {'section': 'general'},
            'mode': 'auto'
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            print("   🎯 ARCHITECTURE: NEW (Multi-Agent endpoint working)")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 3: Response Structure Analysis
    print("\n3️⃣ Response Structure Analysis:")
    print("   OLD Architecture Response Keys:")
    print("   - 'query', 'context', 'stage1_data', 'stage2_response'")
    print("   - 'architecture': 'two_stage'")
    print("   - 'current_stage': 1")
    
    print("\n   NEW Architecture Response Keys:")
    print("   - 'query', 'context', 'mode'")
    print("   - 'success': True/False")
    print("   - 'orchestrator_used': 'crewai'/'autogen'/'langgraph'/'dynamic'")
    print("   - 'agents_used': ['agent1', 'agent2']")
    print("   - 'external_search_used': True/False")
    print("   - 'response': 'Generated response'")
    
    # Method 4: Frontend Integration
    print("\n4️⃣ Frontend Integration:")
    print("   To detect architecture in your frontend:")
    print("   ```javascript")
    print("   // Check health endpoint")
    print("   const healthResponse = await fetch('/health');")
    print("   const healthData = await healthResponse.json();")
    print("   ")
    print("   if (healthData.new_system_available) {")
    print("       console.log('Using NEW Multi-Agent Architecture');")
    print("       // Use /api/v2/query endpoint")
    print("   } else if (healthData.old_system_available) {")
    print("       console.log('Using OLD Multi-Agent Architecture');")
    print("       // Use /api/query endpoint")
    print("   } else {")
    print("       console.log('No Multi-Agent System Available');")
    print("   }")
    print("   ```")
    
    print("\n" + "=" * 50)
    print("✅ Architecture detection test completed!")

if __name__ == "__main__":
    test_architecture_detection()







