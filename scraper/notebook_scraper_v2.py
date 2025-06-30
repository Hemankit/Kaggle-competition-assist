import os
import json
import hashlib
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from scrape_handlers import scrapegraphai_handler

logging.basicConfig(level=logging.INFO)


class NotebookScraperV2:
    def __init__(self, metadata_path: str, save_path: str):
        self.metadata_path = metadata_path
        self.save_path = save_path
        self.cleaned_metadata: List[Dict] = []
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def load_metadata(self) -> List[Dict]:
        if not os.path.exists(self.metadata_path):
            logging.error(f"Metadata file not found: {self.metadata_path}")
            return []
        try:
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading JSON: {e}")
            return []

    def clean(self, raw_metadata: List[Dict]) -> List[Dict]:
        cleaned = []
        for item in raw_metadata:
            try:
                cleaned_item = {
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'author': item.get('author', ''),
                    'description': item.get('description', ''),
                    'tags': item.get('tags', []),
                    'url': item.get('url', ''),
                    'is_pinned': item.get('isPinned', False),
                    'votes': item.get('totalVotes', 0),
                    'comments': item.get('totalComments', 0),
                    'date_created': self.format_date(item.get('dateCreated')),
                    'date_modified': self.format_date(item.get('dateModified')),
                }
                cleaned.append(cleaned_item)
            except Exception as e:
                logging.warning(f"Skipping invalid item: {e}")
        return cleaned

    def format_date(self, date_str: Optional[str]) -> Optional[str]:
        if not date_str:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
        try:
            return datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            logging.warning(f"Invalid date format: {date_str}")
            return None

    def extract_blocks(self, content: str) -> Dict[str, List[str]]:
        code_pattern = re.compile(r'```(?:\w+)?\s*([\s\S]*?)```', re.MULTILINE)
        markdown_pattern = re.compile(r'```markdown\s*([\s\S]*?)```', re.MULTILINE)
        return {
            'code_blocks': [m.strip() for m in code_pattern.findall(content)],
            'markdown_blocks': [m.strip() for m in markdown_pattern.findall(content)]
        }

    def compute_hash(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def scrape(self) -> List[Dict]:
        raw_metadata = self.load_metadata()
        self.cleaned_metadata = self.clean(raw_metadata)
        enriched = []

        for item in self.cleaned_metadata:
            content = item.get("description", "")
            blocks = self.extract_blocks(content)
            combined_text = "\n".join(blocks['code_blocks'] + blocks['markdown_blocks'])

            content_hash = hashlib.sha256(
            f"{item['title']}{item['author']}{item['date_created']}".encode()
        ).hexdigest()

        enriched.append({
        'id': item['id'],
        'title': item['title'],
        'code_blocks': blocks['code_blocks'],
        'markdown_blocks': blocks['markdown_blocks'],
        'notebook_hash': self.compute_hash(combined_text),
        'metadata_hash': content_hash,
        'section': 'code.pinned' if item.get('is_pinned') else 'code.unpinned',
        'last_scraped': self.timestamp,
        'notebook_score': None
    })
        return enriched
    

    def fetch_html(self, url: str) -> str:
        """
        Fetch the HTML content of a Kaggle notebook.
        """
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def extract_markdown_blocks_from_html(self, html: str) -> List[str]:
        """
        Parse notebook HTML and extract markdown cell content only.
        """
        soup = BeautifulSoup(html, "html.parser")
        markdown_cells = []

        for div in soup.find_all("div", class_="markdown"):
            text = div.get_text(separator="\n", strip=True)
            if text:
                markdown_cells.append(text)
        return markdown_cells
    
    def get_all_cleaned_notebooks(self) -> List[Dict]:
        """
        Return cleaned metadata for all notebooks. Lazily loads and cleans if not already done.
        """
        if not self.cleaned_metadata:
            raw_metadata = self.load_metadata()
            self.cleaned_metadata = self.clean(raw_metadata)
        return self.cleaned_metadata

    def save_to_file(self, data: Optional[List[Dict]] = None):
        if data is None:
            data = self.scrape()
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        try:
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Saved {len(data)} notebooks to {self.save_path}")
        except Exception as e:
            logging.error(f"Failed to save file: {e}")

    def parse(self, item: Dict) -> Dict:
        """
        Convert a deeply scraped notebook item into a standardized format.
        """
        return {
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "section": item.get("section", "code"),
        "relevance_score": item.get("relevance_score", None),
        "metadata": {
            "notebook_hash": item.get("notebook_hash"),
            "last_scraped": item.get("last_scraped"),
        },
        "content": "\n\n".join(item.get("markdown_blocks", [])),
    }

    def deep_scrape_notebooks(self, query: str, mode: str = "summary", model: str = "codellama:13b") -> List[Dict[str, Any]]:
        """
        Perform AI-powered deep scraping on notebooks using ScrapeGraphAI.
        """
        notebooks = self.get_all_cleaned_notebooks()
        metadata = [{"url": n["url"], "title": n["title"]} for n in notebooks if n.get("url")]

        results = scrapegraphai_handler(
        query=query,
        mode=mode,
        metadata=metadata,
        model=model
    )
        return results