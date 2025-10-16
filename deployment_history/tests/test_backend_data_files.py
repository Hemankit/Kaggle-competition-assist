#!/usr/bin/env python3
"""Test backend's get_competition_data_files function"""
import sys
sys.path.insert(0, '.')
from Kaggle_Fetcher.kaggle_api_client import get_competition_data_files

print('Testing Backend get_competition_data_files Function')
print('=' * 70)

result = get_competition_data_files('titanic')

if result:
    print(f'SUCCESS: Found {len(result)} files')
    print()
    for file_info in result:
        name = file_info.get('name', 'Unknown')
        size = file_info.get('size', 0)
        size_mb = size / (1024 * 1024)
        desc = file_info.get('description', 'No description')
        print(f'File: {name}')
        print(f'  Size: {size_mb:.2f} MB ({size} bytes)')
        print(f'  Description: {desc}')
        print()
else:
    print('NO FILES RETURNED')
    print()
    print('Possible reasons:')
    print('1. Kaggle API error')
    print('2. Competition has no data files')  
    print('3. API version mismatch')


