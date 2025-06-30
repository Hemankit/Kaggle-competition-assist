import time
import requests
import re
import logging
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from tqdm import tqdm

from scraper.screenshots_handler import extract_text_from_posts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscussionScraper:
    def __init__(self, input_link: str):
        self.input_link = input_link.strip()
        self.competition_name = ""
        self.base_url = ""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.driver = None
        self.wait = None
        self.setup_url()

    def setup_url(self):
        if "kaggle.com" in self.input_link:
            parsed = urlparse(self.input_link)
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "c":
                self.competition_name = parts[1]
            else:
                raise ValueError("URL format not recognized as a Kaggle competition link.")
        else:
            self.competition_name = self.input_link
        self.base_url = f"https://www.kaggle.com/c/{self.competition_name}/discussion"

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

    def scrape_discussion_data(self, retries: int = 3, apply_ocr: bool = True) -> list:
        scraped_data = []
        for attempt in range(1, retries + 1):
            try:
                self.setup_driver()
                self.driver.get(self.base_url)
                self.scroll_to_bottom()

                pinned_posts = self.driver.find_elements(By.CSS_SELECTOR, "div.discussion-post.pinned")
                if not pinned_posts:
                    pinned_section = self.driver.find_elements(By.CSS_SELECTOR, "section.pinned-topics")
                    if pinned_section:
                        pinned_posts = pinned_section[0].find_elements(By.CSS_SELECTOR, "div.discussion-post")

                all_posts = self.driver.find_elements(By.CSS_SELECTOR, "div.discussion-post")
                pinned_ids = set()

                for post in pinned_posts:
                    try:
                        title = post.find_element(By.CSS_SELECTOR, "h3").text
                        content = post.find_element(By.CSS_SELECTOR, "div.markdown").text
                        author = post.find_element(By.CSS_SELECTOR, "span.username").text
                        date = post.find_element(By.CSS_SELECTOR, "span.date").text
                        has_screenshot = bool(re.search(r'!\[.*?\]\((.*?)\)', content))
                        post_id = post.get_attribute("data-id") or title + author + date
                        pinned_ids.add(post_id)
                        scraped_data.append({
                            "title": title,
                            "content": content,
                            "author": author,
                            "date": date,
                            "has_screenshot": has_screenshot,
                            "is_pinned": True,
                            "post_id": post_id
                        })
                    except Exception as e:
                        logger.warning("Error extracting pinned post: %s", e)

                for post in tqdm(all_posts, desc="Scraping discussion posts", unit="post"):
                    try:
                        title = post.find_element(By.CSS_SELECTOR, "h3").text
                        content = post.find_element(By.CSS_SELECTOR, "div.markdown").text
                        author = post.find_element(By.CSS_SELECTOR, "span.username").text
                        date = post.find_element(By.CSS_SELECTOR, "span.date").text
                        has_screenshot = bool(re.search(r'!\[.*?\]\((.*?)\)', content))
                        post_id = post.get_attribute("data-id") or title + author + date
                        if post_id in pinned_ids:
                            continue
                        scraped_data.append({
                            "title": title,
                            "content": content,
                            "author": author,
                            "date": date,
                            "has_screenshot": has_screenshot,
                            "is_pinned": False,
                            "post_id": post_id
                        })
                    except Exception as e:
                        logger.warning("Error extracting post: %s", e)

                self.close_driver()

                if apply_ocr:
                    logger.info("Applying OCR to posts with screenshots...")
                    scraped_data = extract_text_from_posts(scraped_data)

                return scraped_data

            except Exception as e:
                logger.error("Attempt %d failed: %s", attempt, e)
                self.close_driver()
                if attempt == retries:
                    raise
        return scraped_data
