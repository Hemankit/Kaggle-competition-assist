#!/usr/bin/env python3
"""Test code analysis and feedback features"""
import requests

# Sample code snippets to test
code_tests = [
    {
        "name": "Basic Code Review",
        "query": """Review my code:
```python
import pandas as pd
df = pd.read_csv('train.csv')
X = df.drop('Survived', axis=1)
y = df['Survived']
```""",
        "expected_keywords": ["import", "read", "drop", "code", "review", "suggest"]
    },
    {
        "name": "Error Diagnosis",
        "query": """I'm getting this error:
ValueError: could not convert string to float: 'male'
My code:
```python
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(X, y)
```""",
        "expected_keywords": ["error", "valueerror", "string", "categorical", "encode", "convert"]
    },
    {
        "name": "Code Improvement",
        "query": """How can I improve this code?
```python
for i in range(len(df)):
    if df.iloc[i]['Sex'] == 'male':
        df.iloc[i]['Sex_encoded'] = 1
    else:
        df.iloc[i]['Sex_encoded'] = 0
```""",
        "expected_keywords": ["improve", "vectorize", "apply", "map", "faster", "efficient"]
    }
]

BASE_URL = 'http://localhost:5000/component-orchestrator/query'

print('='*70)
print('🔧 TESTING CODE ANALYSIS FEATURES')
print('='*70)
print()

results = {}

for test in code_tests:
    print(f'📝 {test["name"]}')
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
            answer = data.get('final_response', '').lower()
            
            # Check for expected keywords
            found_keywords = [kw for kw in test['expected_keywords'] if kw in answer]
            keyword_score = len(found_keywords) / len(test['expected_keywords'])
            
            # Check if response is substantial
            is_substantial = len(answer) > 200
            
            # Check if code-specific (not generic)
            has_code_context = any(word in answer for word in ['code', 'function', 'variable', 'syntax', 'error'])
            
            passed = keyword_score >= 0.4 and is_substantial and has_code_context
            
            status = '✅' if passed else '❌'
            results[test['name']] = passed
            
            print(f'{status} Status: {"PASS" if passed else "FAIL"}')
            print(f'   Keywords: {len(found_keywords)}/{len(test["expected_keywords"])} ({", ".join(found_keywords[:3])}...)')
            print(f'   Length: {len(answer)} chars')
            print(f'   Code-specific: {has_code_context}')
            
            # Show snippet
            snippet = data.get('final_response', '')[:250].replace('\n', ' ')
            print(f'   Preview: {snippet}...')
            
        else:
            print(f'❌ HTTP Error: {response.status_code}')
            results[test['name']] = False
            
    except Exception as e:
        print(f'❌ Error: {str(e)[:100]}')
        results[test['name']] = False
    
    print()

# Summary
print('='*70)
print('📊 CODE FEATURES SUMMARY')
print('='*70)

passed = sum(results.values())
total = len(results)

for name, result in results.items():
    status = '✅' if result else '❌'
    print(f'{status} {name}')

print()
print(f'🎯 Overall: {passed}/{total} ({passed/total*100:.0f}%)')

if passed >= total * 0.8:
    print('🎉 EXCELLENT! Code features working great!')
elif passed >= total * 0.6:
    print('✅ GOOD! Most code features working')
else:
    print('⚠️  Code features need attention')


