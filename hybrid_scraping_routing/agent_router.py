
import logging
from typing import List, Dict, Any

from Kaggle_Fetcher.kaggle_fetcher import KaggleFetcher
from scraper.overview_scraper import OverviewScraper
from scraper.notebook_scraper_v2 import NotebookScraperV2
from scraper.model_scraper_v2 import ModelScraperV2
from scraper.discussion_scraper_v2 import DiscussionScraperV2
from scraper.screenshots_handler import extract_text_from_posts
from scraper.ai_scrape_config import AIScrapeConfig
from scraper.scrape_handlers import scrapegraphai_handler

from hybrid_scraping_routing.redis_cache import RedisCache
from hybrid_scraping_routing.scraping_decider import ScrapingDecider
from hybrid_scraping_routing.deep_scraper_executor import DeepScraperExecutor
from hybrid_scraping_routing.result_structurer import ResultStructurer
from hybrid_scraping_routing.section_metadata import get_section_metadata

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class HybridScrapingAgent:
    def __init__(self, llm):
        self.llm = llm

        # Scrapers
        self.notebook_scraper = NotebookScraperV2()
        self.model_scraper = ModelScraperV2()
        self.discussion_scraper = DiscussionScraperV2()

        # Core components
        self.cache = RedisCache()
        self.config = AIScrapeConfig("ai_scrape_config.json")
        self.scrape_decider = ScrapingDecider(llm)
        self.deep_scraper = DeepScraperExecutor(
            self.notebook_scraper,
            self.model_scraper,
            self.discussion_scraper,
            self.scrape_decider,
            self.cache
        )
        self.result_structurer = ResultStructurer(
            self.notebook_scraper,
            self.model_scraper,
            self.discussion_scraper,
            self.cache
        )

    def run(self, query: str, section: str) -> List[Dict[str, Any]]:
        """
        Entry point to the hybrid scraping agent.
        Performs deep scraping where needed and returns structured data.
        """
        logger.info(f"[Agent] Running hybrid scraping agent for query='{query}', section='{section}'")

        # Always deep scrape pinned
        pinned_results = self.deep_scraper.deep_scraping_pinned(query, section)

        # Conditionally scrape non-pinned based on LLM decision
        not_pinned_results = self.deep_scraper.deep_scraping_not_pinned(query, section, self.llm)

        # Merge and structure
        all_results = pinned_results + not_pinned_results
        structured = self.result_structurer.structure_results(all_results, section)

        return structured