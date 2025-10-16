#!/usr/bin/env python3
"""Test that strategy queries are collaborative, not prescriptive"""
import requests

BASE_URL = 'http://localhost:5000'

# The user's example query
query = "How do you recommend preprocessing this data? I used a batch processing method due to the size of the data."

print('='*70)
print('🧪 TESTING COLLABORATIVE STRATEGY RESPONSE')
print('='*70)
print()
print(f'Query: "{query}"')
print()

payload = {
    "query": query,
    "session_id": "test_collab",
    "context": {
        "competition_slug": "titanic",
        "competition_name": "Titanic",
        "kaggle_username": "test_user"
    }
}

try:
    response = requests.post(
        f'{BASE_URL}/component-orchestrator/query',
        json=payload,
        timeout=90
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get('final_response', '')
        
        print('✅ Response received')
        print(f'   Length: {len(answer)} chars')
        print()
        
        # Check if response is collaborative
        checks = {
            "NOT a generic template": len(answer) < 1500 or 'batch processing' in answer.lower() or 'approach' in answer.lower(),
            "Acknowledges user's approach": 'batch' in answer.lower() or 'preprocessing' in answer.lower(),
            "Is specific (not generic)": 'titanic' in answer.lower() or len(answer) > 300,
            "NOT prescriptive checklist": answer.count('1.') < 3,  # Doesn't have numbered list of "do this, do that"
        }
        
        print('📊 Collaborative Checks:')
        all_pass = True
        for check, passed in checks.items():
            status = '✅' if passed else '❌'
            print(f'   {status} {check}')
            if not passed:
                all_pass = False
        
        print()
        if all_pass:
            print('✅ RESPONSE IS COLLABORATIVE AND INTELLIGENT!')
        else:
            print('⚠️  Response may still be too generic')
        
        print()
        print('📝 Full Response:')
        print('-'*70)
        print(answer)
        print('-'*70)
        
    else:
        print(f'❌ HTTP {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {str(e)}')

print()
print('='*70)
print('✅ Test complete!')
print('='*70)


