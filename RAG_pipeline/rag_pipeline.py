import datetime
from typing import Any, List, Dict

from RAG_pipeline.chunking import Chunker
from RAG_pipeline.indexing import Indexer
from RAG_pipeline.retrieval import Retriever

import logging
logger = logging.getLogger(__name__)



class HaystackRAGPipeline:
    def __init__(self, document_store=None, embedding_model: str = "BAAI/bge-base-en"):
        """
        Initializes the RAG pipeline using modular classes for chunking, indexing, and retrieval.
        The retriever now includes integrated reranking functionality.
        """
        # Create document store if not provided
        if document_store is None:
            from haystack import FAISSDocumentStore
            document_store = FAISSDocumentStore(
                faiss_index_factory_str="Flat",
                embedding_dim=384  # BGE base embedding dimension
            )
        
        self.document_store = document_store
        self.retriever = Retriever(document_store, embedding_model)
        
        # Initialize chunker and indexer with proper references
        self.chunker = Chunker(document_store, self.retriever.retriever)
        self.indexer = Indexer(
            document_store, 
            self.retriever.retriever, 
            self.retriever.retriever.embedding_model, 
            self.retriever.reranker
        )

    def index_scraped_data(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        """Index scraped data using the indexer."""
        result = self.indexer.index_scraped_data(pydantic_results, structured_results)
        return result.get("message", f"Indexed {len(pydantic_results + structured_results)} documents")

    def index_api_data(self, api_results: List[Dict]):
        """Index API data using the indexer."""
        result = self.indexer.index_api_data(api_results)
        return result.get("message", f"Indexed {len(api_results)} API documents")

    def chunk_and_index(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        """Chunk and index data using the chunker."""
        result = self.chunker.chunk_and_index(pydantic_results, structured_results)
        return result.get("message", f"Chunked and indexed documents")

    def rerank_document_store(self, query: str, top_k_retrieval: int = 20, top_k_final: int = 5):
        """Retrieve and rerank documents using the integrated retriever functionality."""
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k_retrieval)
        # Convert Haystack Documents to dict format for reranking
        retrieved_dicts = []
        for doc in retrieved_docs:
            doc_dict = {
                "content": doc.content,
                "metadata": doc.meta
            }
            retrieved_dicts.append(doc_dict)
        
        reranked_docs = self.retriever.rerank(query, retrieved_dicts, top_k_final)
        return reranked_docs

    def log_retrieval(self, query: str, retrieved_docs: List[Dict], section: str = None):
        """Log retrieval operations using the integrated retriever functionality."""
        # Convert dict docs to the format expected by retriever.log_retrieval
        if retrieved_docs and hasattr(retrieved_docs[0], 'content'):
            # Already Haystack Documents
            self.retriever.log_retrieval(query, retrieved_docs, section)
        else:
            # Convert dict format to Haystack Documents for logging
            from haystack import Document
            haystack_docs = []
            for doc in retrieved_docs:
                content = (
                    doc.get('content', '')
                    or doc.get('markdown_blocks', '')
                    or doc.get('ocr_content', '')
                    or doc.get('model_card_details', '')
                )
                meta = doc.get('metadata', doc.get('meta', {}))
                haystack_docs.append(Document(content=content, meta=meta))
            
            self.retriever.log_retrieval(query, haystack_docs, section)

    def run(self, inputs: Dict[str, Any]) -> List[Dict]:
        """
        Standardized run method to be used by orchestrators.
        Performs chunking, indexing, retrieval, and reranking using integrated functionality.
        """
        query = inputs.get("query")
        documents = inputs.get("documents", [])
        section = inputs.get("section", "unknown")

        if not query or not documents:
            logger.warning("RAG run skipped due to missing query or documents.")
            return []

        try:
            # 1. Chunk and Index
            chunk_result = self.chunker.chunk_and_index([], documents)  # Empty pydantic_results, use documents as structured_results
            logger.info(f"Chunking result: {chunk_result}")

            # 2. Retrieve
            retrieved = self.retriever.retrieve(query, top_k=20)

            # 3. Rerank using integrated functionality
            # Convert Haystack Documents to dict format for reranking
            retrieved_dicts = []
            for doc in retrieved:
                doc_dict = {
                    "content": doc.content,
                    "metadata": doc.meta
                }
                retrieved_dicts.append(doc_dict)
            
            reranked = self.retriever.rerank(query, retrieved_dicts, top_k_final=5)

            # 4. Log
            self.log_retrieval(query, reranked, section)

            return reranked

        except Exception as e:
            logger.error(f"RAG pipeline run failed: {e}")
            return []