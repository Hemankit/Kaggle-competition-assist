#!/usr/bin/env python3
"""Final system test - verify all components working"""
import requests
import sys

BASE_URL = 'http://localhost:5000'

tests = [
    {
        "name": "Overview/Evaluation Query",
        "query": "What is the evaluation metric for this competition?",
        "check": lambda r: len(r) > 200 and 'accuracy' in r.lower()
    },
    {
        "name": "Data Files Query",
        "query": "What data files are available?",
        "check": lambda r: len(r) > 100 and ('train' in r.lower() or 'test' in r.lower())
    },
    {
        "name": "Code Review Query",
        "query": "Review my code: ```python\nfor i in range(10):\n  print(i)\n```",
        "check": lambda r: len(r) > 150 and 'code' in r.lower()
    }
]

print('='*70)
print('FINAL SYSTEM TEST')
print('='*70)
print()

results = {}

for test in tests:
    print(f'{test["name"]}...')
    
    payload = {
        "query": test["query"],
        "session_id": "final_test",
        "context": {
            "competition_slug": "titanic",
            "competition_name": "Titanic",
            "kaggle_username": "test_user"
        }
    }
    
    try:
        response = requests.post(f'{BASE_URL}/component-orchestrator/query', json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('final_response', '')
            
            passed = test["check"](answer)
            results[test['name']] = passed
            
            status = 'PASS' if passed else 'FAIL'
            print(f'  {status} ({len(answer)} chars)')
        else:
            print(f'  FAIL (HTTP {response.status_code})')
            results[test['name']] = False
            
    except Exception as e:
        print(f'  FAIL ({str(e)[:50]})')
        results[test['name']] = False

print()
print('='*70)
print(f'RESULTS: {sum(results.values())}/{len(results)} passed')
print('='*70)

sys.exit(0 if all(results.values()) else 1)


