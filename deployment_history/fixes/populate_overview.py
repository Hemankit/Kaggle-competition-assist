#!/usr/bin/env python3
"""Populate Titanic competition overview in ChromaDB"""
import sys
sys.path.insert(0, '.')

from scraper.overview_scraper import OverviewScraper
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
from datetime import datetime

print('Populating Titanic Competition Overview')
print('=' * 70)

# Step 1: Scrape overview
print('\n[1/3] Scraping competition overview...')
scraper = OverviewScraper(competition_name='titanic')
overview_data = scraper.scrape()

if not overview_data or not overview_data.get('overview_sections'):
    print('❌ Failed to scrape overview data!')
    sys.exit(1)

print(f'✅ Scraped {len(overview_data["overview_sections"])} sections')
for section_name in overview_data['overview_sections'].keys():
    print(f'   - {section_name}')

# Step 2: Initialize ChromaDB
print('\n[2/3] Initializing ChromaDB...')
pipeline = ChromaDBRAGPipeline()
print('✅ ChromaDB ready')

# Step 3: Store in ChromaDB
print('\n[3/3] Storing overview sections in ChromaDB...')

stored_count = 0
for section_name, section_data in overview_data['overview_sections'].items():
    # Extract text content (prefer text over markdown)
    section_content = section_data.get('text', '') if isinstance(section_data, dict) else str(section_data)
    
    if section_content and section_content.strip():
        # Create document for this section
        doc = {
            "title": f"Titanic Competition - {section_name}",
            "content": section_content,
            "section": "overview",
            "overview_section": section_name.lower().replace(' ', '_'),
            "competition_slug": "titanic",
            "competition_name": "Titanic - Machine Learning from Disaster",
            "source": "scraper_overview",
            "last_updated": datetime.now().isoformat()
        }
        
        # Store in ChromaDB
        pipeline.index_scraped_data(
            pydantic_results=[],
            structured_results=[doc]
        )
        
        stored_count += 1
        print(f'  ✅ Stored: {section_name} ({len(section_content)} chars)')

print(f'\n✅ Successfully stored {stored_count} overview sections!')
print('\nNow test with queries like:')
print('  - "What is this competition about?"')
print('  - "What makes this competition unique?"')  
print('  - "What is the goal of this competition?"')

