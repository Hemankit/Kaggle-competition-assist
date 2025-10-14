"""
ChromaDB-based RAG Pipeline for Kaggle Competition Assist.

This is an alternative implementation using ChromaDB instead of Haystack
to avoid version conflicts while maintaining the same architecture and functionality.

Components:
- rag_pipeline.py: Main orchestrator (ChromaDBRAGPipeline)
- chunking.py: Document chunking and preprocessing
- indexing.py: Document indexing and embedding generation
- retrieval.py: Document retrieval and reranking
- logging_utils.py: Logging utilities (shared with Haystack version)
"""

from .rag_pipeline import ChromaDBRAGPipeline
from .chunking import ChromaDBChunker
from .indexing import ChromaDBIndexer
from .retrieval import ChromaDBRetriever

__all__ = [
    "ChromaDBRAGPipeline",
    "ChromaDBChunker", 
    "ChromaDBIndexer",
    "ChromaDBRetriever"
]

