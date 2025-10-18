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
    
    # Get all documents
    all_docs = collection.get(include=['metadatas'])
    total_count = len(all_docs['ids'])
    
    print(f"\n✅ Total documents in ChromaDB: {total_count}")
    
    # Count by section
    sections = {}
    for meta in all_docs['metadatas']:
        sec = meta.get('section', 'unknown')
        sections[sec] = sections.get(sec, 0) + 1
    
    print(f"\n📊 Documents by section:")
    for sec, count in sorted(sections.items()):
        print(f"  {sec}: {count}")
    
    # Check for notebooks specifically
    print(f"\n🔍 Looking for notebooks (section='code')...")
    notebooks = collection.get(
        where={"section": "code"},
        include=['metadatas']
    )
    notebook_count = len(notebooks['ids'])
    
    print(f"  Found {notebook_count} notebooks")
    
    if notebook_count > 0:
        print(f"\n📓 Notebook details:")
        for i, (doc_id, meta) in enumerate(zip(notebooks['ids'], notebooks['metadatas'])):
            print(f"  {i+1}. {meta.get('title', 'Unknown')} ({meta.get('competition_slug', 'unknown')})")
    else:
        print(f"\n❌ NO NOTEBOOKS FOUND!")
        print(f"   Notebooks are being stored but not indexed correctly!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

