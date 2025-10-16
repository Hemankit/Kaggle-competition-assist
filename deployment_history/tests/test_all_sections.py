#!/usr/bin/env python3
"""
Comprehensive Test: All Backend Sections
Tests: Overview, Evaluation, Data, Notebooks, Discussions, Code Review, etc.
"""
import requests
import json

BACKEND_URL = 'http://localhost:5000'
COMPETITION_SLUG = 'titanic'
COMPETITION_NAME = 'Titanic - Machine Learning from Disaster'
USERNAME = 'hemankit'

print('=' * 80)
print('COMPREHENSIVE BACKEND SECTION TEST')
print('=' * 80)
print()

# Test queries for each major section
test_queries = [
    {
        'name': '1. EVALUATION METRIC',
        'query': 'What is the evaluation metric for this competition?',
        'expected_keywords': ['accuracy', 'metric', 'score'],
        'avoid_keywords': ['not specified', 'check the page']
    },
    {
        'name': '2. DATA FILES',
        'query': 'What data files are available?',
        'expected_keywords': ['data', 'csv', 'file'],
        'avoid_keywords': ['no data found', 'mock']
    },
    {
        'name': '3. COMPETITION OVERVIEW',
        'query': 'Tell me about this competition',
        'expected_keywords': ['titanic', 'predict', 'survival'],
        'avoid_keywords': []
    },
    {
        'name': '4. NOTEBOOKS',
        'query': 'Show me top notebooks',
        'expected_keywords': ['notebook', 'kernel'],
        'avoid_keywords': []
    },
    {
        'name': '5. SUBMISSION FORMAT',
        'query': 'What is the submission file format?',
        'expected_keywords': ['csv', 'submit', 'file', 'format'],
        'avoid_keywords': []
    },
    {
        'name': '6. GETTING STARTED',
        'query': 'How do I get started with this competition?',
        'expected_keywords': ['start', 'data', 'download'],
        'avoid_keywords': []
    }
]

results = []

for test in test_queries:
    print(f"\n{'='*80}")
    print(f"{test['name']}")
    print(f"{'='*80}")
    print(f"Query: {test['query']}")
    print()
    
    try:
        response = requests.post(
            f'{BACKEND_URL}/component-orchestrator/query',
            json={
                'query': test['query'],
                'context': {
                    'competition_slug': COMPETITION_SLUG,
                    'competition_name': COMPETITION_NAME,
                    'kaggle_username': USERNAME
                }
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f'FAIL: HTTP {response.status_code}')
            results.append({
                'test': test['name'],
                'status': 'FAIL',
                'reason': f'HTTP {response.status_code}'
            })
            continue
        
        result = response.json()
        final_response = result.get('final_response', '').lower()
        
        # Check for expected keywords
        found_expected = [kw for kw in test['expected_keywords'] if kw in final_response]
        found_avoid = [kw for kw in test['avoid_keywords'] if kw in final_response]
        
        # Determine pass/fail
        has_expected = len(found_expected) > 0
        has_avoid = len(found_avoid) > 0
        is_placeholder = 'not specified' in final_response or 'check the page' in final_response or 'mock' in final_response
        
        status = 'PASS' if (has_expected and not has_avoid and not is_placeholder) else 'WARN' if has_expected else 'FAIL'
        
        print(f'Status: {status}')
        print(f'System: {result.get("system")}')
        print(f'Agents: {result.get("agents_used")}')
        print(f'Response length: {len(result.get("final_response", ""))} chars')
        print()
        
        if found_expected:
            print(f'FOUND expected keywords: {found_expected}')
        else:
            print(f'MISSING expected keywords: {test["expected_keywords"]}')
        
        if found_avoid:
            print(f'WARNING: Found placeholder keywords: {found_avoid}')
        
        if is_placeholder:
            print('WARNING: Response appears to be a placeholder/generic')
        
        # Show preview
        print()
        print('Response Preview (first 300 chars):')
        print('-' * 80)
        preview = result.get('final_response', '')[:300]
        print(preview)
        if len(result.get('final_response', '')) > 300:
            print('...')
        
        results.append({
            'test': test['name'],
            'status': status,
            'has_expected': has_expected,
            'has_avoid': has_avoid,
            'is_placeholder': is_placeholder,
            'response_length': len(result.get('final_response', ''))
        })
        
    except Exception as e:
        print(f'ERROR: {e}')
        results.append({
            'test': test['name'],
            'status': 'ERROR',
            'reason': str(e)
        })

# Summary
print()
print('=' * 80)
print('TEST SUMMARY')
print('=' * 80)

passed = sum(1 for r in results if r['status'] == 'PASS')
warned = sum(1 for r in results if r['status'] == 'WARN')
failed = sum(1 for r in results if r['status'] in ['FAIL', 'ERROR'])

print(f'Total Tests: {len(results)}')
print(f'PASSED: {passed}')
print(f'WARNED: {warned}')
print(f'FAILED: {failed}')
print()

for r in results:
    symbol = 'âœ…' if r['status'] == 'PASS' else 'âš ï¸' if r['status'] == 'WARN' else 'â�Œ'
    print(f"{symbol} {r['test']}: {r['status']}")
    if r.get('is_placeholder'):
        print(f"   â†' Contains placeholder/generic content")

print()
if failed == 0 and warned == 0:
    print('ðŸŽ‰ SUCCESS: All sections working perfectly!')
elif failed == 0:
    print('âœ… MOSTLY WORKING: Some sections need improvement')
else:
    print('âš ï¸ ISSUES FOUND: Some sections not working as expected')


