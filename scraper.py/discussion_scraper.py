import time
import requests
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from tqdm import tqdm


class DiscussionScraper:
    def __init__(self, input_link: str):
        """
        Accepts either a Kaggle competition name (slug) or full discussion URL.
        """
        self.input_link = input_link.strip()
        self.competition_name = ""
        self.base_url = ""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })
        self.driver = None
        self.wait = None
        self.setup_url()

    def setup_url(self):
        """
        Normalizes the input into a proper discussion page URL.
        """
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
        """
        Sets up the Selenium WebDriver.
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def close_driver(self):
        """
        Closes the Selenium WebDriver.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None

    def scroll_to_bottom(self):
        """
        Scrolls to the bottom of the page to load all discussion posts.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        time.sleep(2)

    def scrape_discussion_data(self, retries: int = 3) -> list:
        """
        Scrapes discussion posts from the competition page with retry logic.

        Returns:
            list: List of dictionaries with discussion post data.
        """
        scraped_data = []
        for attempt in range(1, retries + 1):
            try:
                self.setup_driver()
                self.driver.get(self.base_url)
                self.scroll_to_bottom()
                posts = self.driver.find_elements(By.CSS_SELECTOR, "div.discussion-post")

                for post in tqdm(posts, desc="Scraping discussion posts", unit="post"):
                    try:
                        title = post.find_element(By.CSS_SELECTOR, "h3").text
                        content = post.find_element(By.CSS_SELECTOR, "div.markdown").text
                        author = post.find_element(By.CSS_SELECTOR, "span.username").text
                        date = post.find_element(By.CSS_SELECTOR, "span.date").text
                        has_screenshot = bool(re.search(r'!\[.*?\]\((.*?)\)', content))
                        scraped_data.append({
                            "title": title,
                            "content": content,
                            "author": author,
                            "date": date,
                            "has_screenshot": has_screenshot
                            })

                    except Exception as e:
                        print(f"Error extracting post content: {e}")

                break  # Exit retry loop if successful
            except (TimeoutException, WebDriverException) as e:
                print(f"[Attempt {attempt}/{retries}] Error: {e}")
                time.sleep(2)
            finally:
                self.close_driver()

        if not scraped_data:
            print("No discussion data scraped after retries.")
        return scraped_data

    def scrape(self) -> list:
        """
        Main method to scrape discussions.
        Returns:
            list: List of discussion post dictionaries.
        """
        print(f"Scraping discussions for: {self.competition_name}")
        return self.scrape_discussion_data()
    
    


if __name__ == "__main__":
    input_link = "https://www.kaggle.com/c/stanford-ribonanza-rna-folding/discussion"
    scraper = DiscussionScraper(input_link)
    data = scraper.scrape()

    # Print posts with screenshots
    screenshot_posts = [post for post in data if post.get("has_screenshot")]
    print(f"\n[INFO] Found {len(screenshot_posts)} posts with screenshots:\n")
    for post in screenshot_posts[:5]:  # Limit preview
        print(f"- {post['title']} by {post['author']}")
    
