#!/usr/bin/env python3
import chromadb
import os

# Use same path as backend
app_root = os.path.dirname(os.path.abspath(__file__))
persist_dir = os.path.join(app_root, "chroma_db")

try:
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection("kaggle_competition_data")
    
    # Get a few notebooks
    notebooks = collection.get(
        where={"$and": [{"section": "notebooks"}, {"competition_slug": "titanic"}]},
        include=['metadatas'],
        limit=3
    )
    
    print(f"📊 Found {len(notebooks['ids'])} notebooks\n")
    
    for i, (doc_id, meta) in enumerate(zip(notebooks['ids'], notebooks['metadatas'])):
        print(f"Notebook {i+1}:")
        print(f"  Title: {meta.get('title', 'Unknown')}")
        print(f"  Keys: {list(meta.keys())}")
        print(f"  Author: {meta.get('author', 'N/A')}")
        print(f"  Votes: {meta.get('votes', 'N/A')}")
        print(f"  notebook_path: {meta.get('notebook_path', 'MISSING')}")
        print(f"  subsection: {meta.get('subsection', 'N/A')}")
        print()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

