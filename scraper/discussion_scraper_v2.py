from datetime import datetime
import hashlib
import json
import os
import re
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
from tqdm import tqdm

from scraper.screenshots_handler import extract_text_from_posts
from scrape_handlers import scrapegraphai_handler


class DiscussionScraperV2:
    def __init__(self, input_link: str, output_dir: str = "data/discussions"):
        self.input_link = input_link.strip()
        self.output_dir = output_dir
        self.competition_name = self.extract_competition_name()
        self.base_url = f"https://www.kaggle.com/c/{self.competition_name}/discussion"
        self.driver = None
        self.wait = None
        self.data = []
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def extract_competition_name(self):
        if "kaggle.com" in self.input_link:
            parsed = urlparse(self.input_link)
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "c":
                return parts[1]
            raise ValueError("URL format not recognized as a Kaggle competition link.")
        return self.input_link

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

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        time.sleep(2)

    def get_post_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_metadata_hash(self, title: str, author: str, date: str) -> str:
        key = f"{title}{author}{date}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def split_markdown_blocks(self, content: str):
        # Simple paragraph split for markdown blocks
        return [block.strip() for block in content.split("\n\n") if block.strip()]

    def parse_post(self, post_element, is_pinned: bool):
        title = post_element.find_element(By.CSS_SELECTOR, "h3").text
        content = post_element.find_element(By.CSS_SELECTOR, "div.markdown").text
        author = post_element.find_element(By.CSS_SELECTOR, "span.username").text
        date = post_element.find_element(By.CSS_SELECTOR, "span.date").text
        post_id = post_element.get_attribute("data-id") or f"{title}_{author}_{date}"
        has_screenshot = bool(re.search(r'!\[.*?\]\((.*?)\)', content))

        return {
            "title": title,
            "author": author,
            "content": content,
            "markdown_blocks": self.split_markdown_blocks(content),
            "post_id": post_id,
            "post_hash": self.get_post_hash(content),
            "metadata_hash": self.get_metadata_hash(title, author, date),
            "date": date,
            "has_screenshot": has_screenshot,
            "is_pinned": is_pinned,
            "section": "discussion.pinned" if is_pinned else "discussion.unpinned",
            "last_scraped": self.timestamp,
            "upvotes": None  # Future use
        }

    def scrape(self, retries=3, apply_ocr=True):
        for attempt in range(1, retries + 1):
            try:
                self.setup_driver()
                self.driver.get(self.base_url)
                self.scroll_to_bottom()

                pinned_section = self.driver.find_elements(By.CSS_SELECTOR, "section.pinned-topics")
                pinned_posts = pinned_section[0].find_elements(By.CSS_SELECTOR, "div.discussion-post") if pinned_section else []
                all_posts = self.driver.find_elements(By.CSS_SELECTOR, "div.discussion-post")

                pinned_ids = set()
                for post in pinned_posts:
                    try:
                        parsed = self.parse_post(post, is_pinned=True)
                        pinned_ids.add(parsed["post_id"])
                        self.data.append(parsed)
                    except Exception as e:
                        print(f"[WARN] Failed to parse pinned post: {e}")

                for post in tqdm(all_posts, desc="Scraping unpinned discussion posts"):
                    try:
                        parsed = self.parse_post(post, is_pinned=False)
                        if parsed["post_id"] not in pinned_ids:
                            self.data.append(parsed)
                    except Exception as e:
                        print(f"[WARN] Failed to parse unpinned post: {e}")

                self.close_driver()

                if apply_ocr:
                    print("[INFO] Applying OCR to posts with screenshots...")
                    self.data = extract_text_from_posts(self.data)

                return self.data
            except Exception as e:
                print(f"[ERROR] Attempt {attempt} failed: {e}")
                self.close_driver()
                if attempt == retries:
                    raise
        return []
    
    
    def save_to_json(self):
        os.makedirs(self.output_dir, exist_ok=True)
        out_path = os.path.join(self.output_dir, f"{self.competition_name}_discussions.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        return out_path

    def load_from_json(self):
        out_path = os.path.join(self.output_dir, f"{self.competition_name}_discussions.json")
        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        return self.data
    
    def parse(self, item: dict) -> dict:
        """
        Convert a deeply scraped discussion post into a standardized format.
        """
        return {
        "title": item.get("title", ""),
        "url": None,  # Kaggle discussions don't expose direct URLs without JS
        "section": item.get("section", "discussion"),
        "relevance_score": item.get("relevance_score", None),
        "metadata": {
            "post_id": item.get("post_id"),
            "post_hash": item.get("post_hash"),
            "metadata_hash": item.get("metadata_hash"),
            "has_screenshot": item.get("has_screenshot"),
            "ocr_extracted": bool(item.get("ocr_text", "")) if "ocr_text" in item else False,
            "last_scraped": item.get("last_scraped"),
        },
        "content": item.get("ocr_text", item.get("content", "")),
    }

def get_all_cleaned_discussions(self) -> list:
    if not self.data:
        self.load_from_json()
    return self.data
    
def deep_scrape_discussion(self, query: str, mode: str = "summary", model: str = "codellama:13b") -> list:
    """
    Perform AI-powered deep scraping on discussion posts using ScrapeGraphAI.
    """
    posts = self.get_all_cleaned_discussions()
    metadata = [{"title": p["title"], "content": p.get("ocr_text", p["content"])} for p in posts]

    results = scrapegraphai_handler(
        query=query,
        mode=mode,
        metadata=metadata,
        model=model
    )
    return results