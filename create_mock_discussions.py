#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Mock Titanic Discussion Data for Testing
"""
import sys
import os
import hashlib

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print('Creating Mock Titanic Discussion Data')
print('=' * 60)

sys.path.insert(0, os.getcwd())

# Create realistic mock discussions about feature engineering
mock_discussions = [
    {
        "title": "Best Feature Engineering Techniques for Titanic",
        "author": "DataScientist123",
        "content": """I've been experimenting with different feature engineering approaches and wanted to share what worked best for me:

1. FamilySize = SibSp + Parch + 1
   This feature alone gave me a +2% boost. Families tend to survive together.

2. Title extraction from Name column
   Extracting titles like 'Mr', 'Mrs', 'Master', 'Miss' reveals social status better than Pclass alone.
   I group rare titles like 'Lady', 'Countess', 'Sir' into a 'Rare' category.

3. Age binning
   Instead of using raw age, I bin into: Child (0-16), Young Adult (16-32), Adult (32-48), Senior (48+)
   Missing ages I impute using median age per Title.

4. Fare per person = Fare / FamilySize
   Accounts for shared tickets.

These 4 features took me from 0.77 to 0.82 accuracy. Hope this helps!""",
        "date": "2024-10-15",
        "is_pinned": True
    },
    {
        "title": "Age Imputation Strategies - What Works Best?",
        "author": "MLEnthusiast",
        "content": """There's a lot of debate about how to handle missing Age values. Here's what I've tried:

Method 1: Median imputation (simple)
- Fill with overall median age: 28
- Quick but loses information
- Result: 0.78 accuracy

Method 2: Median by Title (better)
- Mr: 30, Mrs: 35, Miss: 22, Master: 5
- Preserves age patterns by social status
- Result: 0.80 accuracy

Method 3: Predictive imputation (complex)
- Train a model to predict Age based on other features
- More accurate but risks overfitting
- Result: 0.81 accuracy (but slower)

I recommend Method 2 for best balance of simplicity and performance.""",
        "date": "2024-10-12",
        "is_pinned": False
    },
    {
        "title": "Cabin Feature: Worth the Effort?",
        "author": "FeatureEngineer",
        "content": """Cabin has 77% missing values. Should we use it?

Approach 1: Drop it entirely
- Easiest solution
- Many top solutions ignore Cabin
- Still achieves 0.80+ accuracy

Approach 2: Extract deck letter (C -> C deck)
- Cabin starts with deck letter (A, B, C, etc.)
- Create 'Deck' feature + 'Has_Cabin' binary flag
- Adds +1% accuracy for me (0.81)

Approach 3: Impute missing cabins
- Too much guesswork, not recommended
- Risks adding noise

My take: Extract deck + Has_Cabin flag. Small gain but worth it.""",
        "date": "2024-10-10",
        "is_pinned": False
    },
    {
        "title": "Debate: Should We Use Neural Networks?",
        "author": "DeepLearningFan",
        "content": """I see some solutions using neural networks. Is it overkill?

PRO Neural Network:
- Can learn complex interactions
- Cool to implement
- Good learning experience

CON Neural Network:
- Dataset is small (891 samples)
- Easy to overfit
- Most top solutions use RandomForest/XGBoost
- Slower training

My experience: NN got me 0.76 accuracy. Switched to RandomForest with good features → 0.82.

Community consensus seems to be: Focus on feature engineering, use simple models.""",
        "date": "2024-10-08",
        "is_pinned": False
    },
    {
        "title": "Feature Engineering Checklist",
        "author": "KaggleMaster",
        "content": """After 50+ Titanic submissions, here's my checklist:

✅ MUST-HAVE Features:
1. FamilySize (SibSp + Parch + 1)
2. Title extracted from Name
3. IsAlone (FamilySize == 1)
4. Age bins (not raw age)

✅ NICE-TO-HAVE:
5. Deck from Cabin
6. FarePerPerson
7. Title_Age interaction

❌ DON'T WASTE TIME:
- Ticket number (too noisy)
- Predicting missing Cabin
- Deep learning (dataset too small)

Follow this and you'll hit 0.82+ easily!""",
        "date": "2024-10-05",
        "is_pinned": True
    }
]

# Convert to ChromaDB format
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

print('[INIT] Initializing ChromaDB pipeline...')
rag_pipeline = ChromaDBRAGPipeline(
    collection_name='kaggle_competition_data', 
    embedding_model='all-mpnet-base-v2',
    target_sections=["overview", "discussion", "code"]
)
print('[OK] Pipeline initialized')

print(f'\n[PROCESS] Converting {len(mock_discussions)} mock discussions...')

discussion_docs = []

for i, disc in enumerate(mock_discussions, 1):
    title = disc['title']
    author = disc['author']
    content = disc['content']
    date = disc['date']
    is_pinned = disc['is_pinned']
    
    doc_content = f"""
Discussion: {title}
Author: {author}
Date: {date}
Type: {'[PINNED]' if is_pinned else 'Community Discussion'}

Content:
{content}

Competition: Titanic - Machine Learning from Disaster
"""
    
    content_hash = hashlib.sha256(doc_content.encode('utf-8')).hexdigest()[:16]
    
    discussion_docs.append({
        'content': doc_content,
        'section': 'discussion',
        'content_hash': content_hash,
        'competition_slug': 'titanic',
        'title': title,
        'author': author,
        'is_pinned': is_pinned,
        'date': date,
        'source': 'mock_data'
    })
    
    print(f'  [{i}/{len(mock_discussions)}] {title[:50]}...')

print(f'\n[INDEX] Indexing {len(discussion_docs)} discussions into ChromaDB...')

result = rag_pipeline.chunker.chunk_and_index(
    pydantic_results=[],
    structured_results=discussion_docs,
    indexer=rag_pipeline.indexer
)

print(f'\n[SUCCESS] INDEXING COMPLETE!')
print(f'   - Chunks created: {result.get("chunks_created", 0)}')
print(f'   - Documents processed: {result.get("documents_processed", 0)}')
print(f'   - Status: {result.get("status", "unknown")}')

# Test retrieval
print('\n[TEST] Testing retrieval...')
retrieved = rag_pipeline.rerank_document_store(
    query="What are people discussing about feature engineering?",
    top_k_retrieval=10,
    top_k_final=5,
    competition_slug='titanic',
    section='discussion'
)

print(f'   - Retrieved: {len(retrieved)} documents')
if retrieved:
    print(f'   - Sample: {retrieved[0].get("metadata", {}).get("title", "N/A")}')

print('\n' + '=' * 60)
print('[DONE] Mock discussions ready for DiscussionHelperAgent testing!')
print('=' * 60)

