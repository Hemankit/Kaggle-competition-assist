"""
Simple check of ChromaDB without querying
"""
import chromadb
import os

persist_dir = os.path.join(os.getcwd(), "chroma_db")
client = chromadb.PersistentClient(path=persist_dir)

print("="*70)
print("CHROMADB STATUS")
print("="*70)

# List all collections
collections = client.list_collections()
print(f"\nTotal collections: {len(collections)}")

for coll in collections:
    print(f"\nCollection: {coll.name}")
    print(f"  Count: {coll.count()}")
    # Get metadata if available
    try:
        metadata = coll.metadata
        print(f"  Metadata: {metadata}")
    except:
        pass

print("\n" + "="*70)




