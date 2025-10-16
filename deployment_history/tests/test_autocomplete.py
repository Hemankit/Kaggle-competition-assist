#!/usr/bin/env python3
"""Test competition autocomplete/search functionality"""
import requests

BASE_URL = 'http://localhost:5000'

test_queries = [
    "titanic",
    "house",
    "digit",
]

print('='*70)
print('🔍 TESTING COMPETITION AUTOCOMPLETE')
print('='*70)
print()

for query in test_queries:
    print(f'Query: "{query}"')
    
    try:
        response = requests.post(
            f'{BASE_URL}/session/competitions/search',
            json={"query": query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            competitions = data.get('competitions', [])
            print(f'  ✅ Found {len(competitions)} competitions')
            
            for i, comp in enumerate(competitions[:3], 1):
                print(f'     {i}. {comp.get("name", "N/A")[:50]} ({comp.get("slug", "N/A")})')
        else:
            print(f'  ❌ HTTP {response.status_code}: {response.text[:100]}')
            
    except Exception as e:
        print(f'  ❌ Error: {str(e)[:100]}')
    
    print()

print('='*70)
print('✅ Autocomplete test complete!')
print('='*70)


