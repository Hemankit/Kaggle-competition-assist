
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from tqdm import tqdm
import sys
import os
# Add the parent directory to sys.path so that 'selectors' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selectors.overview_selectors import (
    SECTION_SELECTOR,
    TITLE_SELECTOR,
    MARKDOWN_SELECTOR,
    FORMAT_BLOCK_SELECTOR
)
class OverviewScraper:
    def __init__(self, competition_name: str):
        self.competition_name = competition_name
        self.base_url = f"https://www.kaggle.com/c/{competition_name}/overview"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

    def scrape_overview_data(self, url: str) -> Dict[str, Any]:
        for _ in range(3):  # Retry logic
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                continue
        else:
            print("Failed after retries.")
            return {}, []

        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.select_one("div.main-content")
        if not main_content:
            return {}, []

        sections = main_content.select(SECTION_SELECTOR)
        scraped_data = {}
        section_titles = []

        for section in sections:
            title_tag = section.select_one(TITLE_SELECTOR)
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            section_titles.append(title)

            content = section.select_one(MARKDOWN_SELECTOR)
            content_text = content.get_text(strip=True) if content else ""

            # Also extract format blocks if present
            format_block = section.select_one(FORMAT_BLOCK_SELECTOR)
            if format_block:
                content_text += "\n\n[Format Block]\n" + format_block.get_text(strip=True)

            scraped_data[title] = content_text

        return scraped_data, section_titles

    def scrape(self) -> Dict[str, Any]:
        print(f"Scraping overview for: {self.competition_name}")
        data, titles = self.scrape_overview_data(self.base_url)
        return {
            "competition_name": self.competition_name,
            "scraped_data": data,
            "section_titles": titles
        }

            
        

    