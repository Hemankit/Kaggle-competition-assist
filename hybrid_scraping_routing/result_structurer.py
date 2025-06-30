import logging
from datetime import datetime, timezone
from hybrid_scraping_routing.redis_cache import RedisCache

logger = logging.getLogger(__name__)

class ResultStructurer:
    def __init__(self, notebook_scraper, discussion_scraper, model_scraper):
        self.notebook_scraper = notebook_scraper
        self.discussion_scraper = discussion_scraper
        self.model_scraper = model_scraper
        self.cache = RedisCache()

    def structure_results(self, deep_scraped_results, section):
        structured_results = []

        for result in deep_scraped_results:
            content = result.get("content", "")
            content_hash = self.cache.compute_hash(content)
            if self.cache.is_deep_scraped(content_hash):
                logger.info(f"Skipping already structured item: {result.get('title', '')}")
                continue

            if section == "code":
                structured = self.notebook_scraper.parse({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "section": section,
                    "relevance_score": result.get("relevance_score", None),
                    "metadata": result.get("metadata", {}),
                    "content": result.get("markdown_blocks", "")
                })
            elif section == "discussion":
                structured = self.discussion_scraper.parse({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "section": section,
                    "relevance_score": result.get("relevance_score", None),
                    "metadata": result.get("metadata", {}),
                    "content": result.get("ocr_content", "")
                })
            elif section == "model":
                structured = self.model_scraper.parse({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "section": section,
                    "relevance_score": result.get("relevance_score", None),
                    "metadata": result.get("metadata", {}),
                    "content": result.get("model_card_details", "")
                })
            else:
                logger.warning(f"No parser for section: {section}")
                continue

            structured_dict = structured.dict() if hasattr(structured, 'dict') else structured
            structured_dict.update({
                "deep_scraped": True,
                "deep_scraped_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": content_hash
            })

            structured_results.append(structured_dict)
            self.cache.set_deep_scraped(content_hash)

        return structured_results