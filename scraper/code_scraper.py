import os
import json
import re
import hashlib
import logging
import pprint
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class CodeParser:
    def __init__(self, metadata_path: str):
        self.metadata_path = metadata_path
        self.metadata: List[Dict[str, Any]] = []
        self.cleaned_metadata: List[Dict[str, Any]] = []
        self.timestamp: str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.load_metadata()


    
    def load_metadata(self) -> None:
        """Load and clean metadata from a JSON file."""
        if not os.path.exists(self.metadata_path):
            logging.error(f"Metadata file '{self.metadata_path}' not found.")
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

    def clean_metadata(self, metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Standardize and simplify metadata."""
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
                    'date_created': self.format_date(item.get('dateCreated')),
                    'date_modified': self.format_date(item.get('dateModified')),
                }
                cleaned_item = self.tag_notebook(cleaned_item)
                cleaned.append(cleaned_item)
            except Exception as e:
                logging.warning(f"Skipping invalid item due to error: {e}")
        return cleaned

    def format_date(self, date_str: Optional[str]) -> Optional[str]:
        """Convert ISO date string to standard readable format."""
        if not date_str:
            return None
        # Try both ISO formats
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
        content = f"{notebook.get('title','')}{notebook.get('author','')}{notebook.get('date_created','')}"
        notebook['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
        notebook['is_pinned'] = notebook.get('is_pinned', False)
        return notebook

    def filter_metadata(
        self,
        metadata: List[Dict[str, Any]],
        min_upvotes: int = 0,
        max_days_old: Optional[int] = None,
        custom_filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generic filter for code notebooks based on upvotes, recency, or a custom function.
        """
        filtered = []
        now = datetime.utcnow()
        for item in metadata:
            votes = item.get('votes', 0)
            date_str = item.get('date_created', '')
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                days_old = (now - dt).days
            except Exception:
                days_old = None

            if votes < min_upvotes:
                continue
            if max_days_old is not None and (days_old is None or days_old > max_days_old):
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
            return sorted(notebooks, key=lambda x: x.get(key, 0) or 0, reverse=reverse)
        except Exception as e:
            logging.error(f"Sorting failed: {e}")
            return notebooks

    def extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks from markdown-style fenced code."""
        pattern = re.compile(r'```(?:\w+)?\s*([\s\S]*?)```', re.MULTILINE)
        return [match.strip() for match in pattern.findall(content)]

    def extract_markdown_blocks(self, content: str) -> List[str]:
        """Extract fenced markdown blocks."""
        pattern = re.compile(r'```markdown\s*([\s\S]*?)```', re.MULTILINE)
        return [match.strip() for match in pattern.findall(content)]

    def extract_code_and_markdown(self, content: str) -> Dict[str, List[str]]:
        """Extract both code and markdown blocks from a single notebook's content."""
        return {
            'code_blocks': self.extract_code_blocks(content),
            'markdown_blocks': self.extract_markdown_blocks(content)
        }

    def compute_hash(self, content: str) -> str:
        """Compute a hash of the notebook content for deduplication/versioning."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def extract_code_and_markdown_from_metadata(self) -> List[Dict[str, Any]]:
        """Apply extraction to all cleaned metadata entries."""
        extracted_data = []
        for item in self.cleaned_metadata:
            content = item.get('description', '')
            extracted = self.extract_code_and_markdown(content)
            combined_text = "\n".join(extracted['code_blocks'] + extracted['markdown_blocks'])
            extracted_data.append({
                'id': item.get('id'),
                'title': item.get('title'),
                'code_blocks': extracted['code_blocks'],
                'markdown_blocks': extracted['markdown_blocks'],
                'notebook_hash': self.compute_hash(combined_text),
                'section': 'code.pinned' if item.get('is_pinned') else 'code.unpinned',
                'last_updated': self.timestamp,
                'notebook_score': None  # Agent will compute this later
            })
        return extracted_data

    def save_metadata(self, metadata: List[Dict[str, Any]], filename: str) -> None:
        """Save metadata or extracted data to a file."""
        try:
            with open(filename, 'w') as f:
                json.dump(metadata, f, indent=4)
        except IOError as e:
            logging.error(f"Failed to save file '{filename}': {e}")
        else:
            logging.info(f"Saved data to '{filename}'")

    def pretty_print(self, data: Any) -> None:
        """Pretty print any data structure."""
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)

if __name__ == "__main__":
    parser = CodeParser("notebook_metadata.json")
    extracted = parser.extract_code_and_markdown_from_metadata()
    parser.save_metadata(extracted, "extracted_code_and_markdown.json")

    # Print summary of first few entries
    logging.info("Preview of extracted code and markdown blocks:")
    for entry in extracted[:5]:
        logging.info(f"{entry['title']}: {len(entry['code_blocks'])} code blocks, {len(entry['markdown_blocks'])} markdown blocks")