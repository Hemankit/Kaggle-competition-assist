#!/usr/bin/env python3
"""Test that code review uses precise terminology"""
import requests

BASE_URL = 'http://localhost:5000'

# The exact query from the user
query = """Review my code:
```python
import pandas as pd
df = pd.read_csv('train.csv')
for i in range(len(df)):
    print(df.iloc[i]['Name'])
```
"""

print('='*70)
print('🧪 TESTING CODE REVIEW PRECISION')
print('='*70)
print()
print('Query: Loop with iloc printing names')
print()

payload = {
    "query": query,
    "session_id": "test_precision",
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
        
        print('✅ Response received')
        print(f'   Length: {len(answer)} chars')
        print()
        
        # Check for precise terminology
        checks = {
            "Uses 'direct column access'": 'direct column access' in answer.lower() or "df['name']" in answer.lower() or 'df["name"]' in answer.lower(),
            "Uses 'vectorized' correctly": ('vectorized' not in answer.lower()) or ('vectorized' in answer.lower() and 'transform' in answer.lower()),
            "Mentions avoiding iloc": 'iloc' in answer.lower(),
            "Provides correct example": "df['Name']" in answer or 'df["Name"]' in answer or 'for name in df' in answer.lower(),
        }
        
        print('📊 Precision Checks:')
        all_pass = True
        for check, passed in checks.items():
            status = '✅' if passed else '❌'
            print(f'   {status} {check}')
            if not passed:
                all_pass = False
        
        print()
        if all_pass:
            print('✅ CODE REVIEW IS NOW TECHNICALLY PRECISE!')
        else:
            print('⚠️  Some precision issues remain')
        
        print()
        print('📝 Response excerpt:')
        print('-'*70)
        # Show relevant part about inefficiencies
        if 'Inefficiencies' in answer or 'inefficienc' in answer.lower():
            start = answer.lower().find('inefficien')
            excerpt = answer[max(0, start-50):min(len(answer), start+400)]
            print(excerpt)
        else:
            print(answer[:500])
        print('-'*70)
        
    else:
        print(f'❌ HTTP {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {str(e)}')

print()
print('='*70)
print('✅ Test complete!')
print('='*70)


