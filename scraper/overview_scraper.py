from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import Dict, Any
import time


class OverviewScraper:
    """
    Kaggle Competition Overview Scraper (Playwright version)
    --------------------------------------------------------
    Loads and extracts the Overview page (Description, Evaluation,
    Timeline, Submission File, etc.) and returns both text and markdown.
    """

    BASE_URL = "https://www.kaggle.com/competitions/{competition}/overview"

    def __init__(self, competition_name: str, headless: bool = True):
        if not competition_name or not isinstance(competition_name, str):
            raise ValueError("competition_name must be a non-empty string.")
        self.competition_name = competition_name
        self.url = self.BASE_URL.format(competition=competition_name)
        self.headless = headless

    def _get_rendered_html(self) -> str:
        """Launch Playwright browser, navigate, and get the fully rendered HTML."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(self.url, timeout=60000, wait_until="networkidle")

            # Wait for any of these selectors to appear (Kaggle uses different structures)
            try:
                page.wait_for_selector("main, div[role='main'], .site-content, body > div", timeout=15000)
            except Exception as e:
                print(f"Warning: Timeout waiting for main content, proceeding anyway: {e}")
            
            # Give extra time for lazy-loaded subcomponents
            time.sleep(3)
            html = page.content()
            browser.close()
            return html

    def _parse_overview_sections(self, html: str) -> Dict[str, Dict[str, str]]:
        """Parse HTML and extract structured overview sections."""
        soup = BeautifulSoup(html, "html.parser")
        
        sections = {}
        
        # Find all h2/h3/h4 headers
        headers = soup.find_all(['h2', 'h3', 'h4'])
        
        for header in headers:
            title = header.get_text(strip=True)
            if not title:
                continue
            
            # Kaggle nests headers deeply. Content is in sibling divs several levels up.
            # Navigate up the DOM tree to find the container with content siblings
            content_elements = []
            current = header
            
            for level in range(8):  # Try up to 8 levels up
                if not current.parent:
                    break
                current = current.parent
                
                # Check if this level has content siblings
                siblings = current.find_next_siblings()
                if siblings:
                    # Look for div siblings with substantial content
                    for sibling in siblings:
                        text = sibling.get_text(strip=True)
                        # If this sibling has meaningful content (> 50 chars), use it
                        if len(text) > 50:
                            content_elements.append(sibling)
                            break
                    
                    if content_elements:
                        break
            
            # Extract text and html from found content
            if content_elements:
                text_content = "\n\n".join([elem.get_text(separator="\n", strip=True) for elem in content_elements])
                html_content = "\n\n".join([str(elem) for elem in content_elements])
            else:
                text_content = ""
                html_content = ""
            
            sections[title] = {
                "text": text_content.strip(),
                "markdown": html_content.strip()
            }

        return sections

    def scrape(self) -> Dict[str, Any]:
        """Scrape and return structured Kaggle overview data."""
        print(f"Scraping Kaggle overview for '{self.competition_name}' using Playwright...")
        html = self._get_rendered_html()
        overview_sections = self._parse_overview_sections(html)
        return {
            "competition_name": self.competition_name,
            "overview_sections": overview_sections,
        }


# --- Example usage ---
if __name__ == "__main__":
    scraper = OverviewScraper("titanic")
    data = scraper.scrape()

    print(f"\n✅ Competition: {data['competition_name']}")
    print("=" * 80)
    for section, content in data["overview_sections"].items():
        print(f"\n--- {section} ---")
        print("TEXT PREVIEW:\n", content["text"][:400], "...")
        print("\nMARKDOWN PREVIEW:\n", content["markdown"][:400], "...")
  # show first 500 characters of each section

            
        

    