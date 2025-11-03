#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate ChromaDB with Titanic Discussions
Fetches discussion posts from Kaggle and indexes them for DiscussionHelperAgent
"""
import sys
import os
import hashlib
import logging

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print('Populating ChromaDB with Titanic Discussions')
print('=' * 60)

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Initialize ChromaDB pipeline
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

print('[INIT] Initializing ChromaDB pipeline...')
# IMPORTANT: Include "discussion" in target_sections!
rag_pipeline = ChromaDBRAGPipeline(
    collection_name='kaggle_competition_data', 
    embedding_model='all-mpnet-base-v2',
    target_sections=["overview", "discussion", "code"]  # Add "discussion" for posts!
)
print('[OK] Pipeline initialized with target_sections: overview, discussion, code')

# Fetch Titanic discussions from Kaggle API
from kaggle import api
api.authenticate()

print('\n[FETCH] Fetching Titanic discussions...')
try:
    # Get discussions for Titanic competition
    discussions = api.discussion_list(
        competition='titanic',
        page_size=20  # Get top 20 discussions
    )
    
    print(f'[OK] Found {len(discussions)} discussions')
    
    # Prepare discussion documents for indexing
    discussion_docs = []
    
    for i, discussion in enumerate(discussions, 1):
        print(f'\n[PROCESS] Discussion {i}/{len(discussions)}: {discussion.title}')
        
        # Extract metadata
        author = discussion.author if hasattr(discussion, 'author') else 'Unknown'
        
        # Determine if pinned
        is_pinned = getattr(discussion, 'is_pinned', False)
        
        # Create document content
        content = f"""
Discussion: {discussion.title}
Author: {author}
Created: {getattr(discussion, 'created_date', 'Unknown')}
Type: {'[PINNED]' if is_pinned else 'Community Discussion'}
URL: https://www.kaggle.com{discussion.url if hasattr(discussion, 'url') else f'/c/titanic/discussion/{discussion.id}'}

Topic: {discussion.title}

Competition: Titanic - Machine Learning from Disaster

Discussion Details:
- ID: {discussion.id}
- Author: {author}
- Comment Count: {getattr(discussion, 'comment_count', 0)}
- Vote Count: {getattr(discussion, 'total_votes', 0)}
- Is Pinned: {is_pinned}

This discussion is part of the Titanic competition community forum.
It contains insights, questions, solutions, and collaborative problem-solving
from the Kaggle community working on the Titanic survival prediction challenge.
"""

        # Try to get discussion content if available
        try:
            print(f'  [INFO] Comments: {getattr(discussion, "comment_count", 0)}, Votes: {getattr(discussion, "total_votes", 0)}')
            
        except Exception as e:
            print(f'  [WARN] Could not fetch full discussion: {e}')
        
        # Generate content hash for unique ID
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
        
        # Create document - flatten important metadata to top level for chunker!
        discussion_docs.append({
            'content': content,
            'section': 'discussion',  # IMPORTANT: For section filtering!
            'content_hash': content_hash,  # CRITICAL: For unique ChromaDB IDs!
            'competition_slug': 'titanic',  # Top-level for metadata extraction
            'title': discussion.title,  # Top-level for metadata extraction
            'author': author,  # Top-level for metadata extraction
            'discussion_id': str(discussion.id),
            'comment_count': getattr(discussion, 'comment_count', 0),
            'total_votes': getattr(discussion, 'total_votes', 0),
            'is_pinned': is_pinned,
            'created_date': str(getattr(discussion, 'created_date', '')),
            'url': f"https://www.kaggle.com{discussion.url if hasattr(discussion, 'url') else f'/c/titanic/discussion/{discussion.id}'}",
            'source': 'kaggle_api_discussions'
        })
    
    print(f'\n[INFO] Prepared {len(discussion_docs)} discussion documents')
    
    # Convert to pydantic format (empty for now, using structured results)
    pydantic_results = []
    
    # Index discussions into ChromaDB
    print('\n[INDEX] Indexing discussions into ChromaDB...')
    print(f'[DEBUG] Sample document structure: {list(discussion_docs[0].keys())}')
    print(f'[DEBUG] Sample document section: {discussion_docs[0].get("section")}')
    print(f'[DEBUG] Sample document content_hash: {discussion_docs[0].get("content_hash", "MISSING!")}')
    print(f'[DEBUG] Sample document content length: {len(discussion_docs[0].get("content", ""))}')
    print(f'[DEBUG] Chunker target_sections: {rag_pipeline.chunker.target_sections}')
    
    result = rag_pipeline.chunker.chunk_and_index(
        pydantic_results=pydantic_results,
        structured_results=discussion_docs,
        indexer=rag_pipeline.indexer
    )
    
    print(f'\n[SUCCESS] INDEXING COMPLETE!')
    print(f'   - Documents indexed: {len(discussion_docs)}')
    print(f'   - Chunks created: {result.get("chunks_created", 0)}')  # Fixed key name!
    print(f'   - Documents processed: {result.get("documents_processed", 0)}')
    print(f'   - Errors: {result.get("errors", 0)}')
    print(f'   - Status: {result.get("status", "unknown")}')
    
    # Test retrieval
    print('\n[TEST] Testing retrieval...')
    test_query = "What are people discussing about feature engineering?"
    
    # Test 1: Direct retrieval with section filter (using $and operator)
    print('\n[TEST 1] Direct retrieval with section filter:')
    direct_retrieved = rag_pipeline.retriever.retrieve(
        query=test_query,
        top_k=5,
        where={"$and": [{"section": "discussion"}, {"competition_slug": "titanic"}]}
    )
    print(f'   - Direct retrieved: {len(direct_retrieved)} documents')
    if direct_retrieved:
        print(f'   - Sample: {direct_retrieved[0].get("metadata", {}).get("title", "N/A")}')
    
    # Test 2: Rerank with section filter
    print('\n[TEST 2] Rerank with section filter:')
    retrieved = rag_pipeline.rerank_document_store(
        query=test_query,
        top_k_retrieval=10,
        top_k_final=5,
        competition_slug='titanic',
        section='discussion'  # Filter by section="discussion"!
    )
    
    print(f'   - Reranked retrieved: {len(retrieved)} documents')
    
    if retrieved:
        print('\n[SAMPLE] Sample retrieved discussion:')
        sample = retrieved[0]
        print(f'   - Title: {sample.get("metadata", {}).get("title", "Unknown")}')
        print(f'   - Author: {sample.get("metadata", {}).get("author", "Unknown")}')
        print(f'   - Comments: {sample.get("metadata", {}).get("comment_count", 0)}')
        print(f'   - Pinned: {sample.get("metadata", {}).get("is_pinned", False)}')
    
    print('\n[SUCCESS] Discussions are now indexed and ready for DiscussionHelperAgent!')
    
except Exception as e:
    print(f'\n[ERROR] {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n' + '=' * 60)
print('[OK] Discussion population complete!')
print('=' * 60)

