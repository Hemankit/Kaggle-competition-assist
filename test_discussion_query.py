#!/usr/bin/env python3
import requests
import json

# Test discussion query
url = "http://localhost:5000/component-orchestrator/query"
data = {
    "query": "Are there any discussions about overfitting?",
    "competition_id": "titanic"
}

print("🧪 Testing: Are there any discussions about overfitting?")
print("=" * 60)

try:
    response = requests.post(url, json=data, timeout=60)
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
    print(f"\n📝 Full response:")
    print(response_text)
    
    # Check quality
    if len(response_text) < 500:
        print(f"\n⚠️ WARNING: Response is too short (< 500 chars)")
    
    if "This discussion does not mention" in response_text:
        print(f"\n⚠️ WARNING: Response includes negative message about single discussion")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

