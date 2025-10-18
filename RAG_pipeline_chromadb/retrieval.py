import logging
from typing import List, Dict
import chromadb

logger = logging.getLogger(__name__)

class ChromaDBRetriever:
    """
    ChromaDB-based document retriever with reranking capabilities.
    
    Provides the same functionality as Haystack EmbeddingRetriever
    but uses ChromaDB for vector storage and retrieval.
    """
    
    def __init__(self, chroma_client: chromadb.Client, collection_name: str, embedding_model):
        """
        Initialize the ChromaDB retriever.
        
        Args:
            chroma_client: ChromaDB client instance
            collection_name: Name of the collection to query
            embedding_model: Sentence transformer model for embeddings
        """
        self.chroma_client = chroma_client
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize cross-encoder for reranking
        try:
            from sentence_transformers import CrossEncoder
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Cross-encoder reranker initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize reranker: {e}")
            self.reranker = None
        
        logger.info(f"ChromaDB Retriever initialized for collection: {collection_name}")

    def retrieve(self, query: str, top_k: int = 20, where: dict = None) -> List[Dict]:
        """
        Retrieve documents using ChromaDB similarity search.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            where: Optional metadata filter (e.g., {"section": "code", "competition_slug": "titanic"})
            
        Returns:
            List of retrieved documents with metadata
        """
        logger.info(f"Retrieving top {top_k} documents for query: {query} (filters: {where})")
        
        try:
            # Get or create collection
            collection = self._get_collection()
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Query the collection
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"]
            }
            if where:
                query_params["where"] = where
            
            results = collection.query(**query_params)
            
            # Format results
            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, doc_content in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                    distance = results["distances"][0][i] if results["distances"] and results["distances"][0] else 0
                    
                    retrieved_docs.append({
                        "content": doc_content,
                        "metadata": metadata,
                        "similarity_score": 1 - distance,  # Convert distance to similarity
                        "distance": distance
                    })
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"ChromaDB retrieval failed: {e}")
            return []

    def rerank(self, query: str, retrieved_docs: List[Dict], top_k_final: int = 5) -> List[Dict]:
        """
        Rerank retrieved documents using cross-encoder.
        
        Args:
            query: Original search query
            retrieved_docs: List of retrieved documents
            top_k_final: Number of final documents to return
            
        Returns:
            List of reranked documents
        """
        logger.info(f"Reranking top {len(retrieved_docs)} documents for query: {query}")
        
        if not self.reranker or not retrieved_docs:
            logger.warning("No reranker available or no documents to rerank")
            return retrieved_docs[:top_k_final]
        
        try:
            # Prepare query-document pairs for reranking
            query_doc_pairs = []
            for doc in retrieved_docs:
                content = doc.get("content", "")
                query_doc_pairs.append([query, content])
            
            # Get reranking scores
            rerank_scores = self.reranker.predict(query_doc_pairs)
            
            # Add scores to documents and sort
            for i, doc in enumerate(retrieved_docs):
                doc["rerank_score"] = float(rerank_scores[i])
            
            # Sort by rerank score (descending)
            reranked_docs = sorted(retrieved_docs, key=lambda x: x["rerank_score"], reverse=True)
            
            logger.info(f"Reranked {len(reranked_docs)} documents")
            return reranked_docs[:top_k_final]
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return retrieved_docs[:top_k_final]

    def _get_collection(self):
        """Get or create the ChromaDB collection."""
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            return collection
        except Exception:
            # Collection doesn't exist, create it
            logger.info(f"Creating new collection: {self.collection_name}")
            collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Kaggle competition data"}
            )
            return collection

    def log_retrieval(self, query: str, retrieved_docs: List[Dict], section: str = None):
        """Log retrieval operations for debugging."""
        import datetime
        timestamp = datetime.datetime.now().isoformat()

        logger.info(f"[{timestamp}] ChromaDB Retrieval Log:")
        logger.info(f"🔍 Query: {query}")
        if section:
            logger.info(f"📂 Section: {section}")
        logger.info(f"📄 Retrieved {len(retrieved_docs)} documents.")

        for i, doc in enumerate(retrieved_docs[:5]):
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")
            similarity = doc.get("similarity_score", 0)
            rerank_score = doc.get("rerank_score", 0)
            
            logger.info(f"  📘 Document {i + 1}:")
            logger.info(f"    Similarity: {similarity:.4f}")
            if rerank_score:
                logger.info(f"    Rerank Score: {rerank_score:.4f}")
            logger.info(f"    Metadata: {metadata}")
            snippet = content[:200].replace('\n', ' ') + "..." if len(content) > 200 else content
            logger.info(f"    Content Snippet: {snippet}")
