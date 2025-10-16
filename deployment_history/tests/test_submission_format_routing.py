#!/usr/bin/env python3
"""Test that submission format queries route to evaluation/overview section"""
import requests

BASE_URL = 'http://localhost:5000'

queries = [
    "What format should my submission file be in?",
    "How do I submit my predictions?",
    "What is the submission file format?"
]

print('='*70)
print('🧪 TESTING SUBMISSION FORMAT ROUTING')
print('='*70)
print()

for query in queries:
    print(f'Query: "{query}"')
    
    payload = {
        "query": query,
        "session_id": "test_routing",
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
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('final_response', '')
            
            # Check for correct section
            is_evaluation = '📊 **Evaluation Metric' in answer or 'Submission File Format' in answer or 'PassengerId,Survived' in answer
            is_data_section = '📊 **Data Section:' in answer and 'train.csv' in answer[:500]
            
            if is_evaluation:
                print('  ✅ Correctly routed to EVALUATION/OVERVIEW section')
                print(f'     Contains submission format details: {len(answer)} chars')
            elif is_data_section:
                print('  ❌ INCORRECTLY routed to DATA section (bug!)')
            else:
                print('  ⚠️  Unknown section')
            
            # Show snippet
            snippet = answer[:200].replace('\n', ' ')
            print(f'     Preview: {snippet}...')
        else:
            print(f'  ❌ HTTP {response.status_code}')
            
    except Exception as e:
        print(f'  ❌ Error: {str(e)[:100]}')
    
    print()

print('='*70)
print('✅ Routing test complete!')
print('='*70)


