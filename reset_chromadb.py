"""
Reset ChromaDB - delete old collection and recreate
"""
import chromadb
import os

# Connect to ChromaDB
persist_dir = os.path.join(os.getcwd(), "chroma_db")
client = chromadb.PersistentClient(path=persist_dir)

print("="*70)
print("RESETTING CHROMADB")
print("="*70)

# Delete old collection
try:
    client.delete_collection("kaggle_competition_data")
    print("[OK] Deleted old collection")
except Exception as e:
    print(f"[INFO] No existing collection to delete: {e}")

# List collections
collections = client.list_collections()
print(f"\n[INFO] Collections after reset: {[c.name for c in collections]}")

print("\n" + "="*70)
print("RESET COMPLETE - Ready for fresh data!")
print("="*70)




