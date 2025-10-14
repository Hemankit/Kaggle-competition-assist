# model_scraper_v2.py
import os
import json
import hashlib
import logging
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from .scrape_handlers import scrapegraphai_handler

logger = logging.getLogger(__name__)


class ModelScraperV2:
    def __init__(self, competition_slug: str = "titanic", output_dir: str = "data/models"):
        # Validate constructor inputs
        if not isinstance(competition_slug, str) or not competition_slug.strip():
            raise ValueError("competition_slug must be a non-empty string.")
        if not isinstance(output_dir, str) or not output_dir.strip():
            raise ValueError("output_dir must be a non-empty string.")
        
        self.slug = competition_slug
        self.output_dir = output_dir
        # Correct type annotation for safety
        self.models: List[Dict[str, Any]] = []
        self.driver = None
        self.wait = None
        # Use modern timezone-aware datetime
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def setup_driver(self):
        """Setup Chrome WebDriver with error handling."""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("WebDriver setup successful")
        except WebDriverException as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise RuntimeError(f"WebDriver setup failed: {e}")

    def close_driver(self):
        """Safely close WebDriver and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None

    def get_hash(self, text: str) -> str:
        """Compute SHA256 hash of text with validation."""
        if not isinstance(text, str):
            logger.warning("get_hash expected string, got %s; coercing to str", type(text).__name__)
            text = str(text)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def scroll_to_bottom(self):
        """Scroll to bottom of page with infinite loop protection."""
        if not self.driver:
            logger.error("Driver not initialized for scrolling")
            return
        
        try:
            last_h = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 50  # Prevent infinite loops
            
            while scroll_attempts < max_attempts:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                new_h = self.driver.execute_script("return document.body.scrollHeight")
                if new_h == last_h:
                    break
                last_h = new_h
                scroll_attempts += 1
            
            if scroll_attempts >= max_attempts:
                logger.warning("Reached maximum scroll attempts, stopping")
        except Exception as e:
            logger.error(f"Error during scrolling: {e}")

    def scrape_models(self) -> List[Dict[str, Any]]:
        """Scrape model information from Kaggle competition models page."""
        url = f"https://www.kaggle.com/c/{self.slug}/models"
        
        try:
            self.setup_driver()
            self.driver.get(url)
            time.sleep(2)

            self.scroll_to_bottom()

            cards = self.driver.find_elements(By.CSS_SELECTOR, "div.model-card")
            logger.info(f"Found {len(cards)} model cards")

            for card in cards:
                try:
                    # Extract title and URL
                    title_el = card.find_element(By.CSS_SELECTOR, "h3")
                    title = title_el.text.strip()
                    url_el = title_el.find_element(By.TAG_NAME, "a")
                    model_url = url_el.get_attribute("href")
                    
                    # Extract description
                    desc_el = card.find_element(By.CSS_SELECTOR, "p")
                    desc = desc_el.text.strip()

                    # Extract metadata
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

                    # Safe score conversion
                    try:
                        score_float = float(score) if score else 0.0
                    except ValueError:
                        logger.warning(f"Invalid score format '{score}', using 0.0")
                        score_float = 0.0

                    # Safe string concatenation for hashes
                    content_text = f"{title}{model_url}{desc}"
                    metadata_text = f"{title}{variation}{score}"

                    entry = {
                        "title": title,
                        "url": model_url,
                        "description": desc,
                        "framework": framework,
                        "variation": variation,
                        "score": score_float,
                        "content_hash": self.get_hash(content_text),
                        "metadata_hash": self.get_hash(metadata_text),
                        "section": "models.main",
                        "last_scraped": self.timestamp,
                        "deep_scraped": False,
                        "deep_scraped_at": None,
                        "full_model_card": None,
                        "card_hash": None
                    }

                    self.models.append(entry)
                except NoSuchElementException as e:
                    logger.warning(f"Failed to find required element in model card: {e}")
                except Exception as e:
                    logger.warning(f"Failed to parse model card: {e}")

        except Exception as e:
            logger.error(f"Error during model scraping: {e}")
        finally:
            self.close_driver()
        
        return self.models
    
    def update_model_with_deep_scrape(self, index: int, deep_data: Dict[str, Any]) -> None:
        """Update model entry with deep scraped data."""
        if not isinstance(index, int) or index < 0 or index >= len(self.models):
            logger.error(f"Invalid index {index} for models list of length {len(self.models)}")
            return
        
        if not isinstance(deep_data, dict):
            logger.error("deep_data must be a dictionary")
            return
        
        self.models[index]["full_model_card"] = deep_data.get("full_model_card")
        self.models[index]["model_details"] = deep_data.get("model_details")
        self.models[index]["model_variations"] = deep_data.get("model_variations")
        self.models[index]["card_hash"] = deep_data.get("card_hash")
        self.models[index]["deep_scraped"] = True
        self.models[index]["deep_scraped_at"] = deep_data.get("deep_scraped_at")

    def deep_scrape_model_card(self, model_url: str) -> Optional[Dict[str, Any]]:
        """
        Deep scrape the model card for all details and variations.
        """
        # Validate input
        if not isinstance(model_url, str) or not model_url.strip():
            logger.error("Invalid model_url provided")
            return None
        
        logger.info(f"Deep scraping model card: {model_url}")
        
        try:
            self.setup_driver()
            self.driver.get(model_url)
            time.sleep(2)

            # Initialize variables to prevent UnboundLocalError
            full = ""
            model_details = ""
            model_variations = ""

            try:
                # Scrape the main model card content
                content_el = self.driver.find_element(By.CSS_SELECTOR, "div.markdown")
                full = content_el.text
            except NoSuchElementException:
                logger.warning("Could not find main content element")
                full = ""

            # Scrape model details section
            try:
                details_el = self.driver.find_element(By.CSS_SELECTOR, "section.model-details")
                model_details = details_el.text
            except NoSuchElementException:
                logger.debug("Model details section not found")
                model_details = ""

            # Scrape model variations section
            try:
                variations_el = self.driver.find_element(By.CSS_SELECTOR, "section.model-variations")
                model_variations = variations_el.text
            except NoSuchElementException:
                logger.debug("Model variations section not found")
                model_variations = ""

            # Safe string concatenation for hash
            combined_text = f"{full}{model_details}{model_variations}"
            card_hash = self.get_hash(combined_text)

        except Exception as e:
            logger.error(f"Failed to deep scrape model card {model_url}: {e}")
            return None
        finally:
            self.close_driver()

        return {
            "full_model_card": full,
            "model_details": model_details,
            "model_variations": model_variations,
            "card_hash": card_hash,
            "deep_scraped_at": datetime.now(timezone.utc).isoformat(),
            "deep_scraped": True
        }

    def save_to_json(self, path: Optional[str] = None) -> str:
        """Save models data to JSON file with error handling."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            file_path = path or os.path.join(self.output_dir, f"{self.slug}_models.json")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.models, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.models)} models to {file_path}")
            return file_path
        except OSError as e:
            logger.error(f"Failed to save models to JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving models: {e}")
            raise

    def load_from_json(self, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load models data from JSON file with error handling."""
        file_path = path or os.path.join(self.output_dir, f"{self.slug}_models.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Models file not found: {file_path}")
            return []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.error(f"Expected list in JSON file, got {type(data).__name__}")
                return []
            
            self.models = data
            logger.info(f"Loaded {len(self.models)} models from {file_path}")
            return self.models
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            return []
        except OSError as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return []
    
    def parse(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a deeply scraped model card into a standardized format.
        """
        if not isinstance(item, dict):
            logger.error("parse expected a dict, got %s", type(item).__name__)
            return {
                "title": "",
                "url": "",
                "section": "models",
                "relevance_score": None,
                "metadata": {"card_hash": None, "deep_scraped_at": None},
                "content": "",
            }
        
        return {
            "title": str(item.get("title", "")),
            "url": str(item.get("url", "")),
            "section": str(item.get("section", "models")),
            "relevance_score": item.get("relevance_score", None),
            "metadata": {
                "card_hash": item.get("card_hash"),
                "deep_scraped_at": item.get("deep_scraped_at"),
            },
            "content": str(item.get("full_model_card", "")),
        }

    def get_all_cleaned_models(self) -> List[Dict[str, Any]]:
        """Get all models, loading from file if not already in memory."""
        if not self.models:
            self.load_from_json()
        return self.models

    def deep_scrape_models_with_llm(
        self, query: str, mode: str = "summary", model: str = "codellama:13b"
    ) -> List[Dict[str, Any]]:
        """Perform AI-powered deep scraping on models using ScrapeGraphAI."""
        # Validate inputs
        if not isinstance(query, str) or not query.strip():
            logger.error("deep_scrape_models_with_llm: 'query' must be a non-empty string.")
            return []
        if not isinstance(mode, str) or not mode.strip():
            logger.error("deep_scrape_models_with_llm: 'mode' must be a non-empty string.")
            return []
        if not isinstance(model, str) or not model.strip():
            logger.error("deep_scrape_models_with_llm: 'model' must be a non-empty string.")
            return []

        models = self.get_all_cleaned_models()
        
        # Safe metadata creation with key validation
        metadata = []
        for m in models:
            if not isinstance(m, dict):
                continue
            
            title = m.get("title", "")
            content = m.get("full_model_card", m.get("description", ""))
            
            if isinstance(title, str) and isinstance(content, str):
                metadata.append({
                    "title": title,
                    "content": content
                })

        try:
            results = scrapegraphai_handler(
                query=query,
                mode=mode,
                metadata=metadata,
                model=model
            )
            
            if not isinstance(results, list):
                logger.warning("Handler returned non-list; coercing to empty list.")
                return []
            
            return results
        except Exception as e:
            logger.error("deep_scrape_models_with_llm: handler failed: %s", e)
            return []