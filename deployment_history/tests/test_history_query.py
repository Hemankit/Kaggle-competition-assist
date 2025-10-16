#!/usr/bin/env python3
"""Test historical details query"""
import requests

payload = {
    "query": "What happened to the Titanic in 1912? Tell me about the historical disaster.",
    "session_id": "test_session",
    "context": {
        "competition_slug": "titanic",
        "competition_name": "Titanic - Machine Learning from Disaster",
        "kaggle_username": "test_user"
    }
}

response = requests.post('http://localhost:5000/component-orchestrator/query', 
                        json=payload, timeout=90)

if response.status_code == 200:
    data = response.json()
    answer = data.get('final_response', '')
    
    print(answer)
    print()
    print('='*70)
    
    # Check for historical details
    checks = {
        "1912": "1912" in answer,
        "April 15": "april" in answer.lower() and "15" in answer,
        "RMS/maiden voyage": "rms" in answer.lower() or "maiden" in answer.lower(),
        "iceberg": "iceberg" in answer.lower(),
        "lifeboats": "lifeboat" in answer.lower(),
        "1502 deaths": "1502" in answer or "1,502" in answer,
        "unsinkable": "unsinkable" in answer.lower()
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        status = '✅' if result else '❌'
        print(f'{status} {check}')
    
    print(f'\n📊 Historical Details: {passed}/{total}')
    
    if passed >= 4:
        print('🎉 EXCELLENT historical detail!')
    elif passed >= 2:
        print('✅ Good historical context')
    else:
        print('⚠️  Missing historical details')
else:
    print(f'❌ Failed: {response.status_code}')


