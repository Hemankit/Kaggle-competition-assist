"""
Test script for ChromaDB RAG Pipeline.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_chromadb_pipeline():
    """Test the ChromaDB RAG pipeline."""
    try:
        print("🧪 Testing ChromaDB RAG Pipeline...")
        
        # Test imports
        from RAG_pipeline_chromadb import ChromaDBRAGPipeline
        print("✅ ChromaDB imports successful")
        
        # Test initialization
        pipeline = ChromaDBRAGPipeline()
        print("✅ ChromaDB pipeline initialization successful")
        
        # Test with sample data
        sample_documents = [
            {
                "content": "This is a sample Kaggle competition overview about machine learning.",
                "metadata": {"section": "overview", "title": "Sample Competition"},
                "section": "overview"
            },
            {
                "content": "This is a discussion about feature engineering techniques.",
                "metadata": {"section": "discussion", "title": "Feature Engineering"},
                "section": "discussion"
            }
        ]
        
        # Test indexing
        result = pipeline.index_scraped_data([], sample_documents)
        print(f"✅ Indexing test: {result}")
        
        # Test retrieval
        query = "machine learning techniques"
        retrieved = pipeline.rerank_document_store(query, top_k_retrieval=5, top_k_final=3)
        print(f"✅ Retrieval test: Found {len(retrieved)} documents")
        
        print("🎉 ChromaDB RAG Pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB RAG Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    test_chromadb_pipeline()
