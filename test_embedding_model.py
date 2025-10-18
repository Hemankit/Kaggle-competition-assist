"""
Test what embedding dimension BAAI/bge-base-en actually has
"""
from sentence_transformers import SentenceTransformer

print("="*70)
print("TESTING EMBEDDING MODEL")
print("="*70)

model_name = "BAAI/bge-base-en"
print(f"\nLoading model: {model_name}")

model = SentenceTransformer(model_name)
dim = model.get_sentence_embedding_dimension()

print(f"Embedding dimension: {dim}")

if dim == 384:
    print("✓ Correct! Should be 384")
elif dim == 768:
    print("✗ WRONG! Got 768 instead of 384")
    print("This might be loading a different variant!")
else:
    print(f"? Unexpected dimension: {dim}")

# Test actual embedding
test_embedding = model.encode("test")
print(f"\nActual embedding length: {len(test_embedding)}")

print("="*70)




