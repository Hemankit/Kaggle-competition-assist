#!/usr/bin/env python3
"""Test overview query through the backend"""
import requests
import json

queries = [
    "What is this competition about?",
    "What makes this competition unique?",
    "What is the goal of this competition?"
]

print('Testing Overview Queries')
print('=' * 70)

for query in queries:
    print(f'\n📝 Query: "{query}"')
    print('-' * 70)
    
    payload = {
        "query": query,
        "session_id": "test_session",
        "context": {
            "competition_slug": "titanic",
            "competition_name": "Titanic - Machine Learning from Disaster",
            "kaggle_username": "test_user"
        }
    }
    
    try:
        response = requests.post('http://localhost:5000/component-orchestrator/query', 
                                json=payload, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('final_response', '')
            
            # Check if response is generic or specific
            if 'Titanic' in answer or 'shipwreck' in answer or 'passengers' in answer or 'survived' in answer:
                print('✅ Titanic-specific response!')
            else:
                print('⚠️  Generic response')
            
            # Show first 300 chars
            print(f'\nResponse preview: {answer[:300]}...')
        else:
            print(f'❌ Failed: {response.status_code}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
    
    print()

print('=' * 70)
print('✅ Overview query testing complete!')


