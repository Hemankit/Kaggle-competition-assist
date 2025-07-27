from haystack.nodes import SentenceTransformersRanker
from haystack.schema import Document
from typing import List
import logging

logger = logging.getLogger(__name__)

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", use_gpu: bool = True):
        self.reranker = SentenceTransformersRanker(
            model_name_or_path=model_name,
            use_gpu=use_gpu
        )

    def rerank(self, query: str, retrieved_docs: List[dict], top_k: int = 5) -> List[Document]:
        logger.info(f"🔁 Reranking top {len(retrieved_docs)} retrieved documents for query: '{query}'")
        # Convert dicts to Haystack Document objects if needed
        haystack_docs = []
        for doc in retrieved_docs:
            content = (
                doc.get("content", "")
                or doc.get("markdown_blocks", "")
                or doc.get("ocr_content", "")
                or doc.get("model_card_details", "")
            )
            meta = doc.get("metadata", doc.get("meta", {}))
            haystack_docs.append(Document(content=content, meta=meta))
        reranked_docs = self.reranker.predict(query=query, documents=haystack_docs)
        return reranked_docs[:top_k]
