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
    
    # Get notebooks
    notebooks = collection.get(
        where={"section": "notebooks"},
        include=['metadatas'],
        limit=50
    )
    
    print(f"\n📊 Found {len(notebooks['ids'])} notebooks")
    
    # Group by competition_slug
    by_slug = {}
    for meta in notebooks['metadatas']:
        slug = meta.get('competition_slug', 'unknown')
        by_slug[slug] = by_slug.get(slug, 0) + 1
    
    print(f"\n📝 Notebooks by competition:")
    for slug, count in sorted(by_slug.items()):
        print(f"  {slug}: {count}")
    
    # Try querying with both filters
    print(f"\n🔍 Testing filter: section='notebooks' AND competition_slug='titanic'")
    result = collection.get(
        where={
            "$and": [
                {"section": "notebooks"},
                {"competition_slug": "titanic"}
            ]
        },
        include=['metadatas'],
        limit=10
    )
    print(f"  Result: {len(result['ids'])} notebooks")
    
    # Try without $and
    print(f"\n🔍 Testing filter: section='notebooks', competition_slug='titanic' (dict)")
    result2 = collection.get(
        where={"section": "notebooks", "competition_slug": "titanic"},
        include=['metadatas'],
        limit=10
    )
    print(f"  Result: {len(result2['ids'])} notebooks")
    
    if len(result2['ids']) > 0:
        print(f"\n✅ Found notebooks! Titles:")
        for meta in result2['metadatas'][:5]:
            print(f"  - {meta.get('title', 'Unknown')}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

