#!/usr/bin/env python3
"""Test multi-agent queries that require competition participation"""
import requests

# Queries that would normally require actual competition participation
multiagent_tests = [
    {
        "name": "Progress Check",
        "query": "Am I stagnating? How am I doing in this competition?",
        "should_handle": "Should explain no submission data or provide general guidance"
    },
    {
        "name": "Idea Generation",
        "query": "Give me ideas for this competition. What should I try?",
        "should_handle": "Should suggest approaches based on competition type"
    },
    {
        "name": "Next Steps",
        "query": "I'm stuck. What should I try next?",
        "should_handle": "Should provide strategy recommendations"
    }
]

BASE_URL = 'http://localhost:5000/component-orchestrator/query'

print('='*70)
print('🤖 TESTING MULTI-AGENT QUERIES (Without Submission Data)')
print('='*70)
print()

results = {}

for test in multiagent_tests:
    print(f'📝 {test["name"]}')
    print(f'   Query: "{test["query"]}"')
    print(f'   Expected: {test["should_handle"]}')
    print('-'*70)
    
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
        response = requests.post(BASE_URL, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('final_response', '')
            
            # Check if response handles missing data gracefully
            has_error_msg = 'error' in answer.lower() or 'not available' in answer.lower() or 'issue' in answer.lower()
            is_helpful = len(answer) > 200 and any(word in answer.lower() for word in ['competition', 'approach', 'strategy', 'try', 'recommend'])
            
            # Determine if acceptable
            acceptable = has_error_msg or is_helpful
            
            status = '✅' if acceptable else '❌'
            results[test['name']] = acceptable
            
            print(f'{status} Status: {"Graceful" if has_error_msg else "Helpful" if is_helpful else "PROBLEMATIC"}')
            print(f'   Length: {len(answer)} chars')
            
            # Show snippet
            snippet = answer[:300].replace('\n', ' ')
            print(f'   Response: {snippet}...')
            
        else:
            print(f'❌ HTTP Error: {response.status_code}')
            results[test['name']] = False
            
    except Exception as e:
        print(f'❌ Error: {str(e)[:100]}')
        results[test['name']] = False
    
    print()

# Summary
print('='*70)
print('📊 MULTI-AGENT QUERY HANDLING')
print('='*70)

passed = sum(results.values())
total = len(results)

for name, result in results.items():
    status = '✅' if result else '❌'
    print(f'{status} {name}')

print()
print(f'🎯 Overall: {passed}/{total} ({passed/total*100:.0f}%)')

if passed == total:
    print('✅ All queries handled gracefully!')
elif passed >= 2:
    print('✅ Most queries handled acceptably')
else:
    print('⚠️  CONCERN: Some queries may give poor responses without submission data')
    print('   RECOMMENDATION: Disable or add warning message for these query types')


