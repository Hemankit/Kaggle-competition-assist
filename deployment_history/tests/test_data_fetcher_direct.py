#!/usr/bin/env python3
"""Test DataFetcher directly"""
from Kaggle_Fetcher.data_fetcher import DataFetcher

print('Testing DataFetcher directly')
print('=' * 70)

fetcher = DataFetcher()
files = fetcher.fetch_data_files('titanic')

print(f'Files found: {len(files)}')
for file in files:
    print(f'  - {file["name"]}: {file["size"]} bytes')


