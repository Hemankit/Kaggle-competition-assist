

import logging
import hashlib
from datetime import datetime, timezone
from hybrid_scraping_routing.redis_cache import RedisCache
from pydantic import BaseModel
from typing import Optional, Dict, Any

class RetrievalResult(BaseModel):
    title: str
    url: str
    section: str
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = {}
    deep_scraped: bool = False
    deep_scraped_at: Optional[str] = None
    content_hash: str

logger = logging.getLogger(__name__)


def compute_content_hash(text: str) -> str:
    """
    Compute SHA256 hash of the given text content.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class ResultStructurer:
    def __init__(self, notebook_scraper, discussion_scraper, model_scraper):
        self.notebook_scraper = notebook_scraper
        self.discussion_scraper = discussion_scraper
        self.model_scraper = model_scraper
        self.cache = RedisCache()

    def structure_results(self, results, section):
        """
        Structure and annotate both scraped and deep-scraped results, with cache checks and metadata.
        Returns a list of RetrievalResult dicts.
        """
        structured_results = []

        for result in results:
            content = (
                result.get("content", "")
                or result.get("markdown_blocks", "")
                or result.get("ocr_content", "")
                or result.get("model_card_details", "")
            )
            raw_for_hash = f"{result.get('title', '')}|{result.get('url', '')}|{content}"
            content_hash = compute_content_hash(raw_for_hash)

            cached_data = self.cache.get_cache(content_hash)
            deep_scraped = cached_data.get("deep_scraped", False) if cached_data else False
            deep_scraped_at = cached_data.get("deep_scraped_at") if cached_data else None

            # Parse and structure using the appropriate scraper
            if section == "code":
                metadata = result.get("metadata", {})
                structured_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "section": section,
                    "relevance_score": result.get("relevance_score", None),
                    "metadata": metadata,
                    "deep_scraped": deep_scraped,
                    "deep_scraped_at": deep_scraped_at,
                    "content_hash": content_hash
                }
            elif section == "discussion":
                metadata = result.get("metadata", {})
                structured_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "section": section,
                    "relevance_score": result.get("relevance_score", None),
                    "metadata": metadata,
                    "deep_scraped": deep_scraped,
                    "deep_scraped_at": deep_scraped_at,
                    "content_hash": content_hash
                }
            elif section == "model":
                metadata = result.get("metadata", {})
                structured_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "section": section,
                    "relevance_score": result.get("relevance_score", None),
                    "metadata": metadata,
                    "deep_scraped": deep_scraped,
                    "deep_scraped_at": deep_scraped_at,
                    "content_hash": content_hash
                }
            else:
                logger.warning(f"No parser for section: {section}")
                continue

            # Validate and structure using Pydantic
            structured_result = RetrievalResult(**structured_data)
            structured_results.append(structured_result.dict())

            # If this result is newly deep-scraped, update cache
            if result.get("deep_scraped", False) and not deep_scraped:
                self.cache.update_cache(content_hash, deep_scraped=True)

        return structured_results