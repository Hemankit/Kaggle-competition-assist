import logging
from haystack.nodes import PreProcessor
from haystack import Document
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Chunker:
    def __init__(self, document_store, retriever):
        self.document_store = document_store
        self.retriever = retriever

        self.preprocessor = PreProcessor(
            split_by="sentence",
            split_length=100,
            split_overlap=20,
            clean_empty_lines=True,
            clean_whitespace=True,
            remove_substrings=None
        )

    def chunk_and_index(self, pydantic_results: List[Dict[str, Any]], structured_results: List[Dict[str, Any]]) -> str:
        all_results = pydantic_results + structured_results
        target_sections = {"overview", "discussion"}

        overview_and_discussion_docs = [
            result for result in all_results if result.get("section") in target_sections
        ]

        chunks = []
        for doc in overview_and_discussion_docs:
            content = (
                doc.get("content", "")
                or doc.get("markdown_blocks", "")
                or doc.get("ocr_content", "")
            )
            if not content.strip():
                continue

            # Build standard metadata
            meta = {
                "section": doc.get("section", "unknown"),
                "source": doc.get("source", "scraped" if not doc.get("deep_scraped") else "deep_scraped"),
                "deep_scraped": doc.get("deep_scraped", False),
                "content_hash": doc.get("content_hash", ""),
            }

            if "topic" in doc:
                meta["topic"] = doc["topic"]

            # Wrap for preprocessing
            haystack_doc = {"content": content, "meta": meta}
            preprocessed = self.preprocessor.process(documents=[haystack_doc])
            chunks.extend(preprocessed)

        if chunks:
            self.document_store.write_documents(chunks)
            self.document_store.update_embeddings(self.retriever)
            logger.info(f"✅ Successfully chunked and indexed {len(chunks)} documents.")
        else:
            logger.warning("⚠️ No chunks created for indexing.")

        return f"Chunked and indexed {len(chunks)} documents."