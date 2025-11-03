#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrape Titanic Discussions and Populate ChromaDB
Uses existing discussion_scraper_v2 to scrape, then indexes into ChromaDB
"""
import sys
import os
import hashlib
import logging
import json

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print('Scraping and Populating Titanic Discussions')
print('=' * 60)

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Step 1: Scrape discussions using existing scraper
print('\n[STEP 1] Scraping Titanic discussions...')
from scraper.discussion_scraper_v2 import DiscussionScraperV2

try:
    scraper = DiscussionScraperV2(
        input_link="titanic",
        output_dir="data/discussions"
    )
    
    print('[SCRAPE] Fetching discussions from Kaggle...')
    discussions_data = scraper.scrape(retries=2, apply_ocr=False)  # Skip OCR for speed
    
    print(f'[OK] Scraped {len(discussions_data)} discussions')
    
    # Save to file for reference
    os.makedirs("data/discussions", exist_ok=True)
    output_file = "data/discussions/titanic_discussions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(discussions_data, f, indent=2, ensure_ascii=False)
    print(f'[OK] Saved to {output_file}')
    
except Exception as e:
    print(f'[ERROR] Scraping failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Initialize ChromaDB pipeline
print('\n[STEP 2] Initializing ChromaDB pipeline...')
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

rag_pipeline = ChromaDBRAGPipeline(
    collection_name='kaggle_competition_data', 
    embedding_model='all-mpnet-base-v2',
    target_sections=["overview", "discussion", "code"]
)
print('[OK] Pipeline initialized')

# Step 3: Convert to ChromaDB format and index
print('\n[STEP 3] Converting and indexing discussions...')

discussion_docs = []

for i, disc in enumerate(discussions_data, 1):
    print(f'\r[PROCESS] Converting {i}/{len(discussions_data)}...', end='', flush=True)
    
    # Extract data from scraped format
    title = disc.get('title', 'Unknown')
    author = disc.get('author', 'Unknown')
    content = disc.get('content', '')
    date = disc.get('date', 'Unknown')
    is_pinned = disc.get('is_pinned', False)
    post_id = disc.get('post_id', str(i))
    
    # Create document content
    doc_content = f"""
Discussion: {title}
Author: {author}
Date: {date}
Type: {'[PINNED]' if is_pinned else 'Community Discussion'}

Content:
{content}

Competition: Titanic - Machine Learning from Disaster

This discussion is part of the Titanic competition community forum.
"""
    
    # Generate content hash for unique ID
    content_hash = hashlib.sha256(doc_content.encode('utf-8')).hexdigest()[:16]
    
    # Create document - flatten important metadata
    discussion_docs.append({
        'content': doc_content,
        'section': 'discussion',  # IMPORTANT: For section filtering!
        'content_hash': content_hash,  # CRITICAL: For unique ChromaDB IDs!
        'competition_slug': 'titanic',
        'title': title,
        'author': author,
        'discussion_id': post_id,
        'is_pinned': is_pinned,
        'date': date,
        'source': 'discussion_scraper_v2'
    })

print(f'\n[OK] Converted {len(discussion_docs)} discussions')

# Index into ChromaDB
print('\n[INDEX] Indexing discussions into ChromaDB...')

pydantic_results = []
result = rag_pipeline.chunker.chunk_and_index(
    pydantic_results=pydantic_results,
    structured_results=discussion_docs,
    indexer=rag_pipeline.indexer
)

print(f'\n[SUCCESS] INDEXING COMPLETE!')
print(f'   - Documents indexed: {len(discussion_docs)}')
print(f'   - Chunks created: {result.get("chunks_created", 0)}')
print(f'   - Documents processed: {result.get("documents_processed", 0)}')
print(f'   - Errors: {result.get("errors", 0)}')
print(f'   - Status: {result.get("status", "unknown")}')

# Step 4: Test retrieval
print('\n[STEP 4] Testing retrieval...')
test_query = "What are people discussing about feature engineering?"

retrieved = rag_pipeline.rerank_document_store(
    query=test_query,
    top_k_retrieval=10,
    top_k_final=5,
    competition_slug='titanic',
    section='discussion'
)

print(f'   - Query: "{test_query}"')
print(f'   - Retrieved: {len(retrieved)} documents')

if retrieved:
    print('\n[SAMPLE] Sample retrieved discussion:')
    sample = retrieved[0]
    print(f'   - Title: {sample.get("metadata", {}).get("title", "Unknown")}')
    print(f'   - Author: {sample.get("metadata", {}).get("author", "Unknown")}')
    print(f'   - Pinned: {sample.get("metadata", {}).get("is_pinned", False)}')

print('\n[SUCCESS] Discussions are now indexed and ready for DiscussionHelperAgent!')

print('\n' + '=' * 60)
print('[DONE] Scraping and population complete!')
print('=' * 60)

