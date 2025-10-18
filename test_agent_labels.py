#!/usr/bin/env python3
"""
Test script to verify backend returns correct agent labels
"""
import requests
import json

def test_backend():
    url = 'http://localhost:5000/component-orchestrator/query'
    
    tests = [
        {
            'name': 'Data Query',
            'payload': {
                'query': 'What columns are in the data?',
                'competition_id': 'titanic',
                'session_id': 'test-001'
            }
        },
        {
            'name': 'Evaluation Query',
            'payload': {
                'query': 'Explain the evaluation metric',
                'competition_id': 'titanic',
                'session_id': 'test-002'
            }
        },
        {
            'name': 'Notebooks Query',
            'payload': {
                'query': 'Show me top notebooks',
                'competition_id': 'titanic',
                'session_id': 'test-003'
            }
        }
    ]
    
    for test in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {test['name']}")
        print('='*60)
        
        try:
            response = requests.post(url, json=test['payload'], timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents_used', [])
                confidence = data.get('confidence', 0)
                system = data.get('system', 'unknown')
                
                print(f"✅ Agents Used: {agents}")
                print(f"✅ Confidence: {confidence}")
                print(f"✅ System: {system}")
                
                # Highlight if using fallback
                if 'fallback_agent' in agents:
                    print("⚠️  WARNING: Still using fallback_agent!")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == '__main__':
    test_backend()
