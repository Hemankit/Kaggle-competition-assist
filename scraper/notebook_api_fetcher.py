"""
Kaggle Notebook API Fetcher
----------------------------
Fetches notebooks via Kaggle API (for dynamic content).
Follows the same pattern as overview_scraper.py but uses API instead of Playwright.
"""
import logging
from typing import Dict, Any, List, Optional
import json
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class NotebookAPIFetcher:
    """
    Kaggle Notebook Fetcher (API version)
    -------------------------------------
    Fetches competition notebooks using Kaggle API.
    Returns structured data similar to overview_scraper.py
    """

    def __init__(self, competition_slug: str):
        """
        Initialize the notebook fetcher.
        
        Args:
            competition_slug: Competition identifier (e.g., "titanic")
        """
        if not competition_slug or not isinstance(competition_slug, str):
            raise ValueError("competition_slug must be a non-empty string.")
        
        self.competition_slug = competition_slug
        
        # Import Kaggle API (lazy import to avoid import errors if not configured)
        try:
            from kaggle import api
            api.authenticate()
            self.api = api
        except Exception as e:
            logger.error(f"Failed to initialize Kaggle API: {e}")
            raise RuntimeError("Kaggle API not available. Please configure kaggle.json credentials.")

    def fetch_notebook_metadata(
        self, 
        max_notebooks: int = 50,
        sort_by: str = "voteCount"
    ) -> List[Dict[str, Any]]:
        """
        Fetch notebook metadata for the competition.
        
        Args:
            max_notebooks: Maximum number of notebooks to fetch
            sort_by: Sort order ("voteCount", "dateCreated", "dateRun")
        
        Returns:
            List of notebook metadata dictionaries
        """
        try:
            logger.info(f"Fetching notebooks for {self.competition_slug} (sort_by={sort_by})...")
            
            # Fetch notebooks using Kaggle API
            notebooks = self.api.kernels_list(
                competition=self.competition_slug,
                page_size=min(max_notebooks, 100),  # API max is 100
                sort_by=sort_by
            )
            
            # Convert to list of dicts with standardized fields
            notebook_list = []
            for notebook in notebooks[:max_notebooks]:
                notebook_dict = {
                    "ref": notebook.ref,  # e.g., "username/notebook-name"
                    "title": notebook.title,
                    "author": notebook.author,
                    "total_votes": notebook.total_votes,
                    "is_pinned": False,  # API doesn't provide this field directly
                    "last_run_time": str(notebook.last_run_time) if hasattr(notebook, 'last_run_time') else None,
                    "language": getattr(notebook, 'language', 'python'),
                    "url": f"https://www.kaggle.com/code/{notebook.ref}",
                    "total_comments": 0  # API doesn't provide this field directly
                }
                notebook_list.append(notebook_dict)
            
            logger.info(f"Fetched {len(notebook_list)} notebooks")
            return notebook_list
            
        except Exception as e:
            logger.error(f"Error fetching notebook metadata: {e}")
            return []

    def download_notebook_content(self, notebook_ref: str) -> Optional[Dict[str, Any]]:
        """
        Download and parse a single notebook's content.
        
        Args:
            notebook_ref: Notebook reference (e.g., "username/notebook-name")
        
        Returns:
            Dictionary with parsed content: {"code_cells": [...], "markdown_cells": [...]}
        """
        try:
            logger.info(f"Downloading notebook: {notebook_ref}")
            
            # Create temp directory for download
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download notebook to temp directory
                self.api.kernels_pull(notebook_ref, path=temp_dir, metadata=False)
                
                # Find the .ipynb file
                ipynb_files = list(Path(temp_dir).glob("*.ipynb"))
                if not ipynb_files:
                    logger.warning(f"No .ipynb file found for {notebook_ref}")
                    return None
                
                # Read and parse the notebook
                with open(ipynb_files[0], 'r', encoding='utf-8') as f:
                    notebook_data = json.load(f)
                
                # Extract cells
                cells = notebook_data.get('cells', [])
                
                code_cells = []
                markdown_cells = []
                
                for cell in cells:
                    cell_type = cell.get('cell_type', '')
                    source = cell.get('source', [])
                    
                    # Join source lines into single string
                    if isinstance(source, list):
                        content = ''.join(source)
                    else:
                        content = str(source)
                    
                    if cell_type == 'code':
                        code_cells.append({
                            "content": content,
                            "language": "python"  # Could detect from metadata
                        })
                    elif cell_type == 'markdown':
                        markdown_cells.append({
                            "content": content
                        })
                
                logger.info(f"Extracted {len(code_cells)} code cells, {len(markdown_cells)} markdown cells")
                
                return {
                    "code_cells": code_cells,
                    "markdown_cells": markdown_cells
                }
                
        except Exception as e:
            logger.error(f"Error downloading notebook {notebook_ref}: {e}")
            return None

    def fetch(
        self,
        max_pinned: int = 5,
        max_top_voted: int = 10,
        min_votes: int = 50,
        download_content: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch and categorize notebooks (similar to overview_scraper.scrape()).
        
        Args:
            max_pinned: Maximum pinned notebooks to fetch
            max_top_voted: Maximum top-voted notebooks to fetch
            min_votes: Minimum votes for top-voted category
            download_content: Whether to download notebook content (can be slow)
        
        Returns:
            Dictionary with categorized notebooks (similar to overview_scraper structure):
            {
                "competition_slug": str,
                "notebook_categories": {
                    "pinned": [...],
                    "top_voted": [...],
                    "recent": [...]
                }
            }
        """
        logger.info(f"Fetching notebooks for competition: {self.competition_slug}")
        
        # Fetch metadata sorted by votes
        all_notebooks = self.fetch_notebook_metadata(max_notebooks=100, sort_by="voteCount")
        
        # Categorize notebooks
        # Note: API doesn't provide is_pinned field directly, so we use top-voted as proxy for "featured"
        # In practice, pinned notebooks are usually high-voted
        pinned_notebooks = all_notebooks[:max_pinned]  # Top N by votes = proxy for pinned
        top_voted_notebooks = [n for n in all_notebooks if n['total_votes'] >= min_votes][:max_top_voted]
        
        # Fetch recent notebooks (sorted by date)
        recent_notebooks = self.fetch_notebook_metadata(max_notebooks=20, sort_by="dateRun")[:5]
        
        result = {
            "competition_slug": self.competition_slug,
            "notebook_categories": {
                "pinned": [],
                "top_voted": [],
                "recent": []
            }
        }
        
        # Download content for pinned notebooks (highest priority)
        if download_content:
            logger.info(f"Downloading content for {len(pinned_notebooks)} pinned notebooks...")
            for notebook in pinned_notebooks:
                content = self.download_notebook_content(notebook['ref'])
                if content:
                    result["notebook_categories"]["pinned"].append({
                        "metadata": notebook,
                        "content": content
                    })
                else:
                    # Include metadata even if download fails
                    result["notebook_categories"]["pinned"].append({
                        "metadata": notebook,
                        "content": None
                    })
        else:
            # Metadata only
            result["notebook_categories"]["pinned"] = [{"metadata": n, "content": None} for n in pinned_notebooks]
            result["notebook_categories"]["top_voted"] = [{"metadata": n, "content": None} for n in top_voted_notebooks]
            result["notebook_categories"]["recent"] = [{"metadata": n, "content": None} for n in recent_notebooks]
        
        logger.info(f"Fetch complete: {len(result['notebook_categories']['pinned'])} pinned, "
                   f"{len(result['notebook_categories']['top_voted'])} top-voted, "
                   f"{len(result['notebook_categories']['recent'])} recent")
        
        return result


# --- Example usage ---
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME', '')
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY', '')
    
    fetcher = NotebookAPIFetcher("titanic")
    data = fetcher.fetch(max_pinned=2, max_top_voted=5, min_votes=10, download_content=True)
    
    print(f"\n[OK] Competition: {data['competition_slug']}")
    print("=" * 80)
    
    for category, notebooks in data['notebook_categories'].items():
        print(f"\n--- {category.upper()} ({len(notebooks)} notebooks) ---")
        for notebook in notebooks:
            metadata = notebook['metadata']
            content = notebook['content']
            print(f"  * {metadata['title']}")
            print(f"     Author: {metadata['author']}")
            print(f"     Votes: {metadata['total_votes']}")
            print(f"     Pinned: {metadata['is_pinned']}")
            if content:
                print(f"     Code cells: {len(content['code_cells'])}")
                print(f"     Markdown cells: {len(content['markdown_cells'])}")

