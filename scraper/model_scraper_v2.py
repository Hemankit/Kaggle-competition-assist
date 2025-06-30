# model_scraper_v2.py
import os
import json
import hashlib
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from scrape_handlers import scrapegraphai_handler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelScraperV2:
    def __init__(self, competition_slug: str, output_dir: str = "data/models"):
        self.slug = competition_slug
        self.output_dir = output_dir
        self.models: List[Dict] = []
        self.driver = None
        self.wait = None
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None

    def get_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def scroll_to_bottom(self):
        last_h = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_h = self.driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h

    def scrape_models(self) -> List[Dict]:
        url = f"https://www.kaggle.com/c/{self.slug}/models"
        self.setup_driver()
        self.driver.get(url)
        time.sleep(2)

        self.scroll_to_bottom()

        cards = self.driver.find_elements(By.CSS_SELECTOR, "div.model-card")
        logger.info(f"Found {len(cards)} model cards")

        for card in cards:
            try:
                title_el = card.find_element(By.CSS_SELECTOR, "h3")
                title = title_el.text.strip()
                url = title_el.find_element(By.TAG_NAME, "a").get_attribute("href")
                desc = card.find_element(By.CSS_SELECTOR, "p").text.strip()

                meta_elems = card.find_elements(By.CSS_SELECTOR, "span.meta")
                framework, variation, score = "", "", ""
                for m in meta_elems:
                    t = m.get_attribute("data-type")
                    if t == "framework":
                        framework = m.text
                    elif t == "variation":
                        variation = m.text
                    elif t == "score":
                        score = m.text

                entry = {
                    "title": title,
                    "url": url,
                    "description": desc,
                    "framework": framework,
                    "variation": variation,
                    "score": float(score) if score else 0.0,
                    "content_hash": self.get_hash(title + url + desc),
                    "metadata_hash": self.get_hash(title + variation + score),
                    "section": "models.main",
                    "last_scraped": self.timestamp,
                    "deep_scraped": False,
                    "deep_scraped_at": None,
                    "full_model_card": None,
                    "card_hash": None
                }

                self.models.append(entry)
            except Exception as e:
                logger.warning(f"[WARN] Failed to parse model card: {e}")

        self.close_driver()
        return self.models
    
    def update_model_with_deep_scrape(self, index: int, deep_data: Dict):
        self.models[index]["full_model_card"] = deep_data.get("full_model_card")
        self.models[index]["card_hash"] = deep_data.get("card_hash")
        self.models[index]["deep_scraped"] = True
        self.models[index]["deep_scraped_at"] = deep_data.get("deep_scraped_at")

    def deep_scrape_model_card(self, model_url: str) -> Optional[Dict]:
        """
        Deep scrape the model card for all details and variations.
        """
        logger.info(f"[INFO] Deep scraping model card: {model_url}")
        self.setup_driver()
        self.driver.get(model_url)
        time.sleep(2)

        try:
            # Scrape the main model card content
            content_el = self.driver.find_element(By.CSS_SELECTOR, "div.markdown")
            full = content_el.text

            # Scrape model details section (adjust selector as needed)
            try:
                details_el = self.driver.find_element(By.CSS_SELECTOR, "section.model-details")
                model_details = details_el.text
            except Exception:
                model_details = ""
            # Scrape model variations section (adjust selector as needed)
            try:
                variations_el = self.driver.find_element(By.CSS_SELECTOR, "section.model-variations")
                model_variations = variations_el.text
            except Exception:
                model_variations = ""

            card_hash = self.get_hash(full + model_details + model_variations)
        except Exception as e:
            logger.error(f"[ERROR] Failed to deep scrape model card {model_url}: {e}")
            self.close_driver()
            return None
        
        self.close_driver()

        return {
            "full_model_card": full,
            "model_details": model_details,
            "model_variations": model_variations,
            "card_hash": card_hash,
            "deep_scraped_at": datetime.now(datetime.timezone.utc).isoformat(),
            "deep_scraped": True
        }

    def update_model_with_deep_scrape(self, index: int, deep_data: Dict):
        self.models[index]["full_model_card"] = deep_data.get("full_model_card")
        self.models[index]["model_details"] = deep_data.get("model_details")
        self.models[index]["model_variations"] = deep_data.get("model_variations")
        self.models[index]["card_hash"] = deep_data.get("card_hash")
        self.models[index]["deep_scraped"] = True
        self.models[index]["deep_scraped_at"] = deep_data.get("deep_scraped_at")

    


    def save_to_json(self, path: Optional[str] = None):
        os.makedirs(self.output_dir, exist_ok=True)
        path = path or os.path.join(self.output_dir, f"{self.slug}_models.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.models, f, indent=2)
        logger.info(f"✅ Saved {len(self.models)} models to {path}")
        return path

    def load_from_json(self, path: Optional[str] = None) -> List[Dict]:
        path = path or os.path.join(self.output_dir, f"{self.slug}_models.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.models = json.load(f)
        return self.models
    
    def parse(self, item: Dict) -> Dict:
        """
        Convert a deeply scraped model card into a standardized format.
        """
        return {
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "section": item.get("section", "models"),
        "relevance_score": item.get("relevance_score", None),
        "metadata": {
            "card_hash": item.get("card_hash"),
            "deep_scraped_at": item.get("deep_scraped_at"),
        },
        "content": item.get("full_model_card", ""),
    }

    def get_all_cleaned_models(self) -> List[Dict]:
        if not self.models:
            self.load_from_json()
        return self.models

    def deep_scrape_models_with_llm(self, query: str, mode: str = "summary", model: str = "codellama:13b") -> List[Dict]:

        models = self.get_all_cleaned_models()
        metadata = [{"title": m["title"], "content": m.get("full_model_card", m.get("description", ""))} for m in models]

        results = scrapegraphai_handler(
        query=query,
        mode=mode,
        metadata=metadata,
        model=model
    )
        return results