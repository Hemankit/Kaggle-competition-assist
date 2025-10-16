#!/usr/bin/env python3
"""Test data files query through the backend"""
import requests

print('Testing Data Files Query')
print('=' * 70)

# Test the data files endpoint
payload = {
    "query": "What data files are available for this competition?",
    "session_id": "test_session",
    "context": {
        "competition_slug": "titanic",
        "competition_name": "Titanic - Machine Learning from Disaster",
        "kaggle_username": "test_user"
    }
}

response = requests.post('http://localhost:5000/component-orchestrator/query', json=payload, timeout=60)

if response.status_code == 200:
    data = response.json()
    
    print('✅ SUCCESS!')
    print()
    print('Full Response JSON:')
    import json
    print(json.dumps(data, indent=2))
    print()
    
    answer = data.get('answer', data.get('response', ''))
    print('Extracted Answer:')
    print(answer)
    print()
    
    # Check if it mentions the actual files
    if 'train.csv' in str(data) or 'test.csv' in str(data):
        print('✅ Response mentions actual data files!')
    else:
        print('⚠️ Response doesn\'t mention specific files')
        
else:
    print(f'❌ FAILED: {response.status_code}')
    print(response.text)

