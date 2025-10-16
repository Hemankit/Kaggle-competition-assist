#!/usr/bin/env python3
from scraper.overview_scraper import OverviewScraper

s = OverviewScraper(competition_name='titanic')
r = s.scrape()

print('Type:', type(r))
print('Keys:', list(r.keys()) if r and isinstance(r, dict) else 'Not a dict or None')
print('Has sections:', 'sections' in r if r and isinstance(r, dict) else False)

if r and isinstance(r, dict):
    print('\nTop-level keys:')
    for key in r.keys():
        val = r[key]
        if isinstance(val, dict):
            print(f'  {key}: dict with {len(val)} items')
        elif isinstance(val, str):
            print(f'  {key}: string ({len(val)} chars)')
        else:
            print(f'  {key}: {type(val)}')


