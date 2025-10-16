#!/usr/bin/env python3
"""Debug what sections are being returned by the overview query"""
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

pipeline = ChromaDBRAGPipeline()
collection = pipeline.retriever._get_collection()

# Simulate the query for "Tell me about the Titanic disaster"
query = "Tell me about the Titanic disaster and what happened in 1912"

# Encode query
query_embedding = pipeline.retriever.embedding_model.encode(query).tolist()

# Query ChromaDB
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=15,
    where={'$and': [{'competition_slug': 'titanic'}, {'section': 'overview'}]},
    include=['metadatas', 'documents']
)

print('Query:', query)
print('='*70)
print(f'\nGot {len(results["documents"][0])} sections:')
print()

for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    title = meta.get('title', 'No title')
    length = len(doc)
    
    # Show snippet
    snippet = doc[:200].replace('\n', ' ')
    
    print(f'{i+1}. {title}')
    print(f'   Length: {length} chars')
    print(f'   Snippet: {snippet}...')
    
    # Check if this is the Description section
    if 'description' in title.lower():
        print('   ⭐ THIS IS THE DESCRIPTION SECTION!')
        if 'april' in doc.lower() or '1912' in doc:
            print('   ✅ Contains historical details!')
        else:
            print('   ❌ Missing historical details')
    
    print()


