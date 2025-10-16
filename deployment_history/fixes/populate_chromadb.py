#!/usr/bin/env python3
"""
Populate ChromaDB with Titanic Competition Data
"""
print('Populating ChromaDB with Titanic Competition Data')
print('=' * 60)

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Initialize ChromaDB pipeline
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

print('Initializing ChromaDB pipeline...')
rag_pipeline = ChromaDBRAGPipeline(collection_name='kaggle_competition_data')
print('✓ Pipeline initialized')

# Fetch Titanic competition data from Kaggle API
from kaggle import api
api.authenticate()

print('Fetching Titanic competition details...')
competitions = api.competitions_list(search='titanic')
comp = competitions[0]

# Prepare competition data
competition_data = {
    'title': comp.title,
    'ref': comp.ref,
    'description': comp.description if hasattr(comp, 'description') else '',
    'deadline': str(comp.deadline),
    'category': comp.category if hasattr(comp, 'category') else 'Getting Started',
    'reward': comp.reward if hasattr(comp, 'reward') else 'Knowledge',
}

print('Competition:', competition_data['title'])
print('Category:', competition_data['category'])

# Create documents for indexing
api_results = [
    {
        'content': competition_data['description'] or comp.title,
        'meta': {
            'competition_slug': 'titanic',
            'section': 'overview',
            'title': competition_data['title'],
            'category': competition_data['category'],
            'deadline': competition_data['deadline'],
            'source': 'kaggle_api'
        }
    }
]

# Add more detailed description
detailed_desc = """Titanic - Machine Learning from Disaster

This is a Getting Started competition on Kaggle.

Competition Details:
* Slug: titanic
* Category: Getting Started
* Reward: Knowledge
* URL: https://www.kaggle.com/competitions/titanic

The Titanic competition is one of Kaggle's most popular getting-started competitions. 
It challenges participants to predict survival on the Titanic using passenger data 
including age, gender, ticket class, and other features.

Key Features:
* Binary classification problem (survived or not)
* Real historical data from the Titanic disaster
* Beginner-friendly competition
* Classic machine learning dataset
"""

api_results.append({
    'content': detailed_desc,
    'meta': {
        'competition_slug': 'titanic',
        'section': 'detailed_overview',
        'title': competition_data['title'],
        'source': 'kaggle_api_enriched'
    }
})

print(f'Indexing {len(api_results)} documents into ChromaDB...')
result = rag_pipeline.index_api_data(api_results)
print('✓', result)

# Verify data was indexed
print('\nVerifying indexed data...')
query = 'What is the Titanic competition about?'
retrieved = rag_pipeline.rerank_document_store(query, top_k_retrieval=5, top_k_final=3)
print(f'✓ Retrieved {len(retrieved)} documents')

if retrieved:
    print('\nSample retrieved content:')
    for i, doc in enumerate(retrieved[:2]):
        content = doc.get('content', '')
        preview = content[:150].replace('\n', ' ')
        print(f'  Document {i+1}: {preview}...')
else:
    print('⚠ No documents retrieved')

print()
print('=' * 60)
print('✅ SUCCESS: ChromaDB populated with Titanic competition data!')


