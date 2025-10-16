#!/usr/bin/env python3
"""Test Kaggle API data files fetching"""
print('Testing Kaggle API - Data Files for Titanic')
print('=' * 70)

from kaggle import api
api.authenticate()

# Test 1: List data files
print('[1] Data Files List:')
try:
    files_list = api.competition_list_files('titanic')
    print(f'Found {len(files_list)} files:')
    for f in files_list:
        desc = f.description if hasattr(f, 'description') else 'N/A'
        print(f'  - Name: {f.name}')
        print(f'    Size: {f.size} bytes')
        print(f'    Description: {desc}')
        print()
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()

print()

# Test 2: Check file attributes
print('[2] File Object Attributes:')
if files_list:
    sample_file = files_list[0]
    print('Available attributes on first file:')
    for attr in dir(sample_file):
        if not attr.startswith('_'):
            try:
                val = getattr(sample_file, attr)
                if not callable(val):
                    print(f'  {attr}: {val}')
            except:
                pass

print()
print('=' * 70)
print('Summary:')
print(f'Total files: {len(files_list) if files_list else 0}')
if files_list:
    total_size = sum(f.size for f in files_list)
    print(f'Total size: {total_size / (1024*1024):.2f} MB')


