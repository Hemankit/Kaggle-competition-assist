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
    response = requests.post(url, json=data, timeout=30)
    result = response.json()
    
    # Extract key fields
    agents_used = result.get('agents_used', [])
    confidence = result.get('confidence', 0)
    system = result.get('system', 'unknown')
    response_text = result.get('response', '')[:200]  # First 200 chars
    
    print(f"\n✅ RESULT:")
    print(f"  agents_used: {agents_used}")
    print(f"  confidence: {confidence}")
    print(f"  system: {system}")
    print(f"\n📝 Response preview:")
    print(f"  {response_text}...")
    
    # Check if fix worked
    if "competition_summary_agent" in agents_used:
        print(f"\n🎉 SUCCESS! Evaluation query now shows competition_summary_agent")
        print(f"✅ Confidence: {confidence} (should be 0.95)")
        exit(0)
    else:
        print(f"\n❌ FAILED! Still showing: {agents_used}")
        exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)

