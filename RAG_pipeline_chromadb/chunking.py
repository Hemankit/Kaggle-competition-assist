import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ChromaDBChunker:
    """
    Document chunker for ChromaDB RAG pipeline.
    
    Provides similar functionality to Haystack PreProcessor
    but works with ChromaDB and simple data structures.
    """
    
    def __init__(
        self, 
        embedding_model: SentenceTransformer,
        split_length: int = 100,
        split_overlap: int = 20,
        target_sections: Optional[List[str]] = None
    ):
        """
        Initialize the ChromaDB chunker.
        
        Args:
            embedding_model: Sentence transformer model for embeddings
            split_length: Maximum length of each chunk (in sentences)
            split_overlap: Overlap between chunks (in sentences)
            target_sections: List of sections to process
        """
        self.embedding_model = embedding_model
        self.split_length = split_length
        self.split_overlap = split_overlap
        self.target_sections = target_sections or ["overview", "discussion"]
        
        logger.info(f"ChromaDB Chunker initialized with split_length={split_length}, split_overlap={split_overlap}")

    def chunk_and_index(
        self, 
        pydantic_results: List[Dict[str, Any]], 
        structured_results: List[Dict[str, Any]],
        indexer
    ) -> Dict[str, Any]:
        """
        Process scraped data, chunk it, and index it for retrieval.
        
        Args:
            pydantic_results: List of documents from Pydantic-based scrapers
            structured_results: List of documents from structured scrapers
            indexer: ChromaDB indexer instance for indexing chunks
            
        Returns:
            Dict containing status information and results
        """
        try:
            # Combine results
            all_results = pydantic_results + structured_results
            target_sections_set = set(self.target_sections)
            
            # Filter documents by target sections
            filtered_docs = []
            for result in all_results:
                if not isinstance(result, dict):
                    logger.warning("Skipping non-dict result: %s", type(result).__name__)
                    continue
                
                section = result.get("section")
                if isinstance(section, str) and section in target_sections_set:
                    filtered_docs.append(result)
            
            logger.info(f"Processing {len(filtered_docs)} documents from target sections")
            
            chunks = []
            processed_count = 0
            error_count = 0
            
            for doc in filtered_docs:
                try:
                    # Extract content
                    content = self._extract_content(doc)
                    if not content or not content.strip():
                        logger.debug("Skipping document with empty content")
                        continue
                    
                    # Build metadata
                    meta = self._build_metadata(doc)
                    
                    # Create chunks
                    doc_chunks = self._create_chunks(content, meta)
                    if doc_chunks:
                        chunks.extend(doc_chunks)
                        processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process document: {e}")
                    error_count += 1
                    continue
            
            # Index chunks
            if chunks:
                success = indexer._index_chunks(chunks)
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
        """Extract content from document."""
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
        """Build metadata dictionary."""
        if not isinstance(doc, dict):
            raise TypeError("Document must be a dictionary")
        
        meta = {
            "section": str(doc.get("section", "unknown")),
            "source": self._determine_source(doc),
            "deep_scraped": bool(doc.get("deep_scraped", False)),
            "content_hash": str(doc.get("content_hash", "")),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields
        if "topic" in doc and doc["topic"]:
            meta["topic"] = str(doc["topic"])
        if "url" in doc and doc["url"]:
            meta["url"] = str(doc["url"])
        if "title" in doc and doc["title"]:
            meta["title"] = str(doc["title"])
        if "competition_slug" in doc and doc["competition_slug"]:
            meta["competition_slug"] = str(doc["competition_slug"])
        if "author" in doc and doc["author"]:
            meta["author"] = str(doc["author"])
        if "votes" in doc:
            meta["votes"] = int(doc["votes"]) if isinstance(doc["votes"], (int, float)) else 0
        if "is_pinned" in doc:
            meta["is_pinned"] = bool(doc["is_pinned"])
        if "notebook_ref" in doc and doc["notebook_ref"]:
            meta["notebook_ref"] = str(doc["notebook_ref"])
        
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

    def _create_chunks(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create chunks from content using simple sentence splitting."""
        try:
            # Split content into sentences
            sentences = self._split_into_sentences(content)
            
            if not sentences:
                return []
            
            chunks = []
            for i in range(0, len(sentences), self.split_length - self.split_overlap):
                chunk_sentences = sentences[i:i + self.split_length]
                chunk_content = " ".join(chunk_sentences)
                
                # Create chunk metadata
                chunk_meta = metadata.copy()
                chunk_meta["chunk_id"] = f"{metadata.get('content_hash', 'unknown')}_{i}"
                chunk_meta["chunk_index"] = i // (self.split_length - self.split_overlap)
                
                chunks.append({
                    "content": chunk_content,
                    "metadata": chunk_meta
                })
            
            return chunks
            
        except Exception as e:
            logger.warning(f"Failed to create chunks: {e}")
            return []

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple regex."""
        if not text:
            return []
        
        # Simple sentence splitting regex
        sentence_endings = r'[.!?]+'
        sentences = re.split(sentence_endings, text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Filter out very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
