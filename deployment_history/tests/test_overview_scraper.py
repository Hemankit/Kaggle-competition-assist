#!/usr/bin/env python3
"""Test overview scraper with detailed error output"""
import sys
sys.path.insert(0, '.')

from scraper.overview_scraper import OverviewScraper
import traceback

print('Testing OverviewScraper')
print('=' * 70)

try:
    scraper = OverviewScraper(competition_name='titanic')
    print('✅ Scraper initialized')
    
    print('\nAttempting to scrape...')
    result = scraper.scrape()
    
    if result and result.get('sections'):
        print(f'\n✅ SUCCESS! Scraped {len(result["sections"])} sections:')
        for name in result['sections'].keys():
            print(f'  - {name}')
    else:
        print(f'\n❌ No sections scraped. Result: {result}')
        
except Exception as e:
    print(f'\n❌ ERROR: {e}')
    print('\nFull traceback:')
    traceback.print_exc()


