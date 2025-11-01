"""
ChromaDB Inspector - Check what data is stored
"""

import sys
import os
sys.path.append('.')

import chromadb
from sentence_transformers import SentenceTransformer
from typing import Dict, Any
import json

def inspect_chromadb():
    """Inspect ChromaDB to see what data we have."""
    
    print("🔍 Inspecting ChromaDB...")
    print("=" * 80)
    
    try:
        # Initialize ChromaDB client
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        print("✅ Connected to ChromaDB")
        
        # List all collections
        collections = chroma_client.list_collections()
        print(f"\n📚 Found {len(collections)} collection(s):")
        
        if not collections:
            print("❌ No collections found! ChromaDB is EMPTY.")
            print("\n💡 Next steps:")
            print("   1. We need to populate ChromaDB with competition data")
            print("   2. Use scrapers to collect Kaggle competition data")
            print("   3. Index the data using ChromaDBRAGPipeline")
            return False
        
        # Inspect each collection
        for collection in collections:
            print(f"\n{'='*80}")
            print(f"📂 Collection: {collection.name}")
            print(f"{'='*80}")
            
            # Get collection stats
            count = collection.count()
            print(f"   📊 Total documents: {count}")
            
            if count == 0:
                print("   ⚠️  Collection is EMPTY!")
                continue
            
            # Get a sample of documents
            sample_size = min(5, count)
            results = collection.get(
                limit=sample_size,
                include=["documents", "metadatas"]
            )
            
            print(f"\n   📄 Sample Documents (showing {sample_size}):")
            print(f"   {'-'*76}")
            
            for i, (doc, metadata) in enumerate(zip(results["documents"], results["metadatas"])):
                print(f"\n   🔖 Document {i+1}:")
                
                # Show metadata
                print(f"      📋 Metadata:")
                for key, value in metadata.items():
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"         • {key}: {value}")
                
                # Show content snippet
                content_snippet = doc[:200].replace('\n', ' ') if len(doc) > 200 else doc
                print(f"      📝 Content: {content_snippet}...")
            
            # Analyze metadata to understand data distribution
            print(f"\n   📊 Data Distribution:")
            print(f"   {'-'*76}")
            
            # Get all metadata to analyze
            all_results = collection.get(include=["metadatas"])
            all_metadata = all_results["metadatas"]
            
            # Count by section
            sections = {}
            competitions = {}
            for metadata in all_metadata:
                section = metadata.get("section", "unknown")
                sections[section] = sections.get(section, 0) + 1
                
                comp = metadata.get("competition_slug", metadata.get("competition", "unknown"))
                competitions[comp] = competitions.get(comp, 0) + 1
            
            print(f"\n      📂 By Section:")
            for section, count in sorted(sections.items(), key=lambda x: x[1], reverse=True):
                print(f"         • {section}: {count} documents")
            
            print(f"\n      🏆 By Competition:")
            for comp, count in sorted(competitions.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"         • {comp}: {count} documents")
            
            if len(competitions) > 10:
                print(f"         ... and {len(competitions) - 10} more competitions")
        
        print(f"\n{'='*80}")
        print("✅ ChromaDB inspection complete!")
        print(f"{'='*80}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inspecting ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_retrieval():
    """Test retrieval with a sample query."""
    print("\n\n🧪 Testing Retrieval...")
    print("=" * 80)
    
    try:
        from RAG_pipeline_chromadb import ChromaDBRAGPipeline
        
        pipeline = ChromaDBRAGPipeline()
        print("✅ ChromaDB pipeline initialized")
        
        # Test queries
        test_queries = [
            "What is the evaluation metric for Titanic?",
            "machine learning techniques",
            "feature engineering"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            results = pipeline.rerank_document_store(query, top_k_retrieval=5, top_k_final=3)
            
            if results:
                print(f"   ✅ Retrieved {len(results)} documents")
                for i, doc in enumerate(results[:2]):
                    content = doc.get("content", "")[:150].replace('\n', ' ')
                    metadata = doc.get("metadata", {})
                    print(f"      {i+1}. {content}...")
                    print(f"         Section: {metadata.get('section', 'N/A')}")
            else:
                print(f"   ⚠️  No results found")
        
        print("\n✅ Retrieval test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 CHROMADB INSPECTION TOOL")
    print("="*80 + "\n")
    
    has_data = inspect_chromadb()
    
    if has_data:
        print("\n" + "="*80)
        test_retrieval()
    else:
        print("\n💡 RECOMMENDATION:")
        print("   ChromaDB is empty. We need to populate it with Kaggle competition data.")
        print("   This is expected for a fresh setup!")

