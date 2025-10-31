"""
RAG Adapter - Connects Intelligent Router with ChromaDB RAG Pipeline
Converts intelligent router output to ChromaDB RAG input format.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional
import logging

# Import our components
from intelligent_router import IntelligentRouter

# Import ChromaDB RAG Pipeline
try:
    from RAG_pipeline_chromadb import ChromaDBRAGPipeline
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: ChromaDB RAG Pipeline not available")

logger = logging.getLogger(__name__)

class RAGAdapter:
    """
    Adapter that connects Intelligent Router with ChromaDB RAG Pipeline.
    Handles data format conversion and pipeline orchestration.
    """

    def __init__(self, google_api_key: Optional[str] = None):
        self.intelligent_router = IntelligentRouter(google_api_key)
        self.rag_pipeline = self._initialize_rag_pipeline()
        self.conversation_history = []

    def _initialize_rag_pipeline(self):
        """Initialize ChromaDB RAG Pipeline."""
        if RAG_AVAILABLE:
            try:
                pipeline = ChromaDBRAGPipeline(
                    collection_name="kaggle_competition_data",
                    embedding_model="all-MiniLM-L6-v2"
                )
                print("✅ ChromaDB RAG Pipeline initialized")
                return pipeline
            except Exception as e:
                print(f"Warning: Could not initialize RAG pipeline: {e}")
                return None
        else:
            print("Warning: RAG pipeline not available")
            return None

    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete pipeline: Query → Intelligent Router → ChromaDB RAG → Response
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Complete processing result with RAG retrieval
        """
        if context is None:
            context = {}
            
        logger.info(f"RAG Adapter: Processing query '{query}'")
        
        try:
            # Step 1: Intelligent Router - Data Collection
            router_result = self.intelligent_router.process_query(query, context)
            
            if not router_result.get('ready_for_agent_router', False):
                return {
                    "query": query,
                    "context": context,
                    "error": "Intelligent router failed",
                    "router_result": router_result,
                    "rag_result": None,
                    "ready_for_response": False
                }
            
            # Step 2: Convert data for RAG pipeline
            rag_input = self._convert_for_rag(router_result, query)
            
            # Step 3: RAG Pipeline - Retrieval and Reranking
            rag_result = self._run_rag_pipeline(rag_input, query)
            
            # Step 4: Combine results
            combined_result = self._combine_results(router_result, rag_result, query, context)
            
            # Step 5: Update conversation history
            self._update_conversation_history(query, combined_result)
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Error in RAG adapter: {e}")
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "ready_for_response": False
            }

    def _convert_for_rag(self, router_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Convert intelligent router output to RAG pipeline input format."""
        collected_data = router_result.get('collected_data', {})
        data = collected_data.get('data', {})
        
        # Extract documents from all sources
        documents = []
        
        for source, source_data in data.items():
            items = source_data.get('items', [])
            for item in items:
                # Create document in RAG pipeline format
                document = {
                    'content': self._extract_content(item),
                    'metadata': {
                        'source': source,
                        'type': source_data.get('type', 'unknown'),
                        'title': item.get('title', ''),
                        'query': query,
                        'timestamp': item.get('timestamp', ''),
                        'original_item': item  # Keep original for reference
                    }
                }
                documents.append(document)
        
        return {
            'query': query,
            'documents': documents,
            'section': router_result.get('context', {}).get('section', 'general')
        }

    def _extract_content(self, item: Dict[str, Any]) -> str:
        """Extract content from item for RAG processing."""
        # Try different content fields
        content_fields = ['content', 'markdown_blocks', 'ocr_content', 'model_card_details', 'description']
        
        for field in content_fields:
            content = item.get(field)
            if content and isinstance(content, str) and content.strip():
                return content.strip()
        
        # Fallback to title if no content
        title = item.get('title', '')
        if title:
            return f"Title: {title}"
        
        return "No content available"

    def _run_rag_pipeline(self, rag_input: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Run the ChromaDB RAG pipeline."""
        if not self.rag_pipeline:
            return {
                "success": False,
                "error": "RAG pipeline not available",
                "retrieved_docs": []
            }
        
        try:
            # Run RAG pipeline
            retrieved_docs = self.rag_pipeline.run(rag_input)
            
            return {
                "success": True,
                "retrieved_docs": retrieved_docs,
                "count": len(retrieved_docs)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                "success": False,
                "error": str(e),
                "retrieved_docs": []
            }

    def _combine_results(self, router_result: Dict[str, Any], rag_result: Dict[str, Any], 
                        query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Combine intelligent router and RAG results."""
        return {
            "query": query,
            "context": context,
            "data_collection": {
                "sources_used": router_result.get('data_sources', []),
                "reasoning": router_result.get('reasoning', ''),
                "chromadb_stored": router_result.get('chromadb_stored', False),
                "total_items_collected": router_result.get('collected_data', {}).get('metadata', {}).get('total_items', 0)
            },
            "rag_retrieval": {
                "success": rag_result.get('success', False),
                "retrieved_count": rag_result.get('count', 0),
                "retrieved_docs": rag_result.get('retrieved_docs', []),
                "error": rag_result.get('error')
            },
            "ready_for_response": True,
            "timestamp": router_result.get('timestamp', ''),
            "conversation_id": len(self.conversation_history)
        }

    def _update_conversation_history(self, query: str, result: Dict[str, Any]) -> None:
        """Update conversation history for context."""
        self.conversation_history.append({
            "query": query,
            "result": result,
            "timestamp": result.get('timestamp', '')
        })

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history

    def clear_conversation_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def search_rag_database(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search the RAG database directly."""
        if not self.rag_pipeline:
            return {"error": "RAG pipeline not available"}
        
        try:
            # Use the retriever directly
            retrieved = self.rag_pipeline.retriever.retrieve(query, top_k=n_results)
            return {
                "success": True,
                "results": retrieved,
                "count": len(retrieved)
            }
        except Exception as e:
            logger.error(f"Error searching RAG database: {e}")
            return {"error": str(e)}

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of both components."""
        return {
            "intelligent_router": {
                "available": True,
                "llm_available": hasattr(self.intelligent_router.llm, 'invoke'),
                "scrapers_available": len(self.intelligent_router.scrapers) > 0,
                "chromadb_available": self.intelligent_router.chromadb_client is not None
            },
            "rag_pipeline": {
                "available": self.rag_pipeline is not None,
                "collection_name": self.rag_pipeline.collection_name if self.rag_pipeline else None
            },
            "conversation_history": {
                "length": len(self.conversation_history),
                "last_query": self.conversation_history[-1]["query"] if self.conversation_history else None
            }
        }


