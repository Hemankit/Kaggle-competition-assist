#!/usr/bin/env python3
"""Test universal features that apply to ANY competition"""
import requests
import json

# Test queries that should work for any competition
test_queries = [
    {
        "name": "Strategy/Approaches",
        "query": "What are good approaches for this competition?",
        "check_keywords": ["model", "approach", "strategy", "feature", "algorithm"],
        "min_keywords": 3
    },
    {
        "name": "Getting Started",
        "query": "I'm new to this competition. How do I get started?",
        "check_keywords": ["data", "start", "first", "baseline", "explore"],
        "min_keywords": 2
    },
    {
        "name": "Submission Format",
        "query": "What's the submission format?",
        "check_keywords": ["csv", "submit", "format", "column", "file"],
        "min_keywords": 2
    },
    {
        "name": "Best Approaches",
        "query": "What techniques work best for this competition?",
        "check_keywords": ["technique", "model", "approach", "feature", "work"],
        "min_keywords": 2
    }
]

BASE_URL = 'http://localhost:5000/component-orchestrator/query'

print('='*70)
print('TESTING UNIVERSAL COMPETITION FEATURES')
print('='*70)
print()

results = {}

for test in test_queries:
    print(f'📝 Testing: {test["name"]}')
    print(f'   Query: "{test["query"]}"')
    
    payload = {
        "query": test["query"],
        "session_id": "test_session",
        "context": {
            "competition_slug": "titanic",
            "competition_name": "Titanic - Machine Learning from Disaster",
            "kaggle_username": "test_user"
        }
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('final_response', '')
            
            # Check for keywords
            answer_lower = answer.lower()
            found_keywords = [kw for kw in test['check_keywords'] if kw in answer_lower]
            
            # Check if response is competition-specific (not generic)
            is_specific = "titanic" in answer_lower or "passenger" in answer_lower or "survived" in answer_lower
            
            # Check length
            is_substantial = len(answer) > 300
            
            # Determine status
            passed = len(found_keywords) >= test['min_keywords'] and is_substantial
            
            status = '✅' if passed else '❌'
            results[test['name']] = passed
            
            print(f'   {status} Keywords: {len(found_keywords)}/{len(test["check_keywords"])} ({", ".join(found_keywords[:3])}...)')
            print(f'   {"✅" if is_specific else "⚠️ "} Competition-specific: {is_specific}')
            print(f'   {"✅" if is_substantial else "❌"} Length: {len(answer)} chars')
            
            # Show snippet
            snippet = answer[:200].replace('\n', ' ')
            print(f'   Preview: {snippet}...')
            
        else:
            print(f'   ❌ HTTP Error: {response.status_code}')
            results[test['name']] = False
            
    except Exception as e:
        print(f'   ❌ Error: {e}')
        results[test['name']] = False
    
    print()

# Summary
print('='*70)
print('SUMMARY')
print('='*70)

passed = sum(results.values())
total = len(results)

for name, result in results.items():
    status = '✅' if result else '❌'
    print(f'{status} {name}')

print()
print(f'📊 Overall: {passed}/{total} ({passed/total*100:.0f}%)')

if passed == total:
    print('🎉 PERFECT! All universal features working!')
elif passed >= total * 0.75:
    print('✅ GOOD! Most features working, minor fixes needed')
elif passed >= total * 0.5:
    print('⚠️  FAIR - Need some improvements')
else:
    print('❌ NEEDS WORK - Significant issues to fix')


