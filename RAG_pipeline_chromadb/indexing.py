import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ChromaDBIndexer:
    """
    ChromaDB-based document indexer.
    
    Provides similar functionality to Haystack Indexer
    but uses ChromaDB for document storage and embedding generation.
    """
    
    def __init__(
        self, 
        chroma_client: chromadb.Client,
        collection_name: str,
        embedding_model: SentenceTransformer
    ):
        """
        Initialize the ChromaDB indexer.
        
        Args:
            chroma_client: ChromaDB client instance
            collection_name: Name of the collection to store documents
            embedding_model: Sentence transformer model for embeddings
        """
        self.chroma_client = chroma_client
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.indexed_hashes: Set[str] = set()
        
        logger.info("ChromaDB Indexer initialized successfully")

    def index_scraped_data(
        self, 
        pydantic_results: List[Dict[str, Any]], 
        structured_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Index scraped data from different sources.
        
        Args:
            pydantic_results: List of documents from Pydantic-based scrapers
            structured_results: List of documents from structured scrapers
        
        Returns:
            Dict containing status information and results
        """
        try:
            documents_to_index: List[Dict[str, Any]] = []
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
            
            # Index documents
            if documents_to_index:
                success = self._index_chunks(documents_to_index)
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

    def index_api_data(self, api_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Index data from API sources.
        
        Args:
            api_results: List of API data to be indexed
        
        Returns:
            Dict containing status information and results
        """
        try:
            documents_to_index: List[Dict[str, Any]] = []
            processed_count = 0
            error_count = 0
            
            for api_data in api_results:
                try:
                    if not isinstance(api_data, dict):
                        logger.warning("Skipping non-dict API data: %s", type(api_data).__name__)
                        error_count += 1
                        continue
                    
                    # Extract content
                    api_content = self._extract_api_content(api_data)
                    if not api_content:
                        logger.debug("Skipping API data with empty content")
                        continue
                    
                    # Build metadata
                    metadata = self._build_api_metadata(api_data)
                    
                    # Create document
                    doc = {
                        "content": api_content,
                        "metadata": metadata
                    }
                    documents_to_index.append(doc)
                    processed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process API data: {e}")
                    error_count += 1
                    continue
            
            # Index documents
            if documents_to_index:
                success = self._index_chunks(documents_to_index)
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

    def _create_document(
        self, 
        item: Dict[str, Any], 
        source_type: str, 
        indexed_hashes: Set[str]
    ) -> Optional[Dict[str, Any]]:
        """Create a document from item data with deduplication."""
        try:
            # Extract content
            content = self._extract_content(item)
            if not content or not content.strip():
                logger.debug("Skipping item with empty content")
                return None
            
            # Generate content hash
            content_hash = self._get_content_hash(item, content)
            
            # Skip if already indexed
            if content_hash in indexed_hashes:
                logger.debug("Skipping duplicate content")
                return None
            
            indexed_hashes.add(content_hash)
            
            # Build metadata
            metadata = self._build_metadata(item, source_type, content_hash)
            
            # Create document
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.warning(f"Failed to create document: {e}")
            return None

    def _extract_content(self, item: Dict[str, Any]) -> str:
        """Extract content from item."""
        content_sources = ["content", "markdown_blocks", "ocr_content", "model_card_details"]
        
        for source in content_sources:
            content = item.get(source)
            if content and isinstance(content, str) and content.strip():
                return content.strip()
        
        return ""

    def _get_content_hash(self, item: Dict[str, Any], content: str) -> str:
        """Get or generate content hash for deduplication."""
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
            return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _build_metadata(self, item: Dict[str, Any], source_type: str, content_hash: str) -> Dict[str, Any]:
        """Build metadata dictionary."""
        metadata = {
            "content_hash": content_hash,
            "source": source_type,
            "section": str(item.get("section", "unknown")),
            "deep_scraped": bool(item.get("deep_scraped", False)),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields
        if "topic" in item and item["topic"]:
            metadata["topic"] = str(item["topic"])
        if "url" in item and item["url"]:
            metadata["url"] = str(item["url"])
        if "title" in item and item["title"]:
            metadata["title"] = str(item["title"])
        
        # Add notebook-specific fields
        if "competition_slug" in item and item["competition_slug"]:
            metadata["competition_slug"] = str(item["competition_slug"])
        if "notebook_path" in item and item["notebook_path"]:
            metadata["notebook_path"] = str(item["notebook_path"])
        if "author" in item and item["author"]:
            metadata["author"] = str(item["author"])
        if "votes" in item:
            metadata["votes"] = int(item["votes"]) if isinstance(item["votes"], (int, float)) else 0
        if "category" in item and item["category"]:
            metadata["category"] = str(item["category"])
        
        # Add discussion-specific fields
        if "discussion_id" in item and item["discussion_id"]:
            metadata["discussion_id"] = str(item["discussion_id"])
        if "date" in item and item["date"]:
            metadata["date"] = str(item["date"])
        if "is_pinned" in item:
            metadata["is_pinned"] = bool(item["is_pinned"])
        if "comment_count" in item:
            metadata["comment_count"] = int(item["comment_count"]) if isinstance(item["comment_count"], (int, float)) else 0
        if "upvotes" in item and item["upvotes"] is not None:
            metadata["upvotes"] = int(item["upvotes"]) if isinstance(item["upvotes"], (int, float)) else 0
        if "author_rank" in item and item["author_rank"]:
            metadata["author_rank"] = str(item["author_rank"])
        if "post_hash" in item and item["post_hash"]:
            metadata["post_hash"] = str(item["post_hash"])
        if "has_full_content" in item:
            metadata["has_full_content"] = bool(item["has_full_content"])
        
        # Add data-specific fields
        if "file_count" in item:
            metadata["file_count"] = int(item["file_count"]) if isinstance(item["file_count"], (int, float)) else 0
        if "total_size" in item:
            metadata["total_size"] = int(item["total_size"]) if isinstance(item["total_size"], (int, float)) else 0
        if "files" in item:
            metadata["files"] = str(item["files"])  # Serialize list to string
        if "description" in item and item["description"]:
            metadata["description"] = str(item["description"])[:1000]  # Limit size
        if "has_description" in item:
            metadata["has_description"] = bool(item["has_description"])
        if "column_count" in item:
            metadata["column_count"] = int(item["column_count"]) if isinstance(item["column_count"], (int, float)) else 0
        if "last_updated" in item and item["last_updated"]:
            metadata["last_updated"] = str(item["last_updated"])
        
        return metadata

    def _extract_api_content(self, api_data: Dict[str, Any]) -> str:
        """Extract content from API data."""
        content = api_data.get("content", "")
        if not isinstance(content, str):
            logger.warning("API content is not a string, converting")
            content = str(content)
        
        return content.strip() if content else ""

    def _build_api_metadata(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata for API data."""
        metadata = {
            "source": "api",
            "section": str(api_data.get("section", "unknown")),
            "deep_scraped": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add optional fields
        if "topic" in api_data and api_data["topic"]:
            metadata["topic"] = str(api_data["topic"])
        if "url" in api_data and api_data["url"]:
            metadata["url"] = str(api_data["url"])
        if "title" in api_data and api_data["title"]:
            metadata["title"] = str(api_data["title"])
        
        return metadata

    def _index_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Index chunks in ChromaDB."""
        try:
            if not chunks:
                logger.warning("No chunks to index")
                return True
            
            # Get or create collection
            collection = self._get_collection()
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            embeddings = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                content = chunk["content"]
                metadata = chunk["metadata"]
                
                # Generate embedding
                embedding = self.embedding_model.encode(content).tolist()
                
                # Generate unique ID
                doc_id = f"{metadata.get('content_hash', 'unknown')}_{i}"
                
                documents.append(content)
                metadatas.append(metadata)
                embeddings.append(embedding)
                ids.append(doc_id)
            
            # Add to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            
            logger.info(f"Successfully indexed {len(chunks)} chunks in ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index chunks in ChromaDB: {e}")
            return False

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
