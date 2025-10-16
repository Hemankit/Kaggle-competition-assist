#!/usr/bin/env python3
"""Detailed test of overview response content"""
import requests

payload = {
    "query": "What is this competition about? Explain in detail.",
    "session_id": "test_session",
    "context": {
        "competition_slug": "titanic",
        "competition_name": "Titanic - Machine Learning from Disaster",
        "kaggle_username": "test_user"
    }
}

print('Testing Detailed Overview Query')
print('=' * 70)

response = requests.post('http://localhost:5000/component-orchestrator/query', 
                        json=payload, timeout=90)

if response.status_code == 200:
    data = response.json()
    answer = data.get('final_response', '')
    
    print('Full Response:')
    print(answer)
    print()
    print('=' * 70)
    
    # Check for key phrases from scraped overview
    checks = {
        "Mentions sinking": "sinking" in answer.lower() or "shipwreck" in answer.lower(),
        "Mentions 1912": "1912" in answer,
        "Mentions passengers": "passenger" in answer.lower(),
        "Mentions survival prediction": "predict" in answer.lower() and "surviv" in answer.lower(),
        "Mentions train/test data": "train.csv" in answer or "test.csv" in answer,
        "Specific details": len(answer) > 500  # Should have substantial content
    }
    
    print('\n✅ Content Check:')
    for check, passed in checks.items():
        status = '✅' if passed else '❌'
        print(f'{status} {check}: {passed}')
        
else:
    print(f'❌ Failed: {response.status_code}')


