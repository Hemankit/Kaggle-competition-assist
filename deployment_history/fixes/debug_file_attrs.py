#!/usr/bin/env python3
"""Debug file object attributes"""
from kaggle import api
api.authenticate()

print('Debugging File Object Attributes')
print('=' * 70)

response = api.competition_list_files('titanic')
print(f'Type of response: {type(response)}')
print()

print('Response attributes:')
for attr in dir(response):
    if not attr.startswith('_'):
        try:
            val = getattr(response, attr)
            if not callable(val):
                print(f'  {attr}: {val} (type: {type(val).__name__})')
        except Exception as e:
            print(f'  {attr}: ERROR - {e}')
print()

# Try to get the files list
files = None
if hasattr(response, 'files'):
    files = response.files
    print(f'Found files attribute: {type(files)}')
elif isinstance(response, list):
    files = response
    print('Response is a list')
else:
    print(f'Cannot find files in response')

if files:
    print(f'Number of files: {len(files)}')
    print()
    first_file = files[0]
    print(f'First file type: {type(first_file)}')
    print(f'First file: {first_file}')
    print()
    
    print('All attributes:')
    for attr in dir(first_file):
        if not attr.startswith('_'):
            try:
                val = getattr(first_file, attr)
                if not callable(val):
                    print(f'  {attr}: {val} (type: {type(val).__name__})')
            except Exception as e:
                print(f'  {attr}: ERROR - {e}')

