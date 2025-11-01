import datetime
from typing import Any, List, Dict
import logging

from .chunking import ChromaDBChunker
from .indexing import ChromaDBIndexer
from .retrieval import ChromaDBRetriever

logger = logging.getLogger(__name__)

class ChromaDBRAGPipeline:
    """
    ChromaDB-based RAG Pipeline - Alternative to Haystack implementation.
    
    Maintains the same interface and functionality as HaystackRAGPipeline
    but uses ChromaDB for vector storage and retrieval to avoid version conflicts.
    """
    
    def __init__(self, collection_name: str = "kaggle_competition_data", embedding_model: str = "all-mpnet-base-v2"):
        """
        Initialize the ChromaDB RAG pipeline.
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: Name of the sentence transformer model
        """
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            import os
            
            # Initialize ChromaDB client with persistence
            # Use parent directory of RAG_pipeline_chromadb (app root) for consistency
            app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_dir = os.path.join(app_root, "chroma_db")
            os.makedirs(persist_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            self.collection_name = collection_name
            logger.info(f"ChromaDB using persistent storage at: {persist_dir}")
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(embedding_model)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            
            # Initialize components
            self.retriever = ChromaDBRetriever(self.chroma_client, collection_name, self.embedding_model)
            self.chunker = ChromaDBChunker(self.embedding_model)
            self.indexer = ChromaDBIndexer(self.chroma_client, collection_name, self.embedding_model)
            
            logger.info(f"ChromaDB RAG Pipeline initialized with collection: {collection_name}")
            
        except ImportError as e:
            logger.error(f"Missing required packages: {e}")
            raise ImportError("Please install: pip install chromadb sentence-transformers")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB RAG Pipeline: {e}")
            raise

    def index_scraped_data(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        """Index scraped data using the ChromaDB indexer."""
        result = self.indexer.index_scraped_data(pydantic_results, structured_results)
        return result.get("message", f"Indexed {len(pydantic_results + structured_results)} documents")

    def index_api_data(self, api_results: List[Dict]):
        """Index API data using the ChromaDB indexer."""
        result = self.indexer.index_api_data(api_results)
        return result.get("message", f"Indexed {len(api_results)} API documents")

    def chunk_and_index(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        """Chunk and index data using the ChromaDB chunker."""
        result = self.chunker.chunk_and_index(pydantic_results, structured_results, self.indexer)
        return result.get("message", f"Chunked and indexed documents")

    def rerank_document_store(self, query: str, top_k_retrieval: int = 20, top_k_final: int = 5):
        """Retrieve and rerank documents using the ChromaDB retriever."""
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k_retrieval)
        reranked_docs = self.retriever.rerank(query, retrieved_docs, top_k_final)
        return reranked_docs

    def log_retrieval(self, query: str, retrieved_docs: List[Dict], section: str = None):
        """Log retrieval operations."""
        timestamp = datetime.datetime.now().isoformat()
        
        logger.info(f"[{timestamp}] ChromaDB Retrieval Log:")
        logger.info(f"🔍 Query: {query}")
        if section:
            logger.info(f"📂 Section: {section}")
        logger.info(f"📄 Retrieved {len(retrieved_docs)} documents.")

        for i, doc in enumerate(retrieved_docs[:5]):
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")
            logger.info(f"  📘 Document {i + 1}:")
            logger.info(f"    Metadata: {metadata}")
            snippet = content[:200].replace('\n', ' ') + "..." if len(content) > 200 else content
            logger.info(f"    Content Snippet: {snippet}")

    def run(self, inputs: Dict[str, Any]) -> List[Dict]:
        """
        Standardized run method - same interface as Haystack version.
        
        Args:
            inputs: Dictionary containing 'query', 'documents', 'section'
            
        Returns:
            List of retrieved and reranked documents
        """
        query = inputs.get("query")
        documents = inputs.get("documents", [])
        section = inputs.get("section", "unknown")

        if not query or not documents:
            logger.warning("ChromaDB RAG run skipped due to missing query or documents.")
            return []

        try:
            # 1. Chunk and Index
            chunk_result = self.chunker.chunk_and_index([], documents, self.indexer)
            logger.info(f"ChromaDB chunking result: {chunk_result}")

            # 2. Retrieve and Rerank
            retrieved = self.retriever.retrieve(query, top_k=20)
            reranked = self.retriever.rerank(query, retrieved, top_k_final=5)

            # 3. Log
            self.log_retrieval(query, reranked, section)

            return reranked

        except Exception as e:
            logger.error(f"ChromaDB RAG pipeline run failed: {e}")
            return []
