"""Quick test of data scraper without emoji issues"""
from scraper.data_scraper import DataSectionScraper
import json

scraper = DataSectionScraper("titanic")
result = scraper.scrape_data_description()

print("="*70)
print("DATA SCRAPER TEST RESULTS")
print("="*70)

print(f"\nCompetition: {result['competition']}")
print(f"Scraped: {result['scraped']}")

print("\n" + "="*70)
print("MAIN DESCRIPTION")
print("="*70)
print(result['description'][:800])

print("\n" + "="*70)
print(f"SECTIONS ({len(result['sections'])})")
print("="*70)
for title, content in result['sections'].items():
    print(f"\n--- {title} ---")
    print(content[:400])
    if len(content) > 400:
        print("...")

print("\n" + "="*70)
print(f"COLUMN INFO ({len(result['column_info'])})")
print("="*70)
for col in result['column_info'][:15]:
    print(f"- {col['column']}: {col['description'][:100]}")

print("\n" + "="*70)
print("DONE")
print("="*70)

