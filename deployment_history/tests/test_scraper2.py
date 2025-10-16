#!/usr/bin/env python3
"""
Test scraper with correct keys
"""
from scraper.overview_scraper import OverviewScraper
import json

print('Testing OverviewScraper on Titanic')
print('=' * 70)

try:
    scraper = OverviewScraper('titanic', headless=True)
    result = scraper.scrape()
    
    print('✓ Scraping completed!')
    print()
    print('Result keys:', list(result.keys()))
    print()
    
    # Check overview_sections
    if 'overview_sections' in result:
        sections = result['overview_sections']
        print(f'Found {len(sections)} sections:')
        
        for section_name, section_data in sections.items():
            text = section_data.get('text', '')
            print(f'\n  📄 Section: {section_name}')
            print(f'     Length: {len(text)} chars')
            
            # Show preview for all sections
            preview = text[:150].replace('\n', ' ')
            print(f'     Preview: {preview}...')
            
            # Check specifically for evaluation
            if 'eval' in section_name.lower():
                print(f'\n  ✅ EVALUATION SECTION!')
                print(f'     Full text:')
                print(f'     {text}')
                print()
                
                # Extract metric
                text_lower = text.lower()
                if 'accuracy' in text_lower:
                    print('     ➡️ Metric: ACCURACY')
                elif 'auc' in text_lower or 'area under' in text_lower:
                    print('     ➡️ Metric: AUC/ROC')
                elif 'rmse' in text_lower:
                    print('     ➡️ Metric: RMSE')
                elif 'f1' in text_lower:
                    print('     ➡️ Metric: F1 Score')
                else:
                    print('     ➡️ Metric: Check text above')
    else:
        print('⚠ No overview_sections key')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()


