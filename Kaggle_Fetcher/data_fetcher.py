"""
Data Fetcher - Hybrid API + Scraping approach for competition data
-------------------------------------------------------------------
Combines:
1. Kaggle API for file listings (fast, reliable)
2. Playwright scraping for data descriptions (on-demand)
3. ChromaDB caching for performance

Similar pattern to NotebookApiFetcher.
"""

from typing import Dict, List, Any, Optional
from Kaggle_Fetcher.kaggle_api_client import get_competition_data_files


class DataFetcher:
    """Fetches competition data information using hybrid API + scraping."""
    
    def __init__(self):
        """Initialize data fetcher."""
        self.cache = {}  # Simple in-memory cache
    
    def fetch_data_files(self, competition_slug: str) -> List[Dict[str, Any]]:
        """
        Fetch list of data files using Kaggle API.
        
        Args:
            competition_slug: Competition identifier
        
        Returns:
            List of file metadata dicts
        """
        print(f"[DataFetcher] Fetching file list for {competition_slug}")
        
        # Use Kaggle API (fast, reliable)
        files = get_competition_data_files(competition_slug)
        
        if not files:
            print(f"[DataFetcher] No files found for {competition_slug}")
            return []
        
        print(f"[DataFetcher] Found {len(files)} files")
        return files
    
    def fetch_data_description(
        self, 
        competition_slug: str, 
        use_scraper: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch data description (requires scraping).
        
        Args:
            competition_slug: Competition identifier
            use_scraper: Whether to use scraper if description not in cache
        
        Returns:
            Dict with description, sections, column_info
        """
        # Check in-memory cache first
        cache_key = f"data_desc_{competition_slug}"
        if cache_key in self.cache:
            print(f"[DataFetcher] Using cached description for {competition_slug}")
            return self.cache[cache_key]
        
        # If scraping enabled, use scraper
        if use_scraper:
            print(f"[DataFetcher] Scraping data description for {competition_slug}")
            try:
                from scraper.data_scraper import DataSectionScraper
                scraper = DataSectionScraper(competition_slug)
                result = scraper.scrape_data_description()
                
                # Cache the result
                self.cache[cache_key] = result
                
                return result
            except Exception as e:
                print(f"[DataFetcher] Error scraping description: {e}")
                return self._empty_description(competition_slug)
        
        return self._empty_description(competition_slug)
    
    def fetch_complete_data_info(
        self, 
        competition_slug: str,
        include_description: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch complete data information (files + description).
        
        Args:
            competition_slug: Competition identifier
            include_description: Whether to include scraped description
        
        Returns:
            Dict with files and description
        """
        print(f"[DataFetcher] Fetching complete data info for {competition_slug}")
        
        # Get file list from API (always fast)
        files = self.fetch_data_files(competition_slug)
        
        # Get description from scraper (if requested)
        description_data = {}
        if include_description:
            description_data = self.fetch_data_description(competition_slug)
        
        return {
            "competition": competition_slug,
            "files": files,
            "file_count": len(files),
            "total_size": sum(f.get('size', 0) for f in files),
            "description": description_data.get('description', ''),
            "sections": description_data.get('sections', {}),
            "column_info": description_data.get('column_info', []),
            "file_descriptions": description_data.get('file_descriptions', []),
            "has_description": bool(description_data.get('description'))
        }
    
    def _empty_description(self, competition_slug: str) -> Dict[str, Any]:
        """Return empty description structure."""
        return {
            "competition": competition_slug,
            "description": "",
            "sections": {},
            "column_info": [],
            "file_descriptions": [],
            "scraped": False
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    import json
    
    competition = sys.argv[1] if len(sys.argv) > 1 else "titanic"
    
    print("=" * 70)
    print(f"DATA FETCHER TEST: {competition}")
    print("=" * 70)
    
    fetcher = DataFetcher()
    
    # Test 1: Fetch files only (API - fast)
    print("\n[TEST 1] Fetching file list (API only)...")
    files = fetcher.fetch_data_files(competition)
    print(f"✅ Found {len(files)} files")
    for f in files:
        size_kb = f['size'] / 1024
        print(f"  - {f['name']}: {size_kb:.1f} KB")
    
    # Test 2: Fetch description (scraping - slower)
    print("\n[TEST 2] Fetching data description (with scraping)...")
    description = fetcher.fetch_data_description(competition)
    print(f"✅ Description length: {len(description.get('description', ''))} chars")
    print(f"✅ Sections: {list(description.get('sections', {}).keys())}")
    print(f"✅ Column info: {len(description.get('column_info', []))} columns")
    
    # Test 3: Fetch complete info
    print("\n[TEST 3] Fetching complete data info...")
    complete = fetcher.fetch_complete_data_info(competition)
    print(f"✅ Files: {complete['file_count']}")
    print(f"✅ Total size: {complete['total_size'] / 1024:.1f} KB")
    print(f"✅ Has description: {complete['has_description']}")
    
    print("\n" + "=" * 70)
    print("SAMPLE OUTPUT (JSON)")
    print("=" * 70)
    
    # Print sample (without full description to keep it readable)
    sample = {
        "competition": complete["competition"],
        "files": complete["files"],
        "description_preview": complete["description"][:200] + "...",
        "sections": list(complete["sections"].keys()),
        "column_count": len(complete["column_info"])
    }
    print(json.dumps(sample, indent=2))
    
    print("\n" + "=" * 70)




