from datetime import datetime, timezone
import hashlib
import json
import os
import re
import time
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from tqdm import tqdm

from .screenshots_handler import extract_text_from_posts
from .scrape_handlers import scrapegraphai_handler


class DiscussionScraperV2:
    def __init__(self, input_link: str = "titanic", output_dir: str = "data/discussions"):
        # Validate constructor inputs
        if not isinstance(input_link, str) or not input_link.strip():
            raise ValueError("input_link must be a non-empty string.")
        if not isinstance(output_dir, str) or not output_dir.strip():
            raise ValueError("output_dir must be a non-empty string.")
        
        self.input_link: str = input_link.strip()
        self.output_dir: str = output_dir
        self.competition_name: str = self.extract_competition_name()
        self.base_url: str = f"https://www.kaggle.com/c/{self.competition_name}/discussion"
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.data: List[Dict[str, Any]] = []
        # Use modern timezone-aware datetime
        self.timestamp: str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def extract_competition_name(self) -> str:
        """Extract competition name from URL or return input if already a name."""
        if not isinstance(self.input_link, str):
            raise TypeError("input_link must be a string")
        
        if "kaggle.com" in self.input_link:
            try:
                parsed = urlparse(self.input_link)
                parts = parsed.path.strip("/").split("/")
                if len(parts) >= 2 and parts[0] == "c":
                    return parts[1]
                raise ValueError("URL format not recognized as a Kaggle competition link.")
            except Exception as e:
                raise ValueError(f"Failed to parse URL: {e}")
        return self.input_link

    def setup_driver(self) -> None:
        """Setup Chrome WebDriver with error handling."""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
        except WebDriverException as e:
            raise RuntimeError(f"Failed to setup WebDriver: {e}")

    def close_driver(self) -> None:
        """Safely close WebDriver and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Warning: Error closing WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page with infinite loop protection."""
        if not self.driver:
            raise RuntimeError("Driver not initialized for scrolling")
        
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 50  # Prevent infinite loops
            
            while scroll_attempts < max_attempts:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
            
            if scroll_attempts >= max_attempts:
                print("Warning: Reached maximum scroll attempts, stopping")
            time.sleep(2)
        except Exception as e:
            raise RuntimeError(f"Error during scrolling: {e}")

    def get_post_hash(self, content: str) -> str:
        """Compute SHA256 hash of post content with validation."""
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_metadata_hash(self, title: str, author: str, date: str) -> str:
        """Compute SHA256 hash of post metadata with validation."""
        if not all(isinstance(x, str) for x in [title, author, date]):
            raise TypeError("title, author, and date must be strings")
        key = f"{title}{author}{date}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def split_markdown_blocks(self, content: str) -> List[str]:
        """Split content into markdown blocks with validation."""
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        return [block.strip() for block in content.split("\n\n") if block.strip()]

    def parse_post(self, post_element: Any, is_pinned: bool) -> Dict[str, Any]:
        """Parse a single discussion post element with comprehensive error handling."""
        if not post_element:
            raise ValueError("post_element cannot be None")
        if not isinstance(is_pinned, bool):
            raise TypeError("is_pinned must be a boolean")
        
        try:
            # Extract title
            title_el = post_element.find_element(By.CSS_SELECTOR, "h3")
            title = title_el.text.strip()
        except NoSuchElementException:
            title = "Unknown Title"
        
        try:
            # Extract content
            content_el = post_element.find_element(By.CSS_SELECTOR, "div.markdown")
            content = content_el.text.strip()
        except NoSuchElementException:
            content = ""
        
        try:
            # Extract author
            author_el = post_element.find_element(By.CSS_SELECTOR, "span.username")
            author = author_el.text.strip()
        except NoSuchElementException:
            author = "Unknown Author"
        
        try:
            # Extract date
            date_el = post_element.find_element(By.CSS_SELECTOR, "span.date")
            date = date_el.text.strip()
        except NoSuchElementException:
            date = "Unknown Date"
        
        # Generate post ID
        post_id = post_element.get_attribute("data-id") or f"{title}_{author}_{date}"
        
        # Check for screenshots safely
        try:
            has_screenshot = bool(re.search(r'!\[.*?\]\((.*?)\)', content))
        except Exception:
            has_screenshot = False

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

    def scrape(self, retries: int = 3, apply_ocr: bool = True) -> List[Dict[str, Any]]:
        """Main scraping method with comprehensive error handling and retry logic."""
        # Validate inputs
        if not isinstance(retries, int) or retries < 1:
            raise ValueError("retries must be a positive integer")
        if not isinstance(apply_ocr, bool):
            raise TypeError("apply_ocr must be a boolean")
        
        for attempt in range(1, retries + 1):
            try:
                self.setup_driver()
                self.driver.get(self.base_url)
                self.scroll_to_bottom()

                # Find pinned posts safely
                pinned_section = self.driver.find_elements(By.CSS_SELECTOR, "section.pinned-topics")
                pinned_posts = []
                if pinned_section:
                    try:
                        pinned_posts = pinned_section[0].find_elements(By.CSS_SELECTOR, "div.discussion-post")
                    except (IndexError, NoSuchElementException):
                        print("Warning: Could not find pinned posts section")
                
                # Find all posts
                all_posts = self.driver.find_elements(By.CSS_SELECTOR, "div.discussion-post")

                pinned_ids = set()
                # Process pinned posts
                for post in pinned_posts:
                    try:
                        parsed = self.parse_post(post, is_pinned=True)
                        pinned_ids.add(parsed["post_id"])
                        self.data.append(parsed)
                    except Exception as e:
                        print(f"Warning: Failed to parse pinned post: {e}")

                # Process all posts with progress bar
                try:
                    for post in tqdm(all_posts, desc="Scraping unpinned discussion posts"):
                        try:
                            parsed = self.parse_post(post, is_pinned=False)
                            if parsed["post_id"] not in pinned_ids:
                                self.data.append(parsed)
                        except Exception as e:
                            print(f"Warning: Failed to parse unpinned post: {e}")
                except Exception as e:
                    print(f"Warning: Error during progress bar processing: {e}")

                self.close_driver()

                # Apply OCR if requested
                if apply_ocr:
                    try:
                        print("Info: Applying OCR to posts with screenshots...")
                        self.data = extract_text_from_posts(self.data)
                    except Exception as e:
                        print(f"Warning: OCR processing failed: {e}")

                return self.data
            except Exception as e:
                print(f"Error: Attempt {attempt} failed: {e}")
                self.close_driver()
                if attempt == retries:
                    raise
        return []
    
    
    def save_to_json(self) -> str:
        """Save scraped data to JSON file with error handling."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            out_path = os.path.join(self.output_dir, f"{self.competition_name}_discussions.json")
            
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            print(f"Info: Saved {len(self.data)} discussions to {out_path}")
            return out_path
        except OSError as e:
            raise RuntimeError(f"Failed to save discussions to JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error saving discussions: {e}")

    def load_from_json(self) -> List[Dict[str, Any]]:
        """Load previously scraped data from JSON file with error handling."""
        out_path = os.path.join(self.output_dir, f"{self.competition_name}_discussions.json")
        
        if not os.path.exists(out_path):
            print(f"Warning: Discussion file not found: {out_path}")
            return []
        
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print(f"Error: Expected list in JSON file, got {type(data).__name__}")
                return []
            
            self.data = data
            print(f"Info: Loaded {len(self.data)} discussions from {out_path}")
            return self.data
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON file {out_path}: {e}")
        except OSError as e:
            raise RuntimeError(f"Failed to read file {out_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading discussions: {e}")
    
    def parse(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a deeply scraped discussion post into a standardized format."""
        if not isinstance(item, dict):
            raise TypeError("item must be a dictionary")
        
        return {
            "title": str(item.get("title", "")),
            "url": None,  # Kaggle discussions don't expose direct URLs without JS
            "section": str(item.get("section", "discussion")),
            "relevance_score": item.get("relevance_score", None),
            "metadata": {
                "post_id": item.get("post_id"),
                "post_hash": item.get("post_hash"),
                "metadata_hash": item.get("metadata_hash"),
                "has_screenshot": item.get("has_screenshot", False),
                "ocr_extracted": bool(item.get("ocr_text", "")) if "ocr_text" in item else False,
                "last_scraped": item.get("last_scraped"),
            },
            "content": str(item.get("ocr_text", item.get("content", ""))),
        }

    def get_all_cleaned_discussions(self) -> List[Dict[str, Any]]:
        """Get all discussion posts, loading from file if not in memory."""
        if not self.data:
            self.load_from_json()
        return self.data
    
    def deep_scrape_discussion(self, query: str, mode: str = "summary", model: str = "codellama:13b") -> List[Dict[str, Any]]:
        """Perform AI-powered deep scraping on discussion posts using ScrapeGraphAI."""
        # Validate inputs
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(mode, str) or not mode.strip():
            raise ValueError("mode must be a non-empty string")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a non-empty string")
        
        try:
            posts = self.get_all_cleaned_discussions()
            
            # Safe metadata creation with key validation
            metadata = []
            for p in posts:
                if not isinstance(p, dict):
                    continue
                
                title = p.get("title", "")
                content = p.get("ocr_text", p.get("content", ""))
                
                if isinstance(title, str) and isinstance(content, str):
                    metadata.append({
                        "title": title,
                        "content": content
                    })

            results = scrapegraphai_handler(
                query=query,
                mode=mode,
                metadata=metadata,
                model=model
            )
            
            if not isinstance(results, list):
                print("Warning: Handler returned non-list; coercing to empty list.")
                return []
            
            return results
        except Exception as e:
            raise RuntimeError(f"Deep scraping failed: {e}")