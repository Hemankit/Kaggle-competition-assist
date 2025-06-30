# kaggle_scraper.py

"""
Orchestrates full scrape process for a Kaggle competition
"""

from .overview_scraper import OverviewScraper
from .model_scraper import ModelScraper
from .code_scraper import CodeScraper
from .discussion_scraper import DiscussionScraper

class ScraperOrchestrator:
    def __init__(self, competition_name):
        self.competition_name = competition_name
        self.overview_scraper = OverviewScraper(competition_name)
        self.model_scraper = ModelScraper(competition_name)
        self.code_scraper = CodeScraper(competition_name)
        self.discussion_scraper = DiscussionScraper(competition_name)

    def run(self, sections=None):
        """
        Runs the full or partial scrape process.

        Args:
            sections (list or None): Optional list of sections to scrape.
                Possible values: ["overview", "model", "code", "discussion"]
                If None, all sections will be scraped.

        Returns:
            dict: Dictionary with keys as section names and values as scraped data.
        """
        results = {}

        if sections is None or "overview" in sections:
            results["overview"] = self.overview_scraper.scrape()

        if sections is None or "model" in sections:
            results["model"] = self.model_scraper.scrape()

        if sections is None or "code" in sections:
            results["code"] = self.code_scraper.scrape()

        if sections is None or "discussion" in sections:
            results["discussion"] = self.discussion_scraper.scrape()

        return results
