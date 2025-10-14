import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set, Union

from haystack import Document, FAISSDocumentStore, EmbeddingRetriever
from haystack.nodes import SentenceTransformersRanker
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class Indexer:
    """
    Document indexer for RAG pipeline that handles document storage, embedding generation, and retrieval logging.
    
    This class manages indexing of scraped data, API data, and provides logging functionality
    for retrieval operations in a multi-agent system processing Kaggle competition data.
    """
    
    def __init__(
        self, 
        document_store: FAISSDocumentStore, 
        retriever: Optional[EmbeddingRetriever] = None, 
        embedding_model: Optional[SentenceTransformer] = None, 
        reranker: Optional[SentenceTransformersRanker] = None
    ) -> None:
        """
        Initialize the indexer with document store, retriever, embedding model, and reranker.
        
        Args:
            document_store: Document store for storing and retrieving documents
            retriever: Retriever for generating embeddings and searching
            embedding_model: Model for generating embeddings
            reranker: Model for reranking retrieved documents
        
        Raises:
            TypeError: If any parameter is not the expected type
            AttributeError: If required methods are not available on components
            ValueError: If components are not properly initialized
        """
        # Validate inputs
        if not isinstance(document_store, FAISSDocumentStore):
            raise TypeError("document_store must be a FAISSDocumentStore instance")
        if retriever is not None and not isinstance(retriever, EmbeddingRetriever):
            raise TypeError("retriever must be an EmbeddingRetriever instance or None")
        if embedding_model is not None and not isinstance(embedding_model, SentenceTransformer):
            raise TypeError("embedding_model must be a SentenceTransformer instance or None")
        if reranker is not None and not isinstance(reranker, SentenceTransformersRanker):
            raise TypeError("reranker must be a SentenceTransformersRanker instance or None")
        
        # Validate required methods
        if not hasattr(document_store, 'write_documents'):
            raise AttributeError("document_store must have write_documents method")
        if not hasattr(document_store, 'update_embeddings'):
            raise AttributeError("document_store must have update_embeddings method")
        if embedding_model is not None and not hasattr(embedding_model, 'encode'):
            raise AttributeError("embedding_model must have encode method")
        
        self.document_store = document_store
        self.retriever = retriever
        self.embedding_model = embedding_model
        self.reranker = reranker
        # Use proper type annotation for indexed hashes
        self.indexed_hashes: Set[str] = set()
        
        logger.info("Indexer initialized successfully")

    def index_scraped_data(
        self, 
        pydantic_results: List[Dict[str, Any]], 
        structured_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Index scraped data from different sources, handling deduplication and metadata creation.
        
        Args:
            pydantic_results: List of documents from Pydantic-based scrapers
            structured_results: List of documents from structured scrapers
        
        Returns:
            Dict containing status information and results
            
        Raises:
            TypeError: If inputs are not lists or contain invalid data types
            ValueError: If document content is invalid or empty
            RuntimeError: If document store operations fail
        """
        # Validate inputs
        if not isinstance(pydantic_results, list):
            raise TypeError("pydantic_results must be a list")
        if not isinstance(structured_results, list):
            raise TypeError("structured_results must be a list")
        
        try:
            documents_to_index: List[Document] = []
            # Use a set to track indexed hashes (in-memory, could be persisted)
            indexed_hashes: Set[str] = set(self.indexed_hashes)
            
            processed_count = 0
            error_count = 0
            
            # Process pydantic results
            for result in pydantic_results:
                try:
                    doc = self._create_document(result, "scraped", indexed_hashes)
                    if doc:
                        documents_to_index.append(doc)
                        processed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process pydantic result: {e}")
                    error_count += 1
                    continue
            
            # Process structured results
            for result in structured_results:
                try:
                    doc = self._create_document(result, "deep_scraped", indexed_hashes)
                    if doc:
                        documents_to_index.append(doc)
                        processed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process structured result: {e}")
                    error_count += 1
                    continue
            
            # Update indexed hashes
            self.indexed_hashes.update(indexed_hashes)
            
            # Index documents if any were created
            if documents_to_index:
                success = self._index_documents(documents_to_index)
                if success:
                    logger.info(f"Successfully indexed {len(documents_to_index)} documents")
                    return {
                        "status": "success",
                        "documents_indexed": len(documents_to_index),
                        "documents_processed": processed_count,
                        "errors": error_count,
                        "message": f"Indexed {len(documents_to_index)} documents"
                    }
                else:
                    return {
                        "status": "error",
                        "documents_indexed": 0,
                        "documents_processed": processed_count,
                        "errors": error_count + 1,
                        "message": "Failed to index documents"
                    }
            else:
                logger.warning("No documents to index")
                return {
                    "status": "warning",
                    "documents_indexed": 0,
                    "documents_processed": processed_count,
                    "errors": error_count,
                    "message": "No documents to index"
                }
                
        except Exception as e:
            logger.error(f"Indexing scraped data failed: {e}")
            raise RuntimeError(f"Indexing scraped data failed: {e}")
    
    def _create_document(
        self, 
        item: Dict[str, Any], 
        source_type: str, 
        indexed_hashes: Set[str]
    ) -> Optional[Document]:
        """Create a document from item data with validation and deduplication."""
        if not isinstance(item, dict):
            raise TypeError("Item must be a dictionary")
        if not isinstance(source_type, str):
            raise TypeError("Source type must be a string")
        
        try:
            # Extract content safely
            content = self._extract_content(item)
            if not content or not content.strip():
                logger.debug("Skipping item with empty content")
                return None
            
            # Generate or get content hash
            content_hash = self._get_content_hash(item, content)
            
            # Skip if already indexed
            if content_hash in indexed_hashes:
                logger.debug("Skipping duplicate content")
                return None
            
            indexed_hashes.add(content_hash)
            
            # Build metadata safely
            metadata = self._build_metadata(item, source_type, content_hash)
            
            # Create document
            return Document(content=content, meta=metadata)
            
        except Exception as e:
            logger.warning(f"Failed to create document: {e}")
            return None
    
    def _extract_content(self, item: Dict[str, Any]) -> str:
        """Extract content from item with validation."""
        if not isinstance(item, dict):
            raise TypeError("Item must be a dictionary")
        
        # Try different content sources in order of preference
        content_sources = ["content", "markdown_blocks", "ocr_content", "model_card_details"]
        
        for source in content_sources:
            content = item.get(source)
            if content and isinstance(content, str) and content.strip():
                return content.strip()
        
        return ""
    
    def _get_content_hash(self, item: Dict[str, Any], content: str) -> str:
        """Get or generate content hash for deduplication."""
        if not isinstance(item, dict):
            raise TypeError("Item must be a dictionary")
        if not isinstance(content, str):
            raise TypeError("Content must be a string")
        
        # Try to get existing hash
        content_hash = item.get("content_hash")
        if content_hash and isinstance(content_hash, str) and content_hash.strip():
            return content_hash.strip()
        
        # Generate hash if missing
        try:
            title = str(item.get("title", ""))
            url = str(item.get("url", ""))
            raw_for_hash = f"{title}|{url}|{content}"
            return hashlib.sha256(raw_for_hash.encode("utf-8")).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to generate content hash: {e}")
            # Fallback to content-only hash
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def _build_metadata(self, item: Dict[str, Any], source_type: str, content_hash: str) -> Dict[str, Any]:
        """Build metadata dictionary safely."""
        if not isinstance(item, dict):
            raise TypeError("Item must be a dictionary")
        if not isinstance(source_type, str):
            raise TypeError("Source type must be a string")
        if not isinstance(content_hash, str):
            raise TypeError("Content hash must be a string")
        
        metadata = {
            "content_hash": content_hash,
            "source": source_type,
            "section": str(item.get("section", "unknown")),
            "deep_scraped": bool(item.get("deep_scraped", False)),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields safely
        if "topic" in item and item["topic"]:
            metadata["topic"] = str(item["topic"])
        
        if "url" in item and item["url"]:
            metadata["url"] = str(item["url"])
        
        if "title" in item and item["title"]:
            metadata["title"] = str(item["title"])
        
        return metadata
    
    def _index_documents(self, documents: List[Document]) -> bool:
        """Index documents with error handling."""
        try:
            if not isinstance(documents, list):
                logger.error("Documents must be a list")
                return False
            
            if not documents:
                logger.warning("No documents to index")
                return True
            
            # Write documents
            self.document_store.write_documents(documents)
            
            # Update embeddings if retriever is available
            if self.retriever:
                self.document_store.update_embeddings(
                    self.retriever,
                    filters={"source": ["scraped", "deep_scraped"]}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            return False

    def index_api_data(self, api_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Index data from API sources with pre-computed embeddings.
        
        Args:
            api_results: List of API data to be indexed
        
        Returns:
            Dict containing status information and results
            
        Raises:
            TypeError: If input is not a list or contains invalid data types
            ValueError: If content is invalid or empty
            RuntimeError: If document store operations fail
        """
        # Validate inputs
        if not isinstance(api_results, list):
            raise TypeError("api_results must be a list")
        
        try:
            documents_to_index: List[Document] = []
            processed_count = 0
            error_count = 0
            
            for api_data in api_results:
                try:
                    if not isinstance(api_data, dict):
                        logger.warning("Skipping non-dict API data: %s", type(api_data).__name__)
                        error_count += 1
                        continue
                    
                    # Extract content safely
                    api_content = self._extract_api_content(api_data)
                    if not api_content:
                        logger.debug("Skipping API data with empty content")
                        continue
                    
                    # Generate embedding safely
                    embedding = self._generate_embedding(api_content)
                    if embedding is None:
                        logger.warning("Failed to generate embedding for API content")
                        error_count += 1
                        continue
                    
                    # Build metadata safely
                    metadata = self._build_api_metadata(api_data)
                    
                    # Create document
                    doc = Document(content=api_content, embedding=embedding, meta=metadata)
                    documents_to_index.append(doc)
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process API data: {e}")
                    error_count += 1
                    continue
            
            # Index documents if any were created
            if documents_to_index:
                success = self._index_documents(documents_to_index)
                if success:
                    logger.info(f"Successfully indexed {len(documents_to_index)} API documents")
                    return {
                        "status": "success",
                        "documents_indexed": len(documents_to_index),
                        "documents_processed": processed_count,
                        "errors": error_count,
                        "message": f"Indexed {len(documents_to_index)} API documents"
                    }
                else:
                    return {
                        "status": "error",
                        "documents_indexed": 0,
                        "documents_processed": processed_count,
                        "errors": error_count + 1,
                        "message": "Failed to index API documents"
                    }
            else:
                logger.warning("No API documents to index")
                return {
                    "status": "warning",
                    "documents_indexed": 0,
                    "documents_processed": processed_count,
                    "errors": error_count,
                    "message": "No API documents to index"
                }
                
        except Exception as e:
            logger.error(f"Indexing API data failed: {e}")
            raise RuntimeError(f"Indexing API data failed: {e}")
    
    def _extract_api_content(self, api_data: Dict[str, Any]) -> str:
        """Extract content from API data with validation."""
        if not isinstance(api_data, dict):
            raise TypeError("API data must be a dictionary")
        
        content = api_data.get("content", "")
        if not isinstance(content, str):
            logger.warning("API content is not a string, converting")
            content = str(content)
        
        return content.strip() if content else ""
    
    def _generate_embedding(self, content: str) -> Optional[List[float]]:
        """Generate embedding for content with error handling."""
        if not isinstance(content, str):
            raise TypeError("Content must be a string")
        
        if not content.strip():
            return None
        
        if not self.embedding_model:
            logger.warning("No embedding model available")
            return None
            
        try:
            embedding = self.embedding_model.encode(content)
            if not isinstance(embedding, (list, tuple)) or len(embedding) == 0:
                logger.warning("Invalid embedding generated")
                return None
            return list(embedding) if isinstance(embedding, tuple) else embedding
        except Exception as e:
            logger.warning(f"Failed to generate embedding: {e}")
            return None
    
    def _build_api_metadata(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata for API data safely."""
        if not isinstance(api_data, dict):
            raise TypeError("API data must be a dictionary")
        
        metadata = {
            "source": "api",
            "section": str(api_data.get("section", "unknown")),
            "deep_scraped": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields safely
        if "topic" in api_data and api_data["topic"]:
            metadata["topic"] = str(api_data["topic"])
        
        if "url" in api_data and api_data["url"]:
            metadata["url"] = str(api_data["url"])
        
        if "title" in api_data and api_data["title"]:
            metadata["title"] = str(api_data["title"])
        
        return metadata

    def log_retrieval(
        self, 
        query: str, 
        retrieved_docs: List[Document], 
        section: Optional[str] = None
    ) -> None:
        """
        Log retrieval operations for debugging and monitoring.
        
        Args:
            query: Search query that was executed
            retrieved_docs: List of retrieved documents
            section: Section filter that was applied (optional)
        
        Raises:
            TypeError: If parameters are not the expected types
            AttributeError: If document objects don't have expected attributes
        """
        # Validate inputs
        if not isinstance(query, str):
            raise TypeError("Query must be a string")
        if not isinstance(retrieved_docs, list):
            raise TypeError("Retrieved docs must be a list")
        if section is not None and not isinstance(section, str):
            raise TypeError("Section must be a string or None")
        
        try:
            # Use timezone-aware datetime
            timestamp = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"[{timestamp}] Retrieval Log:")
            logger.info(f"🔍 Query: {query}")
            if section:
                logger.info(f"📂 Section: {section}")
            logger.info(f"📄 Retrieved {len(retrieved_docs)} documents.")
            
            # Log document details safely
            for i, doc in enumerate(retrieved_docs[:5]):
                try:
                    logger.info(f"  📘 Document {i + 1}:")
                    
                    # Safe metadata access
                    if hasattr(doc, 'meta') and doc.meta:
                        logger.info(f"    Metadata: {doc.meta}")
                    else:
                        logger.info("    Metadata: None")
                    
                    # Safe content access
                    if hasattr(doc, 'content') and doc.content:
                        content = str(doc.content)
                        # Safe string operations
                        if len(content) > 200:
                            snippet = content[:200].replace('\n', ' ') + "..."
                        else:
                            snippet = content.replace('\n', ' ')
                        logger.info(f"    Content Snippet: {snippet}")
                    else:
                        logger.info("    Content Snippet: None")
                        
                except Exception as e:
                    logger.warning(f"Failed to log document {i + 1}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to log retrieval: {e}")
            # Don't raise exception for logging failures