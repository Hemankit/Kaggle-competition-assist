import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class RetrievalLogger:
    """
    Logs queries and retrieved documents during RAG pipeline execution.
    """
    def __init__(self):
        self.logger = logger

    def log(self, query, retrieved_docs, section=None):
        timestamp = datetime.datetime.now().isoformat()

        self.logger.info(f"[{timestamp}] Retrieval Log:")
        self.logger.info(f"🔍 Query: {query}")
        if section:
            self.logger.info(f"📂 Section: {section}")
        self.logger.info(f"📄 Retrieved {len(retrieved_docs)} documents.")

        for i, doc in enumerate(retrieved_docs[:5]):  # Log top 5 only
            self.logger.info(f"  📘 Document {i + 1}:")
            meta = doc.get("metadata", doc.get("meta", {}))
            content = (
                doc.get("content", "")
                or doc.get("markdown_blocks", "")
                or doc.get("ocr_content", "")
                or doc.get("model_card_details", "")
            )
            self.logger.info(f"    Metadata: {meta}")
            snippet = content[:200].replace('\n', ' ') + "..."
            self.logger.info(f"    Content Snippet: {snippet}")