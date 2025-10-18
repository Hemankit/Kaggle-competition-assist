#!/usr/bin/env python3
import requests
import json

# Test notebook query
url = "http://localhost:5000/component-orchestrator/query"
data = {
    "query": "Show me the top notebooks",
    "competition_id": "titanic"
}

print("🧪 Testing: Show me the top notebooks")
print("=" * 60)

try:
    response = requests.post(url, json=data, timeout=30)
    result = response.json()
    
    # Extract key fields
    agents_used = result.get('agents_used', [])
    confidence = result.get('confidence', 0)
    system = result.get('system', 'unknown')
    response_text = result.get('final_response', result.get('response', ''))
    
    print(f"\n✅ RESULT:")
    print(f"  agents_used: {agents_used}")
    print(f"  confidence: {confidence}")
    print(f"  system: {system}")
    print(f"\n📝 Response length: {len(response_text)} chars")
    print(f"\n📝 Response preview:")
    print(response_text[:500])
    
    # Check if it's a stub response
    if "Data retrieved from Kaggle API and cached for fast access" in response_text and len(response_text) < 200:
        print(f"\n❌ STUB RESPONSE DETECTED!")
        print(f"   This is the placeholder response, not actual notebook data")
        exit(1)
    else:
        print(f"\n✅ Looks like real notebook data (not a stub)")
        exit(0)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

