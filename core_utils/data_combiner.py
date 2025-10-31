"""
Data Combiner - Combines data from multiple sources
Refactored from ResultStructurer without deep scraping dependencies.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class DataCombiner:
    """
    Combines and structures data from multiple sources.
    Removes deep scraping dependencies and focuses on clean data integration.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def combine_data(self, collected_data: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Combine data from multiple sources into a unified structure.
        
        Args:
            collected_data: List of data from different sources
            query: Original user query for context
            
        Returns:
            Combined and structured data
        """
        if not collected_data:
            return {"error": "No data collected", "sources": []}
            
        try:
            # Separate data by source
            source_data = {}
            for item in collected_data:
                source = item.get("source", "unknown")
                if source not in source_data:
                    source_data[source] = []
                source_data[source].append(item.get("data", {}))
            
            # Combine data from each source
            combined = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "sources": list(source_data.keys()),
                "data": {}
            }
            
            # Process each source
            for source, data_list in source_data.items():
                if source == "KAGGLE_API":
                    combined["data"]["kaggle"] = self._process_kaggle_data(data_list)
                elif source == "SHALLOW_SCRAPING":
                    combined["data"]["scraped"] = self._process_scraped_data(data_list)
                elif source == "PERPLEXITY_SEARCH":
                    combined["data"]["search"] = self._process_search_data(data_list)
                elif source == "CACHED_DATA":
                    combined["data"]["cached"] = self._process_cached_data(data_list)
                else:
                    combined["data"][source.lower()] = data_list
            
            # Add metadata
            combined["metadata"] = self._generate_metadata(combined["data"])
            
            return combined
            
        except Exception as e:
            logger.error(f"Error combining data: {e}")
            return {"error": f"Data combination failed: {str(e)}", "sources": []}

    def _process_kaggle_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process Kaggle API data."""
        if not data_list:
            return {}
            
        # Combine all Kaggle data
        combined = {
            "type": "kaggle_api",
            "items": data_list,
            "count": len(data_list)
        }
        
        return combined

    def _process_scraped_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process scraped data."""
        if not data_list:
            return {}
            
        # Structure scraped data
        structured_items = []
        for data in data_list:
            if isinstance(data, list):
                # Handle list of items
                for item in data:
                    structured_items.append(self._structure_item(item, "scraped"))
            else:
                # Handle single item
                structured_items.append(self._structure_item(data, "scraped"))
        
        return {
            "type": "scraped",
            "items": structured_items,
            "count": len(structured_items)
        }

    def _process_search_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process search data (Perplexity, etc.)."""
        if not data_list:
            return {}
            
        return {
            "type": "search",
            "items": data_list,
            "count": len(data_list)
        }

    def _process_cached_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process cached data."""
        if not data_list:
            return {}
            
        return {
            "type": "cached",
            "items": data_list,
            "count": len(data_list)
        }

    def _structure_item(self, item: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Structure a single data item."""
        # Generate content hash for deduplication
        content = item.get("content", "") or item.get("title", "") or str(item)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        
        structured = {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": content,
            "source": source,
            "content_hash": content_hash,
            "metadata": item.get("metadata", {}),
            "timestamp": item.get("timestamp", datetime.now().isoformat())
        }
        
        # Add any additional fields from the original item
        for key, value in item.items():
            if key not in structured and value is not None:
                structured[key] = value
                
        return structured

    def _generate_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata about the combined data."""
        metadata = {
            "total_sources": len(data),
            "source_types": list(data.keys()),
            "total_items": 0,
            "freshness": "unknown"
        }
        
        # Count total items
        for source, source_data in data.items():
            if isinstance(source_data, dict) and "count" in source_data:
                metadata["total_items"] += source_data["count"]
            elif isinstance(source_data, list):
                metadata["total_items"] += len(source_data)
        
        # Determine freshness
        has_fresh = any(source in ["kaggle", "scraped", "search"] for source in data.keys())
        has_cached = "cached" in data.keys()
        
        if has_fresh and has_cached:
            metadata["freshness"] = "mixed"
        elif has_fresh:
            metadata["freshness"] = "fresh"
        elif has_cached:
            metadata["freshness"] = "cached"
        else:
            metadata["freshness"] = "unknown"
            
        return metadata

    def deduplicate_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate items based on content hash."""
        seen_hashes = set()
        unique_items = []
        
        for item in items:
            content_hash = item.get("content_hash", "")
            if content_hash and content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_items.append(item)
            elif not content_hash:
                # If no hash, add anyway (shouldn't happen with structured items)
                unique_items.append(item)
                
        return unique_items

    def prioritize_items(self, items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Prioritize items based on relevance to query."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        def relevance_score(item):
            score = 0
            title = item.get("title", "").lower()
            content = item.get("content", "").lower()
            
            # Title matches are worth more
            for word in query_words:
                if word in title:
                    score += 3
                if word in content:
                    score += 1
                    
            # Boost score for certain metadata
            if item.get("pinned", False):
                score += 2
            if item.get("relevance_score"):
                score += item["relevance_score"]
                
            return score
            
        # Sort by relevance score (descending)
        return sorted(items, key=relevance_score, reverse=True)

