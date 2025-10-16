#!/usr/bin/env python3
"""
Populate ChromaDB with Evaluation Data from Titanic
"""
print('Populating ChromaDB with Titanic Evaluation Data')
print('=' * 70)

import sys
import os
sys.path.insert(0, os.getcwd())

# Scrape evaluation data
from scraper.overview_scraper import OverviewScraper

print('[1/3] Scraping Titanic competition page...')
scraper = OverviewScraper('titanic', headless=True)
result = scraper.scrape()

eval_text = ''
if 'overview_sections' in result:
    sections = result['overview_sections']
    
    # Find evaluation section
    for section_name, section_data in sections.items():
        if 'eval' in section_name.lower():
            eval_text = section_data.get('text', '')
            print(f'✓ Found evaluation section: {len(eval_text)} chars')
            break

if not eval_text:
    print('❌ No evaluation section found!')
    exit(1)

print()
print('[2/3] Preparing evaluation documents...')

# Initialize ChromaDB pipeline
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
rag_pipeline = ChromaDBRAGPipeline(collection_name='kaggle_competition_data')

# Create evaluation documents
api_results = [
    {
        'content': f"""Titanic Competition - Evaluation Metric

Goal: Predict if a passenger survived the sinking of the Titanic or not.

Evaluation Metric: ACCURACY

Your score is the percentage of passengers you correctly predict. This is known as accuracy.

Submission Format:
- CSV file with exactly 418 entries plus a header row
- 2 columns: PassengerId and Survived
- Survived: 1 for survived, 0 for deceased

Full Details:
{eval_text}
""",
        'meta': {
            'competition_slug': 'titanic',
            'section': 'evaluation',
            'title': 'Titanic - Evaluation Metric',
            'metric': 'accuracy',
            'source': 'scraper_overview'
        }
    },
    {
        'content': """The Titanic competition uses ACCURACY as the evaluation metric. 

Accuracy is the percentage of passengers you correctly predict (survived or not survived).

For each passenger in the test set, you must predict a 0 or 1 value:
- 0 = Did not survive
- 1 = Survived

Your score will be calculated as: (Number of correct predictions) / (Total predictions) * 100%
""",
        'meta': {
            'competition_slug': 'titanic',
            'section': 'evaluation_metric_detailed',
            'title': 'Titanic - Accuracy Metric Explained',
            'metric': 'accuracy',
            'source': 'evaluation_enriched'
        }
    }
]

print(f'✓ Created {len(api_results)} evaluation documents')
print()

print('[3/3] Indexing into ChromaDB...')
result = rag_pipeline.index_api_data(api_results)
print('✓', result)

print()
print('=' * 70)
print('✅ SUCCESS: Evaluation data populated!')
print()
print('Testing retrieval...')
retrieved = rag_pipeline.rerank_document_store(
    'What is the evaluation metric for Titanic?', 
    top_k_retrieval=5, 
    top_k_final=2
)
print(f'✓ Retrieved {len(retrieved)} documents')
if retrieved:
    print(f'   Sample: {retrieved[0].get("content", "")[:150]}...')


