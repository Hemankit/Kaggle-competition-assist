#!/usr/bin/env python3
"""COMPREHENSIVE SYSTEM TEST - All Major Features"""
import requests
import time

test_suite = {
    "Core Competition Info": [
        ("Data Files", "What data files are available?"),
        ("Evaluation Metric", "What is the evaluation metric?"),
        ("Overview", "What is this competition about?"),
    ],
    "Getting Started": [
        ("New User Help", "I'm new to Kaggle. How do I start?"),
        ("Submission Format", "How do I submit my predictions?"),
    ],
    "Strategy & Analysis": [
        ("Approaches", "What are good approaches for this competition?"),
        ("Best Techniques", "What techniques work best?"),
    ],
    "Advanced Features": [
        ("Notebooks", "Show me useful notebooks for this competition"),
    ]
}

BASE_URL = 'http://localhost:5000/component-orchestrator/query'

print('='*80)
print('🚀 COMPREHENSIVE SYSTEM TEST - Kaggle Competition Assistant')
print('='*80)
print()

category_results = {}
all_results = []

for category, tests in test_suite.items():
    print(f'\n📁 {category}')
    print('-'*80)
    
    category_passed = 0
    category_total = len(tests)
    
    for test_name, query in tests:
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
            response = requests.post(BASE_URL, json=payload, timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('final_response', '')
                
                # Quality checks
                is_substantial = len(answer) > 200
                is_specific = any(word in answer.lower() for word in ['titanic', 'passenger', 'surviv', 'csv', 'train', 'test'])
                not_error = 'error' not in answer.lower() or len(answer) > 500
                
                passed = is_substantial and is_specific and not_error
                
                if passed:
                    category_passed += 1
                    status = '✅'
                else:
                    status = '❌'
                
                all_results.append((category, test_name, passed))
                
                # Detailed status
                checks = []
                if is_substantial:
                    checks.append(f'{len(answer)} chars')
                else:
                    checks.append(f'⚠️ Only {len(answer)} chars')
                
                if is_specific:
                    checks.append('Titanic-specific')
                else:
                    checks.append('⚠️ Generic')
                
                print(f'  {status} {test_name}: {", ".join(checks)}')
                
            else:
                print(f'  ❌ {test_name}: HTTP {response.status_code}')
                all_results.append((category, test_name, False))
                
        except Exception as e:
            print(f'  ❌ {test_name}: {str(e)[:50]}')
            all_results.append((category, test_name, False))
    
    category_results[category] = (category_passed, category_total)
    print(f'  📊 Category Score: {category_passed}/{category_total}')

# Final Summary
print()
print('='*80)
print('📊 FINAL RESULTS')
print('='*80)

total_passed = 0
total_tests = 0

for category, (passed, total) in category_results.items():
    total_passed += passed
    total_tests += total
    percentage = (passed/total*100) if total > 0 else 0
    status = '✅' if passed == total else '⚠️' if passed >= total*0.7 else '❌'
    print(f'{status} {category}: {passed}/{total} ({percentage:.0f}%)')

print()
print(f'🎯 OVERALL SYSTEM: {total_passed}/{total_tests} ({total_passed/total_tests*100:.0f}%)')
print()

if total_passed == total_tests:
    print('🎉🎉🎉 PERFECT! 100% - SYSTEM READY FOR LINKEDIN!')
    print('All features working flawlessly!')
elif total_passed >= total_tests * 0.85:
    print('✅ EXCELLENT! 85%+ - Almost perfect!')
    print('System is production-ready with minor polish needed.')
elif total_passed >= total_tests * 0.70:
    print('✅ GOOD! 70%+ - Solid performance')
    print('Core features working, some improvements recommended.')
else:
    print('⚠️  Needs more work to reach production quality')

print()
print('='*80)


