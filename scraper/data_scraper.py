"""
Kaggle Competition Data Section Scraper
----------------------------------------
Scrapes the Data page of a Kaggle competition to extract:
- Data description
- File information
- Column descriptions
- Data schema details

Uses Playwright for dynamic content rendering.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import time


class DataSectionScraper:
    """Scraper for Kaggle competition data section."""
    
    BASE_URL = "https://www.kaggle.com/competitions/{competition}/data"
    
    def __init__(self, competition_slug: str, headless: bool = True):
        """
        Initialize scraper for competition data page.
        
        Args:
            competition_slug: Competition identifier (e.g., 'titanic')
            headless: Run browser in headless mode
        """
        if not competition_slug or not isinstance(competition_slug, str):
            raise ValueError("competition_slug must be a non-empty string")
        
        self.competition_slug = competition_slug.replace(
            'https://www.kaggle.com/competitions/', ''
        )
        self.url = self.BASE_URL.format(competition=self.competition_slug)
        self.headless = headless
    
    def scrape_data_description(self) -> Dict[str, Any]:
        """
        Scrape the data section and return structured information.
        
        Returns:
            Dict containing:
                - description: Main data description text
                - sections: Dict of section titles and content
                - file_descriptions: List of file-specific descriptions
        """
        print(f"[DataScraper] Scraping data page for '{self.competition_slug}'...")
        
        try:
            html = self._get_rendered_html()
            if not html:
                return self._empty_result()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            result = {
                "competition": self.competition_slug,
                "description": self._extract_main_description(soup),
                "sections": self._extract_sections(soup),
                "file_descriptions": self._extract_file_descriptions(soup),
                "column_info": self._extract_column_info(soup),
                "scraped": True
            }
            
            print(f"[DataScraper] Successfully scraped data description")
            return result
        
        except Exception as e:
            print(f"[DataScraper] Error scraping data page: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_result()
    
    def _get_rendered_html(self) -> str:
        """Get fully rendered HTML using Playwright."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                page.set_viewport_size({"width": 1920, "height": 1080})
                
                print(f"[DataScraper] Loading {self.url}")
                page.goto(self.url, timeout=60000, wait_until="networkidle")
                
                # Wait for main content
                try:
                    page.wait_for_selector(
                        "main, div[role='main'], .site-content",
                        timeout=15000
                    )
                except Exception as e:
                    print(f"[DataScraper] Timeout waiting for content: {e}")
                
                # Give time for lazy loading
                time.sleep(2)
                
                html = page.content()
                browser.close()
                
                return html
        
        except Exception as e:
            print(f"[DataScraper] Error getting HTML: {e}")
            return ""
    
    def _extract_main_description(self, soup: BeautifulSoup) -> str:
        """Extract the main data description text."""
        # Try multiple selectors for main content
        selectors = [
            'div[class*="markdown"]',
            'div[class*="description"]',
            'div[class*="data-description"]',
            'div[class*="about"]',
            'main div p',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # Get text from all matching elements
                texts = []
                for elem in elements[:5]:  # Limit to first 5
                    text = elem.get_text(separator="\n", strip=True)
                    if len(text) > 50:  # Must be substantial
                        texts.append(text)
                
                if texts:
                    return "\n\n".join(texts)
        
        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            texts = [p.get_text(strip=True) for p in paragraphs[:10]]
            texts = [t for t in texts if len(t) > 30]
            return "\n\n".join(texts)
        
        return "No description available"
    
    def _extract_sections(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract organized sections (Files, Columns, etc.)."""
        sections = {}
        
        # Find headers (h2, h3, h4)
        headers = soup.find_all(['h2', 'h3', 'h4'])
        
        for header in headers:
            title = header.get_text(strip=True)
            if not title or len(title) < 3:
                continue
            
            # Get content after this header
            content_parts = []
            current = header.find_next_sibling()
            
            # Collect content until next header or max 5 elements
            count = 0
            while current and count < 5:
                if current.name in ['h2', 'h3', 'h4']:
                    break
                
                text = current.get_text(strip=True)
                if text and len(text) > 20:
                    content_parts.append(text)
                
                current = current.find_next_sibling()
                count += 1
            
            if content_parts:
                sections[title] = "\n\n".join(content_parts)
        
        return sections
    
    def _extract_file_descriptions(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract file-specific descriptions."""
        file_descriptions = []
        
        # Look for file names (common patterns: train.csv, test.csv, etc.)
        file_patterns = ['train', 'test', 'sample', 'submission', '.csv', '.json']
        
        # Find elements that mention files
        for elem in soup.find_all(['p', 'li', 'div']):
            text = elem.get_text(strip=True)
            
            # Check if this element mentions a file
            if any(pattern in text.lower() for pattern in file_patterns):
                # Try to extract file name and description
                if ':' in text:
                    parts = text.split(':', 1)
                    file_descriptions.append({
                        "file": parts[0].strip(),
                        "description": parts[1].strip()
                    })
                elif '-' in text and len(text) < 200:
                    parts = text.split('-', 1)
                    file_descriptions.append({
                        "file": parts[0].strip(),
                        "description": parts[1].strip() if len(parts) > 1 else ""
                    })
        
        return file_descriptions[:10]  # Limit to top 10
    
    def _extract_column_info(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract column/feature descriptions."""
        column_info = []
        
        # Look for lists or tables describing columns
        # Common format: "column_name - description" or "column_name: description"
        
        # Try list items first
        list_items = soup.find_all('li')
        for li in list_items:
            text = li.get_text(strip=True)
            
            # Check if this looks like a column description
            if (':' in text or '-' in text) and len(text) < 300:
                # Split on : or -
                separator = ':' if ':' in text else '-'
                parts = text.split(separator, 1)
                
                if len(parts) == 2:
                    column_name = parts[0].strip()
                    description = parts[1].strip()
                    
                    # Validate it looks like a column name (not too long)
                    if len(column_name) < 50 and len(column_name) > 2:
                        column_info.append({
                            "column": column_name,
                            "description": description
                        })
        
        # Try table rows
        if not column_info:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        column_info.append({
                            "column": cells[0].get_text(strip=True),
                            "description": cells[1].get_text(strip=True)
                        })
        
        return column_info[:20]  # Limit to top 20 columns
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "competition": self.competition_slug,
            "description": "",
            "sections": {},
            "file_descriptions": [],
            "column_info": [],
            "scraped": False
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    
    competition = sys.argv[1] if len(sys.argv) > 1 else "titanic"
    
    print("=" * 70)
    print(f"DATA SECTION SCRAPER TEST: {competition}")
    print("=" * 70)
    
    scraper = DataSectionScraper(competition)
    result = scraper.scrape_data_description()
    
    print(f"\n✅ Competition: {result['competition']}")
    print(f"✅ Scraped: {result['scraped']}")
    
    print("\n" + "=" * 70)
    print("MAIN DESCRIPTION")
    print("=" * 70)
    print(result['description'][:500])
    if len(result['description']) > 500:
        print("...")
    
    print("\n" + "=" * 70)
    print(f"SECTIONS ({len(result['sections'])})")
    print("=" * 70)
    for title, content in result['sections'].items():
        print(f"\n--- {title} ---")
        print(content[:200])
        if len(content) > 200:
            print("...")
    
    print("\n" + "=" * 70)
    print(f"FILE DESCRIPTIONS ({len(result['file_descriptions'])})")
    print("=" * 70)
    for file_desc in result['file_descriptions']:
        print(f"- {file_desc['file']}: {file_desc['description'][:100]}")
    
    print("\n" + "=" * 70)
    print(f"COLUMN INFO ({len(result['column_info'])})")
    print("=" * 70)
    for col in result['column_info'][:10]:
        print(f"- {col['column']}: {col['description'][:80]}")
    
    print("\n" + "=" * 70)




