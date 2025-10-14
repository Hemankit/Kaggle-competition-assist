#!/usr/bin/env python3
"""
Test script for RAG Pipeline components
Tests: Both Haystack and ChromaDB implementations
Tests: rag_pipeline, chunking, indexing, retrieval, logging_utils
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_haystack_rag_pipeline():
    """Test Haystack RAG Pipeline initialization and basic functionality"""
    print("🔍 Testing Haystack RAG Pipeline...")
    
    try:
        from RAG_pipeline.rag_pipeline import HaystackRAGPipeline
        print("✅ Haystack import successful")
        
        # Test initialization with default parameters
        pipeline = HaystackRAGPipeline()
        print("✅ Haystack pipeline initialization successful")
        
        # Test basic methods exist
        methods = ['index_scraped_data', 'index_api_data', 'chunk_and_index', 'rerank_document_store', 'run']
        for method in methods:
            if hasattr(pipeline, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Haystack RAG Pipeline test failed: {e}")
        return False

def test_chromadb_rag_pipeline():
    """Test ChromaDB RAG Pipeline initialization and basic functionality"""
    print("\n🔍 Testing ChromaDB RAG Pipeline...")
    
    try:
        from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
        print("✅ ChromaDB import successful")
        
        # Test initialization with default parameters
        pipeline = ChromaDBRAGPipeline()
        print("✅ ChromaDB pipeline initialization successful")
        
        # Test basic methods exist
        methods = ['index_scraped_data', 'index_api_data', 'chunk_and_index', 'rerank_document_store', 'run']
        for method in methods:
            if hasattr(pipeline, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        # Test with sample data
        sample_documents = [
            {
                "content": "This is a sample Kaggle competition overview about machine learning.",
                "metadata": {"section": "overview", "title": "Sample Competition"},
                "section": "overview"
            }
        ]
        
        # Test indexing
        result = pipeline.index_scraped_data([], sample_documents)
        print(f"✅ Indexing test: {result}")
        
        # Test retrieval
        query = "machine learning techniques"
        retrieved = pipeline.rerank_document_store(query, top_k_retrieval=5, top_k_final=3)
        print(f"✅ Retrieval test: Found {len(retrieved)} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB RAG Pipeline test failed: {e}")
        return False

def test_chunking():
    """Test Chunking module initialization and basic functionality"""
    print("\n🔍 Testing Chunking...")
    
    try:
        from RAG_pipeline.chunking import Chunker
        print("✅ Import successful")
        
        # Test initialization (will create default document store)
        chunker = Chunker()
        print("✅ Chunker initialization successful")
        
        # Test basic methods exist
        methods = ['chunk_and_index', 'preprocess_documents', 'create_chunks']
        for method in methods:
            if hasattr(chunker, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Chunking test failed: {e}")
        return False

def test_indexing():
    """Test Indexing module initialization and basic functionality"""
    print("\n🔍 Testing Indexing...")
    
    try:
        from RAG_pipeline.indexing import Indexer
        print("✅ Import successful")
        
        # Test initialization (will create default document store)
        indexer = Indexer()
        print("✅ Indexer initialization successful")
        
        # Test basic methods exist
        methods = ['index_scraped_data', 'index_api_data', 'generate_embedding']
        for method in methods:
            if hasattr(indexer, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Indexing test failed: {e}")
        return False

def test_retrieval():
    """Test Retrieval module initialization and basic functionality"""
    print("\n🔍 Testing Retrieval...")
    
    try:
        from RAG_pipeline.retrieval import Retriever
        print("✅ Import successful")
        
        # Test initialization (will create default document store)
        retriever = Retriever()
        print("✅ Retriever initialization successful")
        
        # Test basic methods exist
        methods = ['retrieve', 'rerank', 'log_retrieval']
        for method in methods:
            if hasattr(retriever, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        return False

def test_logging_utils():
    """Test Logging Utils initialization and basic functionality"""
    print("\n🔍 Testing Logging Utils...")
    
    try:
        from RAG_pipeline.logging_utils import RetrievalLogger
        print("✅ Import successful")
        
        # Test initialization
        logger = RetrievalLogger()
        print("✅ Logger initialization successful")
        
        # Test basic methods exist
        methods = ['log']
        for method in methods:
            if hasattr(logger, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging Utils test failed: {e}")
        return False

def main():
    """Run all RAG Pipeline tests"""
    print("🚀 Starting RAG Pipeline Component Tests\n")
    
    results = []
    
    # Test both implementations
    results.append(test_haystack_rag_pipeline())
    results.append(test_chromadb_rag_pipeline())
    
    # Test individual components (these will test the original Haystack versions)
    results.append(test_chunking())
    results.append(test_indexing())
    results.append(test_retrieval())
    results.append(test_logging_utils())
    
    print(f"\n📊 RAG Pipeline Test Results: {sum(results)}/{len(results)} components passed")
    
    if all(results):
        print("🎉 All RAG Pipeline components are working!")
    else:
        print("⚠️  Some RAG Pipeline components need attention")
    
    # Show which implementations are working
    haystack_working = results[0]
    chromadb_working = results[1]
    
    print(f"\n🔍 Implementation Status:")
    print(f"   Haystack RAG Pipeline: {'✅ Working' if haystack_working else '❌ Not Working'}")
    print(f"   ChromaDB RAG Pipeline: {'✅ Working' if chromadb_working else '❌ Not Working'}")
    
    if chromadb_working:
        print("\n💡 Recommendation: Use ChromaDB RAG Pipeline (no version conflicts)")
    
    return all(results)

if __name__ == "__main__":
    main()
