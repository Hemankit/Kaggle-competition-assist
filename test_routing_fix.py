#!/usr/bin/env python3
"""
Test script to verify routing fixes and absence of fallback responses
"""

import requests

url = 'http://localhost:5000/component-orchestrator/query'
headers = {'Content-Type': 'application/json'}

queries = [
    ('What columns are in the titanic data?', 'data query'),
    ('What is the evaluation metric?', 'evaluation query'),
    ('What discussions exist?', 'discussion query'),
    ('Explain accuracy metric', 'metric explanation'),
]

print('\n' + '='*70)
print('🎯 TESTING ROUTING FIXES AND FALLBACK ELIMINATION')
print('='*70)

fallback_count = 0
success_count = 0

for query, desc in queries:
    print(f'\n🔷 Test: {desc}')
    print(f'   Query: "{query}"')
    print('   ' + '-' * 60)
    
    try:
        r = requests.post(url, json={'query': query, 'competition_id': 'titanic', 'session_id': 'test'}, 
                         headers=headers, timeout=20)
        result = r.json()
        agents = result.get('agents_used', [])
        confidence = result.get('confidence', 0)
        system = result.get('system', 'unknown')
        
        print(f'   Agents: {agents}')
        print(f'   Confidence: {confidence}')
        print(f'   System: {system}')
        
        if 'fallback_agent' in str(agents):
            print('   ❌ FALLBACK DETECTED!')
            fallback_count += 1
        else:
            print('   ✅ Real agent handled it!')
            success_count += 1
    except Exception as e:
        print(f'   ❌ ERROR: {e}')

print('\n' + '='*70)
print(f'SUMMARY: {success_count} real agents, {fallback_count} fallbacks')
print('='*70)

if fallback_count == 0:
    print('✅✅✅ SUCCESS! No fallback responses detected!')
else:
    print(f'⚠️  WARNING: {fallback_count} fallback response(s) still present')
