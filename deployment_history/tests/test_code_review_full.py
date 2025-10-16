#!/usr/bin/env python3
"""Get full code review response to analyze"""
import requests

BASE_URL = 'http://localhost:5000'

query = """Review my code:
```python
import pandas as pd
df = pd.read_csv('train.csv')
for i in range(len(df)):
    print(df.iloc[i]['Name'])
```
"""

payload = {
    "query": query,
    "session_id": "test_full",
    "context": {
        "competition_slug": "titanic",
        "competition_name": "Titanic",
        "kaggle_username": "Hemankit"
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
        
        print('='*70)
        print('FULL CODE REVIEW RESPONSE:')
        print('='*70)
        print()
        print(answer)
        print()
        print('='*70)
        
except Exception as e:
    print(f'Error: {e}')


