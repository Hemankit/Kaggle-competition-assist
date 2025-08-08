import logging
from typing import List, Dict, Any
from datetime import datetime

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
        self.overview_scraper = OverviewScraper()
        self.kaggle_api = KaggleFetcher()
        self.api_results = []

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

    def route_to_retrieval_method(self, section: str, predicted_section: str) -> Any:
        """
        Route to the appropriate retrieval method based on the section.
        """
        logger.info(f"Routing query. Queried section: '{section}', Predicted section: '{predicted_section}'")

        if section != predicted_section:
            logger.error(f"Section mismatch: queried='{section}' vs predicted='{predicted_section}'")
            raise ValueError(f"Section mismatch: {section} != {predicted_section}")

        api_retriever = {
            "leaderboard": self.kaggle_api.fetch_leaderboard_metadata,
            "data": self.kaggle_api.fetch_dataset_metadata,
        }
        scraper_retriever = {
            "overview": self.overview_scraper.scrape,
            "code": self.notebook_scraper.scrape,
            "model": self.model_scraper.scrape_models,
            "discussion": self.discussion_scraper.scrape,
        }

        if section in api_retriever:
            logger.info(f"Using API retriever for section: '{section}'")
            result = api_retriever[section]()
            self.api_results.append({
                "section": section,
                "retrieved_at": datetime.now().isoformat(),
                "content": result
            })
            return result
        
        logger.info(f"Using scraper retriever for section: '{section}'")
        result = scraper_retriever[section]()
        return result
    
    def run(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = inputs.get("query")
        section = inputs.get("section")
        predicted_section = inputs.get("predicted_section", section)
        logger.info(f"[Agent] Running hybrid scraping agent for query='{query}', section='{section}'")

        # api based sections
        if section in ["leaderboard", "data"]:
            result = self.route_to_retrieval_method(section, predicted_section)
            return [{"section": section, "content": result}]

        # Scraping (shallow)
        scraper_retriever = {
            "overview": self.overview_scraper.scrape,
            "code": self.notebook_scraper.scrape,
            "model": self.model_scraper.scrape_models,
            "discussion": self.discussion_scraper.scrape,
        }
        scrape_results = []
        if section in scraper_retriever:
            try:
                scrape_results = scraper_retriever[section]()
            except Exception as e:
                logger.error(f"Error during scraping for section '{section}': {e}")
                scrape_results = []
            # Ensure scrape_results is a list
            if not isinstance(scrape_results, list):
                scrape_results = [scrape_results]

        # Deep scraping
        pinned_results = self.deep_scraper.deep_scraping_pinned(query, section)
        not_pinned_results = self.deep_scraper.deep_scraping_not_pinned(query, section, self.llm)
        all_results = scrape_results + pinned_results + not_pinned_results
        structured_results = self.result_structurer.structure_results(all_results, section)

        if structured_results and hasattr(structured_results[0], 'dict'):
            return [r.dict() for r in structured_results]
        return structured_results