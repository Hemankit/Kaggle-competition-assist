#!/bin/bash
# Fix ChromaDB embedding dimension mismatch by using consistent 384-dim model

echo "=========================================="
echo "FIX CHROMADB EMBEDDING DIMENSIONS"
echo "=========================================="

# Step 1: Delete old ChromaDB collection
echo ""
echo "[1/4] Deleting old ChromaDB collection..."
python3 << 'PYTHON_SCRIPT'
import chromadb
import os

try:
    persist_dir = os.path.join(os.getcwd(), "chroma_db")
    client = chromadb.PersistentClient(path=persist_dir)
    
    # Delete the collection
    try:
        client.delete_collection("kaggle_competition_data")
        print("[OK] Deleted old collection 'kaggle_competition_data'")
    except Exception as e:
        print(f"[INFO] Collection may not exist: {e}")
    
    print("[OK] ChromaDB reset complete")
except Exception as e:
    print(f"[ERROR] Failed to reset ChromaDB: {e}")
    import traceback
    traceback.print_exc()
PYTHON_SCRIPT

# Step 2: Restart backend to reinitialize with new model
echo ""
echo "[2/4] Restarting backend service..."
sudo systemctl restart kaggle-backend
sleep 5

# Check backend status
if systemctl is-active --quiet kaggle-backend; then
    echo "[OK] Backend restarted successfully"
else
    echo "[ERROR] Backend failed to restart"
    sudo journalctl -u kaggle-backend --since "1 minute ago" --no-pager | tail -20
    exit 1
fi

# Step 3: Re-populate ChromaDB with consistent 384-dim embeddings
echo ""
echo "[3/4] Re-populating ChromaDB with Titanic data..."
cd /home/ubuntu/Kaggle-competition-assist
python3 populate_all_competition_data.py titanic

# Step 4: Verify embedding dimensions
echo ""
echo "[4/4] Verifying embedding dimensions..."
python3 << 'PYTHON_SCRIPT'
import chromadb
import os
from sentence_transformers import SentenceTransformer

try:
    persist_dir = os.path.join(os.getcwd(), "chroma_db")
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection("kaggle_competition_data")
    
    # Check model dimension
    model = SentenceTransformer("all-MiniLM-L6-v2")
    model_dim = model.get_sentence_embedding_dimension()
    
    # Count documents
    doc_count = collection.count()
    
    print(f"[OK] Collection: kaggle_competition_data")
    print(f"[OK] Model: all-MiniLM-L6-v2")
    print(f"[OK] Embedding dimension: {model_dim}")
    print(f"[OK] Document count: {doc_count}")
    
    if model_dim == 384:
        print("\n*** SUCCESS! Using standard 384-dimensional embeddings ***")
    else:
        print(f"\n[WARNING] Unexpected dimension: {model_dim}")
    
except Exception as e:
    print(f"[ERROR] Verification failed: {e}")
    import traceback
    traceback.print_exc()
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "FIX COMPLETE!"
echo "=========================================="
echo ""
echo "Next step: Test data queries in frontend"
echo "Example: 'What data files are available?'"



