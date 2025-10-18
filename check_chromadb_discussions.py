#!/usr/bin/env python3
import chromadb
import os

# Use same path as backend
app_root = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.join(app_root, "chroma_db")

print(f"📁 Checking ChromaDB at: {persist_dir}")
print("=" * 60)

try:
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection("kaggle_competition_data")
    
    # Get discussions
    print(f"\n🔍 Looking for discussions (section='discussions')...")
    discussions = collection.get(
        where={"$and": [{"section": "discussions"}, {"competition_slug": "titanic"}]},
        include=['metadatas'],
        limit=50
    )
    
    discussion_count = len(discussions['ids'])
    print(f"  Found {discussion_count} discussions for titanic")
    
    if discussion_count > 0:
        print(f"\n📊 Sample discussion metadata:")
        for i, (doc_id, meta) in enumerate(zip(discussions['ids'][:5], discussions['metadatas'][:5])):
            print(f"\n  Discussion {i+1}:")
            print(f"    Title: {meta.get('title', 'Unknown')}")
            print(f"    Author: {meta.get('author', 'Unknown')}")
            print(f"    Pinned: {meta.get('is_pinned', False)}")
            print(f"    Keys: {list(meta.keys())}")
    
    # Test semantic search with overfitting
    print(f"\n🔍 Testing semantic search for 'overfitting'...")
    from sentence_transformers import SentenceTransformer
    
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = embedding_model.encode("discussions about overfitting validation").tolist()
    
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={"$and": [{"section": "discussions"}, {"competition_slug": "titanic"}]},
        include=["documents", "metadatas", "distances"]
    )
    
    print(f"  Found {len(result['ids'][0])} relevant discussions")
    
    if len(result['ids'][0]) > 0:
        print(f"\n📝 Top results:")
        for i, (doc, meta, dist) in enumerate(zip(result['documents'][0][:3], result['metadatas'][0][:3], result['distances'][0][:3])):
            print(f"\n  Result {i+1} (distance: {dist:.3f}):")
            print(f"    Title: {meta.get('title', 'Unknown')}")
            print(f"    Preview: {doc[:150]}...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

