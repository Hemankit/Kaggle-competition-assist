#!/usr/bin/env python3
import requests
import json

# Test evaluation query
url = "http://localhost:5000/component-orchestrator/query"
data = {
    "query": "Explain the evaluation metric",
    "competition_id": "titanic"
}

print("🧪 Testing: Explain the evaluation metric")
print("=" * 60)

try:
    response = requests.post(url, json=data, timeout=60)  # Increased timeout for LLM generation
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
    
    # Check if it has code examples
    if "```python" in response_text:
        print(f"\n✅ SUCCESS! Response includes Python code examples")
        exit(0)
    else:
        print(f"\n⚠️ WARNING: Response doesn't include Python code examples")
        print(f"   The enhanced prompt might not be used")
        exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

