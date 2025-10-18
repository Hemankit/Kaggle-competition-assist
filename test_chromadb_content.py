"""
Test what's actually in ChromaDB on EC2
"""
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

# Connect to ChromaDB
rag_pipeline = ChromaDBRAGPipeline(collection_name="kaggle_competition_data")

# Query for data description
print("="*70)
print("TESTING CHROMADB CONTENT")
print("="*70)

# Test 1: Get all data_description documents
print("\n1. Querying for data_description section...")
results = rag_pipeline.retriever._get_collection().query(
    query_texts=["columns data features"],
    n_results=10,
    where={
        "$and": [
            {"competition_slug": "titanic"},
            {"section": "data_description"}
        ]
    }
)

if results and results['documents'] and results['documents'][0]:
    print(f"   Found {len(results['documents'][0])} documents")
    for i, doc in enumerate(results['documents'][0][:3]):
        print(f"\n   Document {i+1}:")
        print(f"   {doc[:300]}...")
else:
    print("   NO DOCUMENTS FOUND!")

# Test 2: Get overview documents
print("\n2. Querying for overview section...")
overview_results = rag_pipeline.retriever._get_collection().query(
    query_texts=["evaluation metric accuracy"],
    n_results=10,
    where={
        "$and": [
            {"competition_slug": "titanic"},
            {"section": "overview"}
        ]
    }
)

if overview_results and overview_results['documents'] and overview_results['documents'][0]:
    print(f"   Found {len(overview_results['documents'][0])} documents")
    for i, doc in enumerate(overview_results['documents'][0][:2]):
        print(f"\n   Document {i+1}:")
        print(f"   {doc[:200]}...")
else:
    print("   NO DOCUMENTS FOUND!")

# Test 3: Count total documents
print("\n3. Checking collection stats...")
collection = rag_pipeline.retriever._get_collection()
print(f"   Collection name: {collection.name}")
count = collection.count()
print(f"   Total documents: {count}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)




