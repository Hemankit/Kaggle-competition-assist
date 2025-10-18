#!/usr/bin/env python3
import chromadb
import os
from sentence_transformers import SentenceTransformer

# Use same path as backend
app_root = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.join(app_root, "chroma_db")

print(f"📁 Testing collection.query() vs collection.get() with WHERE clause")
print("=" * 60)

try:
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection("kaggle_competition_data")
    
    # Test 1: collection.get() with WHERE (we know this works)
    print(f"\n✅ Test 1: collection.get() with WHERE")
    result_get = collection.get(
        where={"$and": [{"section": "notebooks"}, {"competition_slug": "titanic"}]},
        limit=5
    )
    print(f"  Result: {len(result_get['ids'])} documents")
    
    # Test 2: collection.query() with WHERE
    print(f"\n🔍 Test 2: collection.query() with WHERE")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = embedding_model.encode("top notebooks code for titanic").tolist()
    
    result_query = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={"$and": [{"section": "notebooks"}, {"competition_slug": "titanic"}]},
        include=["documents", "metadatas", "distances"]
    )
    print(f"  Result: {len(result_query['ids'][0])} documents")
    
    if len(result_query['ids'][0]) > 0:
        print(f"\n✅ SUCCESS! collection.query() with WHERE works!")
        for i, meta in enumerate(result_query['metadatas'][0][:3]):
            print(f"  {i+1}. {meta.get('title', 'Unknown')}")
    else:
        print(f"\n❌ FAILED! collection.query() with WHERE returns 0 results")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

