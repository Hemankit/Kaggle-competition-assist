"""
Check what embedding dimensions the collection actually has
"""
import chromadb
import os

persist_dir = os.path.join(os.getcwd(), "chroma_db")
client = chromadb.PersistentClient(path=persist_dir)

collection = client.get_collection("kaggle_competition_data")

print("="*70)
print("COLLECTION METADATA")
print("="*70)

print(f"Name: {collection.name}")
print(f"Count: {collection.count()}")
print(f"Metadata: {collection.metadata}")

# Try to get one document to see its embedding dimension
result = collection.get(limit=1, include=["embeddings", "metadatas"])

if result and result['embeddings']:
    embedding_dim = len(result['embeddings'][0])
    print(f"\nEmbedding dimension in collection: {embedding_dim}")
    
    if embedding_dim == 384:
        print("✓ Collection uses 384-dimensional embeddings (BAAI/bge-base-en)")
    elif embedding_dim == 768:
        print("✗ Collection uses 768-dimensional embeddings (different model!)")
    else:
        print(f"? Collection uses {embedding_dim}-dimensional embeddings (unknown model)")
else:
    print("\nCould not retrieve embeddings")

print("="*70)




