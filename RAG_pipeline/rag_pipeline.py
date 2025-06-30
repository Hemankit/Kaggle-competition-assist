import datetime
from typing import List, Dict

from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever, PreProcessor
from haystack.schema import Document
from haystack.nodes import SentenceTransformersRanker
from sentence_transformers import SentenceTransformer

import logging
logger = logging.getLogger(__name__)


class HaystackRAGPipeline:
    def __init__(self, index_name="kaggle_index", use_faiss=True, embedding_model="BAAI/bge-base-en"):
        """
        Initializes the RAG pipeline with a FAISS document store and an embedding retriever.
        """
        self.document_store = FAISSDocumentStore(
            faiss_index_factory_str="IVF256,Flat",
            similarity="cosine",
            return_embedding=True
        )

        self.retriever = EmbeddingRetriever(
            document_store=self.document_store,
            embedding_model=embedding_model,
            model_format="sentence_transformers",
            use_gpu=True
        )

        self.embedding_model = SentenceTransformer(embedding_model)

        self.reranker = SentenceTransformersRanker(
            model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2",
            use_gpu=True
        )

        self.indexed_hashes = set()

    def index_scraped_data(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        documents_to_index = []

        def create_document(item, source_type):
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            metadata.update({
                "content_hash": item.get("content_hash"),
                "source": source_type,
                "deep_scraped": item.get("deep_scraped", False),
            })
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

    def index_api_data(self, api_results: List[Dict]):
        documents_to_index = []
        for api_data in api_results:
            api_content = api_data.get("content", "")
            if not api_content.strip():
                continue
            embed_api_content = self.embedding_model.encode(api_content)
            documents_to_index.append({
                "content": api_content,
                "embedding": embed_api_content
            })
        self.document_store.write_documents(documents_to_index)

    def chunk_and_index(self, pydantic_results: List[Dict], structured_results: List[Dict]):
        all_results = pydantic_results + structured_results
        overview_and_discussion_docs = [result for result in all_results if result.get("section") in {"overview", "discussion"}]

        preprocessor = PreProcessor(
            split_by="sentence",
            split_length=100,
            split_overlap=20,
            clean_empty_lines=True,
            clean_whitespace=True,
            remove_substrings=None
        )

        chunks = []
        for doc in overview_and_discussion_docs:
            preprocessed = preprocessor.process(documents=[{"content": doc["content"], "meta": doc}])
            chunks.extend(preprocessed)

        self.document_store.write_documents(chunks)
        self.document_store.update_embeddings(self.retriever)

        return f"Successfully chunked and indexed {len(chunks)} documents."

    def rerank_document_store(self, query: str, top_k_retrieval: int = 20, top_k_final: int = 5):
        retrieved_docs = self.retriever.retrieve(query=query, top_k=top_k_retrieval)
        reranked_docs = self.reranker.predict(query=query, documents=retrieved_docs)
        return reranked_docs[:top_k_final]

    def log_retrieval(self, query: str, retrieved_docs: List[Document], section: str = None):
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