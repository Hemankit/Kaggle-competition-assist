from haystack import Document 
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from sentence_transformers import SentenceTransformer
from haystack.nodes import SentenceTransformersRanker
import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Indexer:
    def __init__(self, document_store: FAISSDocumentStore, retriever: EmbeddingRetriever, embedding_model: SentenceTransformer, reranker: SentenceTransformersRanker):
        self.document_store = document_store
        self.retriever = retriever
        self.embedding_model = embedding_model
        self.reranker = reranker
        self.indexed_hashes = set()

    def index_scraped_data(self, pydantic_results, structured_results):
        documents_to_index = []

        def create_document(item, source_type):
            content = item.get("content", "")
            metadata = {
                "content_hash": item.get("content_hash", ""),
                "source": source_type,
                "section": item.get("section", "unknown"),
                "deep_scraped": item.get("deep_scraped", False),
            }

            # Optional: Include topic if available
            if "topic" in item:
                metadata["topic"] = item["topic"]

            return Document(content=content, meta=metadata)

        for result in pydantic_results:
            documents_to_index.append(create_document(result, "scraped"))

        for result in structured_results:
            documents_to_index.append(create_document(result, "deep_scraped"))

        self.document_store.write_documents(documents_to_index)
        self.document_store.update_embeddings(
            self.retriever,
            filters={"source": ["scraped", "deep_scraped"]}
        )

    def index_api_data(self, api_results):
        documents_to_index = []
        for api_data in api_results:
            api_content = api_data.get("content", "")
            if not api_content.strip():
                continue

            embedding = self.embedding_model.encode(api_content)

            metadata = {
                "source": "api",
                "section": api_data.get("section", "unknown"),
                "deep_scraped": False
            }

            if "topic" in api_data:
                metadata["topic"] = api_data["topic"]

            documents_to_index.append(
                Document(content=api_content, embedding=embedding, meta=metadata)
            )

        self.document_store.write_documents(documents_to_index)

    def log_retrieval(self, query, retrieved_docs, section=None):
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