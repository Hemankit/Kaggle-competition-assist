#!/usr/bin/env python3
"""
Test if OverviewScraper can get evaluation data from Titanic
"""
from scraper.overview_scraper import OverviewScraper

print('Testing OverviewScraper on Titanic')
print('=' * 70)

try:
    scraper = OverviewScraper('titanic', headless=True)
    result = scraper.scrape()
    
    print('✓ Scraping completed!')
    print()
    
    if 'sections' in result:
        print(f'Found {len(result["sections"])} sections:')
        for section_name, section_data in result['sections'].items():
            text = section_data.get('text', '')
            print(f'\n  Section: {section_name}')
            print(f'    Text length: {len(text)} chars')
            
            # Check specifically for evaluation
            if 'eval' in section_name.lower():
                print(f'\n  ✅ EVALUATION SECTION FOUND!')
                print(f'    Full text:\n{text}')
                
                # Try to extract the metric
                if 'accuracy' in text.lower():
                    print('\\n    Metric appears to be: ACCURACY')
                elif 'auc' in text.lower() or 'roc' in text.lower():
                    print('\\n    Metric appears to be: AUC/ROC')
                elif 'rmse' in text.lower():
                    print('\\n    Metric appears to be: RMSE')
    else:
        print('⚠ No sections found')
        print('Result keys:', list(result.keys()))
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()


