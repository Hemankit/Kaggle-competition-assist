#!/usr/bin/env python3
"""Fix kaggle_api_client.py attribute names"""
import shutil

file_path = 'Kaggle_Fetcher/kaggle_api_client.py'

# Backup first
shutil.copy(file_path, file_path + '.backup')
print(f'Created backup: {file_path}.backup')

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

# Fix the attribute names
content = content.replace("getattr(f, 'totalBytes', 0)", "getattr(f, 'total_bytes', 0)")
content = content.replace("getattr(f, 'creationDate', '')", "getattr(f, 'creation_date', '')")

# Write back
with open(file_path, 'w') as f:
    f.write(content)

print('✅ Fixed attribute names:')
print('   - totalBytes → total_bytes')
print('   - creationDate → creation_date')


