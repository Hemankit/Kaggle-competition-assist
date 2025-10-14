import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from .result_structurer import compute_content_hash
from .redis_cache import RedisCache
from .section_metadata import get_section_metadata

logger = logging.getLogger(__name__)

class DeepScraperExecutor:
    def __init__(self, notebook_scraper, discussion_scraper, model_scraper, decider_chain):
        self.notebook_scraper = notebook_scraper
        self.discussion_scraper = discussion_scraper
        self.model_scraper = model_scraper
        self.deep_scrape_decider = decider_chain
        self.cache = RedisCache()

    def deep_scraping_pinned(self, query: str, section: str) -> List[Dict[str, Any]]:
        """Perform deep scraping on pinned items."""
        scraper, items = self._get_scraper_and_items(section, pinned=True)
        if not scraper or not items:
            return []

        logger.info(f"Deep scraping pinned items for query '{query}' in section '{section}'")
        deep_scraped = scraper(items)

        for item in deep_scraped:
            content_hash = compute_content_hash(item.get("content", ""))
            self.cache.update_cache("", content_hash, deep_scraped=True)
            item["deep_scraped"] = True
            item["deep_scraped_at"] = datetime.now(timezone.utc).isoformat()
            item["content_hash"] = content_hash
            item["metadata"] = get_section_metadata(section, item)

        return deep_scraped

    def deep_scraping_not_pinned(self, query: str, section: str) -> List[Dict[str, Any]]:
        """Perform deep scraping on items not already pinned, based on decision chain."""
        scraper, items = self._get_scraper_and_items(section, pinned=False)
        if not scraper or not items:
            return []

        deep_scraped_results = []
        for item in items:
            content_hash = compute_content_hash(item.get("content", ""))
            cached = self.cache.get_cache(content_hash)

            if cached and cached.get("deep_scraped"):
                logger.info(f"Skipping cached item: {item.get('title', '')}")
                continue

            decision = self.deep_scrape_decider.invoke({
                "query": query,
                "section": section,
                "title": item.get("title", ""),
                "has_image": item.get("has_image", False),
                "pinned": item.get("pinned", False),
                "content_snippet": item.get("content_snippet", "")
            })

            if "YES" in decision.upper():
                logger.info(f"Deep scraping: {item.get('title', '')}")
                result = scraper([item])
                for r in result:
                    result_hash = compute_content_hash(r.get("content", ""))
                    self.cache.update_cache("", result_hash, deep_scraped=True)
                    r["deep_scraped"] = True
                    r["deep_scraped_at"] = datetime.now(timezone.utc).isoformat()
                    r["content_hash"] = result_hash
                    r["metadata"] = get_section_metadata(section, r)
                deep_scraped_results.extend(result)
            else:
                logger.info(f"Skipping deep scrape: {item.get('title', '')}")

        return deep_scraped_results
    
    def deep_scrape_item(self, item: dict, section: str, query: str) -> dict:
        """
        Deep scrape a single item if the decision chain says YES.
        Returns the deep-scraped item dict, or None if not deep scraped.
        """
        content_hash = compute_content_hash(item.get("content", ""))
        cached = self.cache.get_cache(content_hash)
        if cached and cached.get("deep_scraped"):
            logger.info(f"Skipping cached item: {item.get('title', '')}")
            return None

        # Decision
        decision = self.deep_scrape_decider.invoke({
            "query": query,
            "section": section,
            "title": item.get("title", ""),
            "has_image": item.get("has_image", False),
            "pinned": item.get("pinned", False),
            "content_snippet": item.get("content_snippet", "")
        })

        if "YES" in decision.upper():
            logger.info(f"Deep scraping: {item.get('title', '')}")
            # Select the correct scraper for the section
            if section == "code":
                result = self.notebook_scraper.deep_scrape_notebooks(query, mode="summary")
            elif section == "discussion":
                result = self.discussion_scraper.deep_scrape_discussion(query, mode="summary")
            elif section == "model":
                result = self.model_scraper.deep_scrape_models_with_llm(query, mode="summary")
            else:
                logger.warning(f"Unknown section for deep scrape: {section}")
                return None

            if result:
                r = result[0]
                result_hash = compute_content_hash(r.get("content", ""))
                self.cache.update_cache("", result_hash, deep_scraped=True)
                r["deep_scraped"] = True
                r["deep_scraped_at"] = datetime.now(timezone.utc).isoformat()
                r["content_hash"] = result_hash
                r["metadata"] = get_section_metadata(section, r)
                return r
        else:
            logger.info(f"Skipping deep scrape: {item.get('title', '')}")
        return None

    def _get_scraper_and_items(self, section: str, pinned: bool):
        if section == "code":
            items = [n for n in self.notebook_scraper.get_all_cleaned_notebooks() if n.get("is_pinned", False) == pinned]
            return self.notebook_scraper.deep_scrape_notebooks, items
        elif section == "discussion":
            items = [d for d in self.discussion_scraper.get_all_cleaned_discussions() if d.get("is_pinned", False) == pinned]
            return self.discussion_scraper.deep_scrape_discussion, items
        elif section == "model":
            items = [m for m in self.model_scraper.get_all_cleaned_models() if m.get("is_pinned", False) == pinned]
            return self.model_scraper.deep_scrape_models_with_llm, items
        else:
            logger.warning(f"Unknown section: {section}")
            return None, None