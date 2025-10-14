import logging
from haystack import PreProcessor, Document, BaseDocumentStore, BaseRetriever
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class Chunker:
    """
    Document chunker for RAG pipeline that processes scraped data and indexes it for retrieval.
    
    This class handles the preprocessing, chunking, and indexing of documents from various
    scrapers, specifically designed for Kaggle competition data.
    """
    
    def __init__(
        self, 
        document_store: BaseDocumentStore, 
        retriever: Optional[BaseRetriever] = None,
        split_length: int = 100,
        split_overlap: int = 20,
        target_sections: Optional[List[str]] = None
    ):
        """
        Initialize the chunker with document store and retriever.
        
        Args:
            document_store: Haystack document store for storing and retrieving documents
            retriever: Haystack retriever for generating embeddings and searching
            split_length: Maximum length of each chunk (default: 100)
            split_overlap: Overlap between chunks (default: 20)
            target_sections: List of sections to process (default: ["overview", "discussion"])
        
        Raises:
            TypeError: If document_store or retriever are not valid types
            ValueError: If parameters are invalid
            AttributeError: If required methods are not available
        """
        # Validate inputs
        if not isinstance(document_store, BaseDocumentStore):
            raise TypeError("document_store must be a BaseDocumentStore instance")
        if retriever is not None and not isinstance(retriever, BaseRetriever):
            raise TypeError("retriever must be a BaseRetriever instance or None")
        if not isinstance(split_length, int) or split_length <= 0:
            raise ValueError("split_length must be a positive integer")
        if not isinstance(split_overlap, int) or split_overlap < 0:
            raise ValueError("split_overlap must be a non-negative integer")
        if split_overlap >= split_length:
            raise ValueError("split_overlap must be less than split_length")
        
        # Validate required methods
        if not hasattr(document_store, 'write_documents'):
            raise AttributeError("document_store must have write_documents method")
        if not hasattr(document_store, 'update_embeddings'):
            raise AttributeError("document_store must have update_embeddings method")
        if retriever is not None and not hasattr(retriever, 'embed_documents'):
            raise AttributeError("retriever must have embed_documents method")
        
        self.document_store = document_store
        self.retriever = retriever
        self.target_sections = target_sections or ["overview", "discussion"]
        
        # Initialize preprocessor with error handling
        try:
            self.preprocessor = PreProcessor(
                split_by="sentence",
                split_length=split_length,
                split_overlap=split_overlap,
                clean_empty_lines=True,
                clean_whitespace=True,
                remove_substrings=None
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize PreProcessor: {e}")
        
        logger.info(f"Chunker initialized with split_length={split_length}, split_overlap={split_overlap}")

    def chunk_and_index(
        self, 
        pydantic_results: List[Dict[str, Any]], 
        structured_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process scraped data, chunk it, and index it for retrieval.
        
        Args:
            pydantic_results: List of documents from Pydantic-based scrapers
            structured_results: List of documents from structured scrapers
        
        Returns:
            Dict containing status information and results
            
        Raises:
            TypeError: If inputs are not lists
            ValueError: If document content is invalid
            RuntimeError: If processing or indexing fails
        """
        # Validate inputs
        if not isinstance(pydantic_results, list):
            raise TypeError("pydantic_results must be a list")
        if not isinstance(structured_results, list):
            raise TypeError("structured_results must be a list")
        
        try:
            # Combine results safely
            all_results = pydantic_results + structured_results
            target_sections_set = set(self.target_sections)
            
            # Filter documents by target sections with validation
            overview_and_discussion_docs = []
            for result in all_results:
                if not isinstance(result, dict):
                    logger.warning("Skipping non-dict result: %s", type(result).__name__)
                    continue
                
                section = result.get("section")
                if isinstance(section, str) and section in target_sections_set:
                    overview_and_discussion_docs.append(result)
            
            logger.info(f"Processing {len(overview_and_discussion_docs)} documents from target sections")
            
            chunks = []
            processed_count = 0
            error_count = 0
            
            for doc in overview_and_discussion_docs:
                try:
                    # Extract content safely
                    content = self._extract_content(doc)
                    if not content or not content.strip():
                        logger.debug("Skipping document with empty content")
                        continue
                    
                    # Build metadata safely
                    meta = self._build_metadata(doc)
                    
                    # Create haystack document
                    haystack_doc = {"content": content, "meta": meta}
                    
                    # Process with preprocessor
                    preprocessed = self._process_document(haystack_doc)
                    if preprocessed:
                        chunks.extend(preprocessed)
                        processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process document: {e}")
                    error_count += 1
                    continue
            
            # Index chunks if any were created
            if chunks:
                success = self._index_chunks(chunks)
                if success:
                    logger.info(f"Successfully chunked and indexed {len(chunks)} documents")
                    return {
                        "status": "success",
                        "chunks_created": len(chunks),
                        "documents_processed": processed_count,
                        "errors": error_count,
                        "message": f"Chunked and indexed {len(chunks)} documents"
                    }
                else:
                    return {
                        "status": "error",
                        "chunks_created": 0,
                        "documents_processed": processed_count,
                        "errors": error_count + 1,
                        "message": "Failed to index chunks"
                    }
            else:
                logger.warning("No chunks created for indexing")
                return {
                    "status": "warning",
                    "chunks_created": 0,
                    "documents_processed": processed_count,
                    "errors": error_count,
                    "message": "No chunks created for indexing"
                }
                
        except Exception as e:
            logger.error(f"Chunking and indexing failed: {e}")
            raise RuntimeError(f"Chunking and indexing failed: {e}")
    
    def _extract_content(self, doc: Dict[str, Any]) -> str:
        """Extract content from document with validation."""
        if not isinstance(doc, dict):
            raise TypeError("Document must be a dictionary")
        
        # Try different content sources in order of preference
        content_sources = ["content", "markdown_blocks", "ocr_content"]
        
        for source in content_sources:
            content = doc.get(source)
            if content and isinstance(content, str) and content.strip():
                return content.strip()
        
        return ""
    
    def _build_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata dictionary safely."""
        if not isinstance(doc, dict):
            raise TypeError("Document must be a dictionary")
        
        # Build standard metadata with safe access
        meta = {
            "section": str(doc.get("section", "unknown")),
            "source": self._determine_source(doc),
            "deep_scraped": bool(doc.get("deep_scraped", False)),
            "content_hash": str(doc.get("content_hash", "")),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields safely
        if "topic" in doc and doc["topic"]:
            meta["topic"] = str(doc["topic"])
        
        if "url" in doc and doc["url"]:
            meta["url"] = str(doc["url"])
        
        if "title" in doc and doc["title"]:
            meta["title"] = str(doc["title"])
        
        return meta
    
    def _determine_source(self, doc: Dict[str, Any]) -> str:
        """Determine source type based on document data."""
        if not isinstance(doc, dict):
            return "unknown"
        
        if doc.get("deep_scraped"):
            return "deep_scraped"
        elif doc.get("source"):
            return str(doc["source"])
        else:
            return "scraped"
    
    def _process_document(self, haystack_doc: Dict[str, Any]) -> List[Any]:
        """Process document with preprocessor safely."""
        try:
            preprocessed = self.preprocessor.process(documents=[haystack_doc])
            if not isinstance(preprocessed, list):
                logger.warning("Preprocessor returned non-list result")
                return []
            return preprocessed
        except Exception as e:
            logger.warning(f"Preprocessing failed: {e}")
            return []
    
    def _index_chunks(self, chunks: List[Any]) -> bool:
        """Index chunks with error handling."""
        try:
            # Validate chunks before writing
            if not isinstance(chunks, list):
                logger.error("Chunks must be a list")
                return False
            
            if not chunks:
                logger.warning("No chunks to index")
                return True
            
            # Write documents
            self.document_store.write_documents(chunks)
            
            # Update embeddings if retriever is available
            if self.retriever:
                self.document_store.update_embeddings(self.retriever)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index chunks: {e}")
            return False