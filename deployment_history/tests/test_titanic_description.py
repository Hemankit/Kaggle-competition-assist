#!/usr/bin/env python3
"""Test query that should pull main Titanic description"""
import requests

payload = {
    "query": "Tell me about the Titanic disaster and the challenge in this competition.",
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
    
    print('Response:')
    print(answer)
    print()
    print('='*70)
    print('Key Content Check:')
    checks = {
        "sinking/shipwreck": "sink" in answer.lower() or "shipwreck" in answer.lower(),
        "1912": "1912" in answer,
        "passengers": "passenger" in answer.lower(),
        "survival prediction": ("predict" in answer.lower() or "surviv" in answer.lower()) and "model" in answer.lower(),
        "RMS Titanic": "titanic" in answer.lower() and ("rms" in answer.lower() or "maiden" in answer.lower()),
        "lifeboats": "lifeboat" in answer.lower()
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        status = '✅' if result else '❌'
        print(f'{status} {check}')
    
    print(f'\n📊 Score: {passed}/{total} ({passed/total*100:.0f}%)')
    
    if passed >= 4:
        print('\n🎉 EXCELLENT! Using real Titanic description!')
    elif passed >= 2:
        print('\n✅ GOOD! Has some Titanic details')
    else:
        print('\n⚠️  Still generic')
else:
    print(f'❌ Failed: {response.status_code}')


