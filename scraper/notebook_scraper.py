import os
import json
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class NotebookScraper:
    def __init__(self, metadata_path: str):
        self.metadata_path = metadata_path
        self.metadata: List[Dict[str, Any]] = []
        self.cleaned_metadata: List[Dict[str, Any]] = []
        self.timestamp: str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.load_metadata()

    def load_metadata(self) -> None:
        """Load and clean notebook metadata from JSON file."""
        if not os.path.exists(self.metadata_path):
            logging.error(f"Notebook metadata file '{self.metadata_path}' not found.")
            return

        try:
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON: {e}")
            return
        except Exception as e:
            logging.error(f"Unexpected error loading metadata: {e}")
            return

        self.cleaned_metadata = self.clean_metadata(self.metadata)

    def clean_metadata(self, metadata: List[Dict]) -> List[Dict]:
        """Standardize and simplify notebook metadata."""
        cleaned = []
        for item in metadata:
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
                    'score': item.get('score', 0),
                    'date_created': self.format_date(item.get('dateCreated')),
                    'date_modified': self.format_date(item.get('dateModified')),
                }
                cleaned_item = self.tag_notebook(cleaned_item)
                cleaned.append(cleaned_item)
            except Exception as e:
                logging.warning(f"Skipping notebook due to error: {e}")
        return cleaned

    def format_date(self, date_str: Optional[str]) -> Optional[str]:
        """Convert ISO date string to standard readable format."""
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

    def tag_notebook(self, notebook: Dict[str, Any]) -> Dict[str, Any]:
        """Add a content hash for deduplication/versioning."""
        content = f"{notebook.get('title', '')}{notebook.get('author', '')}{notebook.get('date_created', '')}"
        notebook['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
        return notebook

    def get_all_cleaned_notebooks(self) -> List[Dict[str, Any]]:
        """Return all cleaned notebooks."""
        return self.cleaned_metadata

    def get_pinned_notebooks(self) -> List[Dict[str, Any]]:
        """Return all pinned notebooks."""
        return [nb for nb in self.cleaned_metadata if nb.get('is_pinned')]

    def get_unpinned_notebooks(self) -> List[Dict[str, Any]]:
        """Return all unpinned notebooks."""
        return [nb for nb in self.cleaned_metadata if not nb.get('is_pinned')]

    def filter_metadata(
        self,
        metadata: List[Dict[str, Any]],
        min_upvotes: int = 0,
        max_days_old: Optional[int] = None,
        custom_filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> List[Dict[str, Any]]:
        """Filter notebooks based on upvotes, age, or custom logic."""
        filtered = []
        now = datetime.utcnow()
        for item in metadata:
            votes = item.get('votes', 0)
            created_str = item.get('date_created', '')
            try:
                created = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            age_days = (now - created).days
            if votes < min_upvotes:
                continue
            if max_days_old is not None and age_days > max_days_old:
                continue
            if custom_filter_fn and not custom_filter_fn(item):
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
        try:
            return sorted(notebooks, key=lambda nb: nb.get(key, 0), reverse=reverse)
        except Exception as e:
            logging.warning(f"Failed to sort notebooks by '{key}': {e}")
            return notebooks