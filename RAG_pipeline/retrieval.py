from haystack.nodes import EmbeddingRetriever, SentenceTransformersRanker
from typing import List
import logging

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, document_store, embedding_model: str = "BAAI/bge-base-en"):
        self.document_store = document_store

        # Embedding-based retriever
        self.retriever = EmbeddingRetriever(
            document_store=self.document_store,
            embedding_model=embedding_model,
            model_format="sentence_transformers",
            use_gpu=True
        )

        # Optional reranker
        self.reranker = SentenceTransformersRanker(
            model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2",
            use_gpu=True
        )

    def retrieve(self, query: str, top_k: int = 20):
        logger.info(f"Retrieving top {top_k} documents for query: {query}")
        return self.retriever.retrieve(query=query, top_k=top_k)

    def rerank(self, query: str, retrieved_docs: List[dict], top_k_final: int = 5):
        logger.info(f"Reranking top {len(retrieved_docs)} documents for query: {query}")
        reranked = self.reranker.predict(query=query, documents=retrieved_docs)
        return reranked[:top_k_final]

    def log_retrieval(self, query: str, retrieved_docs: List[dict], section: str = None):
        import datetime
        timestamp = datetime.datetime.now().isoformat()

        logger.info(f"[{timestamp}] Retrieval Log:")
        logger.info(f"🔍 Query: {query}")
        if section:
            logger.info(f"📂 Section: {section}")
        logger.info(f"📄 Retrieved {len(retrieved_docs)} documents.")

        for i, doc in enumerate(retrieved_docs[:5]):
            logger.info(f"  📘 Document {i + 1}:")
            logger.info(f"    Metadata: {doc.meta}")
            snippet = doc.content[:200].replace('\n', ' ') + "..."
            logger.info(f"    Content Snippet: {snippet}")
