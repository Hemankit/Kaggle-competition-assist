import os
import json
import hashlib
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import re
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from .scrape_handlers import scrapegraphai_handler

logger = logging.getLogger(__name__)


class NotebookScraperV2:
    def __init__(self, metadata_path: str = "data/notebooks_metadata.json", save_path: str = "data/notebooks_scraped.json"):
        # Validate constructor inputs (Fixes #2)
        if not isinstance(metadata_path, str) or not metadata_path.strip():
            raise ValueError("metadata_path must be a non-empty string.")
        if not isinstance(save_path, str) or not save_path.strip():
            raise ValueError("save_path must be a non-empty string.")

        self.metadata_path = metadata_path
        self.save_path = save_path
        # Correct type annotation for safety (Fix #3)
        self.cleaned_metadata: List[Dict[str, Any]] = []
        # Safe UTC timestamp (Fix #4)
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # ---- I/O & Metadata ----

    def load_metadata(self) -> List[Dict[str, Any]]:
        """Load raw metadata from JSON file with UTF-8 and validation."""
        # metadata_path is already validated in constructor, so no need to check again
        if not os.path.exists(self.metadata_path):
            logger.error("Metadata file not found: %s", self.metadata_path)
            return []
        try:
            # Specify encoding (Fix #6)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                logger.error("Metadata JSON root should be a list, got %s", type(data).__name__)
                return []
            return data
        except json.JSONDecodeError as e:
            logger.error("Error parsing metadata JSON: %s", e)
            return []
        except OSError as e:
            logger.error("Error reading metadata file: %s", e)
            return []

    def save_to_file(self, data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save processed/enriched data to disk (UTF-8, safe dirs)."""
        # Validate input data list (Fix #24)
        if data is None:
            data = self.scrape()
        if not isinstance(data, list):
            logger.error("save_to_file expected a list, got %s", type(data).__name__)
            return

        dirpath = os.path.dirname(self.save_path)
        # Handle case when only filename is given (Fix #25)
        if dirpath:
            try:
                os.makedirs(dirpath, exist_ok=True)
            except OSError as e:
                logger.error("Failed to create directory '%s': %s", dirpath, e)
                return
        try:
            # Specify encoding (Fix #26)
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Saved %d notebooks to %s", len(data), self.save_path)
        except OSError as e:
            logger.error("Failed to save file '%s': %s", self.save_path, e)

    # ---- Cleaning & Normalization ----

    def clean(self, raw_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize raw notebook metadata into a safe, typed structure.
        Skips invalid entries but logs context.
        """
        # Validate input (Fixes #7, #8)
        if not isinstance(raw_metadata, list):
            logger.error("Expected raw_metadata to be a list, got %s", type(raw_metadata).__name__)  # pyright: ignore[reportUnreachable]
            return []  # pyright: ignore[reportUnreachable]

        cleaned: List[Dict[str, Any]] = []

        for idx, item in enumerate(raw_metadata):
            # Guard against non-dict items (Fix #9)
            if not isinstance(item, dict):
                logger.warning("Skipping non-dict item at index %d: %r", idx, item)
                continue

            try:
                cleaned_item: Dict[str, Any] = {
                    "id": item.get("id") or f"missing_id_{idx}",
                    "title": str(item.get("title") or ""),
                    "author": str(item.get("author") or ""),
                    "description": str(item.get("description") or ""),
                    "tags": item.get("tags") if isinstance(item.get("tags"), list) else [],
                    "url": str(item.get("url") or ""),
                    "is_pinned": bool(item.get("isPinned", False)),
                    "votes": int(item.get("totalVotes") or 0),
                    "comments": int(item.get("totalComments") or 0),
                    "date_created": self.format_date(item.get("dateCreated")),
                    "date_modified": self.format_date(item.get("dateModified")),
                }
                cleaned.append(cleaned_item)
            except Exception as e:
                logger.warning(
                    "Skipping invalid item at index %d due to error: %s | item=%r",
                    idx, e, item
                )
        return cleaned

    def format_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse various Kaggle-like ISO dates to a consistent format."""
        # Validate input presence/type (Fix #10)
        if not date_str or not isinstance(date_str, str):
            return None

        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            logger.warning("Invalid date format: %s", date_str)
            return None

    # ---- Filtering & Sorting ----

    def filter_metadata(
        self,
        metadata: List[Dict[str, Any]],
        min_upvotes: int = 0,
        max_days_old: Optional[int] = None,
        custom_filter_fn: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generic filter for code notebooks based on upvotes, recency, or a custom function.
        """
        if not isinstance(metadata, list):
            logger.error("filter_metadata expected a list, got %s", type(metadata).__name__)
            return []

        filtered = []
        now = datetime.now(timezone.utc)
        
        for item in metadata:
            if not isinstance(item, dict):
                continue
                
            votes = item.get('votes', 0)
            date_str = item.get('date_created', '')
            
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                # Make timezone-aware for comparison
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                days_old = (now - dt).days
            except Exception:
                days_old = None

            if votes < min_upvotes:
                continue
            if max_days_old is not None and (days_old is None or days_old > max_days_old):
                continue
            if custom_filter_fn and callable(custom_filter_fn) and not custom_filter_fn(item):
                continue
            filtered.append(item)
        
        return filtered

    def sort_by(
        self,
        notebooks: List[Dict[str, Any]],
        key: str,
        reverse: bool = True
    ) -> List[Dict[str, Any]]:
        """Sort a given list of notebooks by any metadata key."""
        if not isinstance(notebooks, list):
            logger.error("sort_by expected a list, got %s", type(notebooks).__name__)
            return notebooks
            
        try:
            return sorted(notebooks, key=lambda x: x.get(key, 0) or 0, reverse=reverse)
        except Exception as e:
            logger.error("Sorting failed: %s", e)
            return notebooks

    # ---- Content Extraction & Hashing ----

    def extract_blocks(self, content: str) -> Dict[str, List[str]]:
        """
        Extract fenced code and fenced markdown blocks from a text blob.
        Returns dict with 'code_blocks' and 'markdown_blocks' lists.
        """
        # Validate input (Fix #11)
        if not isinstance(content, str):
            logger.warning("extract_blocks expected a string, got %s", type(content).__name__)
            return {"code_blocks": [], "markdown_blocks": []}

        # Efficient regex using DOTALL instead of [\\s\\S] (Fix #12)
        code_pattern = re.compile(r"```(?:\w+)?\s*(.*?)```", re.MULTILINE | re.DOTALL)
        markdown_pattern = re.compile(r"```markdown\s*(.*?)```", re.MULTILINE | re.DOTALL)

        code_blocks = [m.strip() for m in code_pattern.findall(content)]
        md_blocks = [m.strip() for m in markdown_pattern.findall(content)]

        return {"code_blocks": code_blocks, "markdown_blocks": md_blocks}

    def compute_hash(self, text: str) -> str:
        """Compute an md5 hash of text with safety checks (Fix #13)."""
        if not isinstance(text, str):
            logger.warning("compute_hash expected string, got %s; coercing to str", type(text).__name__)
            text = str(text)
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    # ---- High-Level Orchestration ----

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Load metadata, clean it, extract blocks, and build enriched items.
        """
        raw_metadata = self.load_metadata()
        # load_metadata() already validates and returns empty list if not a list
        self.cleaned_metadata = self.clean(raw_metadata)
        enriched: List[Dict[str, Any]] = []

        for item in self.cleaned_metadata:
            # Protect against malformed dicts (Fix #14)
            if not isinstance(item, dict):
                logger.warning("Skipping non-dict metadata item: %r", item)
                continue

            content = item.get("description", "") or ""
            if not isinstance(content, str):
                logger.warning("Skipping item with invalid description type: %r", type(content).__name__)
                continue

            blocks = self.extract_blocks(content)
            # Guard list concatenation (Fix #15)
            code_list = blocks.get("code_blocks") if isinstance(blocks.get("code_blocks"), list) else []
            md_list = blocks.get("markdown_blocks") if isinstance(blocks.get("markdown_blocks"), list) else []
            combined_text = "\n".join(code_list + md_list)

            # Robust metadata hash (Fixes #16, #17)
            title = item.get("title") or ""
            author = item.get("author") or ""
            date_created = item.get("date_created") or ""
            try:
                content_hash = hashlib.sha256(f"{title}{author}{date_created}".encode("utf-8")).hexdigest()
            except Exception as e:
                logger.error("Failed to compute metadata hash: %s", e)
                content_hash = ""

            # Safe id/title access (Fix #19)
            enriched.append(
                {
                    "id": item.get("id"),
                    "title": title,
                    "code_blocks": code_list,
                    "markdown_blocks": md_list,
                    "notebook_hash": self.compute_hash(combined_text),
                    "metadata_hash": content_hash,
                    "section": "code.pinned" if item.get("is_pinned") else "code.unpinned",
                    "last_scraped": self.timestamp,
                    "notebook_score": None,
                }
            )

        return enriched

    # ---- HTML Fetch & Parse ----

    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of a Kaggle notebook.
        Returns HTML string if successful, None otherwise.
        """
        # Validate input (Fix #20)
        if not isinstance(url, str) or not url.strip():
            logger.error("Invalid URL provided: %r", url)
            return None

        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            # Network error handling + timeout (Fixes #21, #22)
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except RequestException as e:
            logger.error("Failed to fetch HTML from %s: %s", url, e)
            return None

    def extract_markdown_blocks_from_html(self, html: str) -> Dict[str, List[str]]:
        """
        Parse notebook HTML and extract:
          - 'markdown_text': raw text from markdown cells
          - 'code_blocks': fenced code inside those cells (for hybrid RAG)

        Returns a dict with both lists.
        """
        # Validate input (Fix #23)
        if not isinstance(html, str):
            logger.error("extract_markdown_blocks_from_html expected str, got %s", type(html).__name__)
            return {"markdown_text": [], "code_blocks": []}

        soup = BeautifulSoup(html, "html.parser")
        markdown_cells: List[str] = []
        code_blocks: List[str] = []

        for div in soup.find_all("div", class_="markdown"):
            text = div.get_text(separator="\n", strip=True)
            if text:
                markdown_cells.append(text)

                # Extract fenced code from the cell text
                fenced = re.findall(r"```(?:\w+)?\s*(.*?)```", text, re.MULTILINE | re.DOTALL)
                code_blocks.extend([c.strip() for c in fenced if c.strip()])

        return {"markdown_text": markdown_cells, "code_blocks": code_blocks}

    def get_all_cleaned_notebooks(self) -> List[Dict[str, Any]]:
        """
        Return cleaned metadata for all notebooks.
        Lazily loads and cleans if not already done (safe even if file missing).
        """
        if not self.cleaned_metadata:
            raw_metadata = self.load_metadata()
            # load_metadata() already validates and returns empty list if not a list
            self.cleaned_metadata = self.clean(raw_metadata)
        return self.cleaned_metadata

    # ---- Parsing & Deep Scrape ----

    def parse(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a deeply scraped notebook item into a standardized format.
        """
        # Validate input (Fixes #27, #28, #29)
        if not isinstance(item, dict):
            logger.error("parse expected a dict, got %s", type(item).__name__)
            return {
                "title": "",
                "url": "",
                "section": "code",
                "relevance_score": None,
                "metadata": {"notebook_hash": None, "last_scraped": None},
                "content": "",
            }

        md_blocks = item.get("markdown_blocks", [])
        if not isinstance(md_blocks, list):
            logger.warning("parse expected markdown_blocks to be a list; coercing to empty list.")
            md_blocks = []

        content = "\n\n".join([str(x) for x in md_blocks])

        return {
            "title": str(item.get("title", "")),
            "url": str(item.get("url", "")),
            "section": str(item.get("section", "code")),
            "relevance_score": item.get("relevance_score", None),
            "metadata": {
                "notebook_hash": item.get("notebook_hash"),
                "last_scraped": item.get("last_scraped"),
            },
            "content": content,
        }

    def deep_scrape_notebooks(
        self, query: str, mode: str = "summary", model: str = "codellama:13b"
    ) -> List[Dict[str, Any]]:
        """
        Perform AI-powered deep scraping on notebooks using ScrapeGraphAI.
        """
        # Validate inputs (Fix #30)
        if not isinstance(query, str) or not query.strip():
            logger.error("deep_scrape_notebooks: 'query' must be a non-empty string.")
            return []
        if not isinstance(mode, str) or not mode.strip():
            logger.error("deep_scrape_notebooks: 'mode' must be a non-empty string.")
            return []
        if not isinstance(model, str) or not model.strip():
            logger.error("deep_scrape_notebooks: 'model' must be a non-empty string.")
            return []

        notebooks = self.get_all_cleaned_notebooks()
        # Guard against missing keys (Fix #31)
        metadata = []
        for n in notebooks:
            if not isinstance(n, dict):
                continue
            url = n.get("url")
            title = n.get("title")
            if isinstance(url, str) and url.strip():
                metadata.append({"url": url, "title": str(title or "")})

        # Handler call is assumed to be available per your config choice.
        try:
            results = scrapegraphai_handler(
                query=query,
                mode=mode,
                metadata=metadata,
                model=model,
            )
        except Exception as e:
            logger.error("deep_scrape_notebooks: handler failed: %s", e)
            return []

        if not isinstance(results, list):
            logger.warning("deep_scrape_notebooks: handler returned non-list; coercing to empty list.")
            return []

        return results
