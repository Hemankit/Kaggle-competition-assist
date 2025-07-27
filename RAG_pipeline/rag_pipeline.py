import datetime
from typing import List, Dict


from RAG_pipeline.chunking import Chunker
from RAG_pipeline.indexing import Indexer
from RAG_pipeline.reranking import Reranker
from RAG_pipeline.retrieval import Retriever

import logging
logger = logging.getLogger(__name__)



class HaystackRAGPipeline:
    def __init__(self, index_name="kaggle_index"):
        """
        Initializes the RAG pipeline using modular classes for chunking, indexing, retrieval, and reranking.
        """
        self.chunker = Chunker()
        self.indexer = Indexer(index_name=index_name)
        self.retriever = Retriever(index_name=index_name)
        self.reranker = Reranker()
        self.indexed_hashes = set()

    def index_scraped_data(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        all_results = pydantic_results + structured_results
        self.indexer.index(all_results)
        return f"Successfully indexed {len(all_results)} documents."

    def index_api_data(self, api_results: List[Dict]):
        self.indexer.index(api_results)
        return f"Successfully indexed {len(api_results)} API documents."

    def chunk_and_index(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        all_results = pydantic_results + structured_results
        chunks = self.chunker.chunk(all_results)
        self.indexer.index(chunks)
        return f"Successfully chunked and indexed {len(chunks)} documents."

    def rerank_document_store(self, query: str, top_k_retrieval: int = 20, top_k_final: int = 5):
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k_retrieval)
        reranked_docs = self.reranker.rerank(query, retrieved_docs)
        return reranked_docs[:top_k_final]

    def log_retrieval(self, query: str, retrieved_docs: List[Dict], section: str = None):
        timestamp = datetime.datetime.now().isoformat()
        logger.info(f"[{timestamp}] Retrieval Log:")
        logger.info(f"🔍 Query: {query}")
        if section:
            logger.info(f"📂 Section: {section}")
        logger.info(f"📄 Retrieved {len(retrieved_docs)} documents.")
        for i, doc in enumerate(retrieved_docs[:5]):
            logger.info(f"  📘 Document {i + 1}:")
            meta = doc.get('metadata', doc.get('meta', {}))
            logger.info(f"    Metadata: {meta}")
            content = (
                doc.get('content', '')
                or doc.get('markdown_blocks', '')
                or doc.get('ocr_content', '')
                or doc.get('model_card_details', '')
            )
            snippet = content[:200].replace('\n', ' ') + "..."
            logger.info(f"    Content Snippet: {snippet}")