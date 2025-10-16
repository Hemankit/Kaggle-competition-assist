#!/usr/bin/env python3
"""Check what overview sections are in ChromaDB"""
import sys
sys.path.insert(0, '.')

from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

print('Checking Overview Sections in ChromaDB')
print('=' * 70)

pipeline = ChromaDBRAGPipeline()
collection = pipeline.retriever._get_collection()

# Get all overview sections for titanic
results = collection.get(
    where={'$and': [{'competition_slug': 'titanic'}, {'section': 'overview'}]},
    include=['metadatas', 'documents']
)

if results and results['metadatas']:
    print(f'\nFound {len(results["metadatas"])} overview documents')
    print('\nSections stored:')
    
    sections = {}
    for i, meta in enumerate(results['metadatas']):
        section_name = meta.get('overview_section', 'unknown')
        title = meta.get('title', 'No title')
        doc_len = len(results['documents'][i]) if results['documents'] else 0
        
        if section_name not in sections:
            sections[section_name] = []
        sections[section_name].append((title, doc_len))
    
    for section in sorted(sections.keys()):
        docs = sections[section]
        print(f'\n  {section}:')
        for title, length in docs:
            print(f'    - {title} ({length} chars)')
else:
    print('No sections found')


