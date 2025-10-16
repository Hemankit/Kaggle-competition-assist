#!/usr/bin/env python3
data = open('Kaggle_Fetcher/kaggle_api_client.py', 'rb').read()
null_count = data.count(b'\x00')
print(f'File size: {len(data)} bytes')
print(f'Null bytes: {null_count}')
if null_count > 0:
    print('File is CORRUPTED (contains null bytes)')
else:
    print('File is CLEAN')

