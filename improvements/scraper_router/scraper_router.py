"""
Scraper Router - Main orchestrator for data collection
Refactored from HybridScrapingAgent without deep scraping dependencies.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .data_source_decider import DataSourceDecider
from ..core_utils.simple_cache import SimpleCache
from ..core_utils.data_combiner import DataCombiner

logger = logging.getLogger(__name__)

class ScraperRouter:
    """
    Main orchestrator for data collection in the new architecture.
    Refactored from HybridScrapingAgent without deep scraping dependencies.
    """

    def __init__(self, llm, perplexity_api_key: Optional[str] = None):
        self.llm = llm
        self.perplexity_api_key = perplexity_api_key
        
        # Initialize components
        self.data_source_decider = DataSourceDecider(llm)
        self.cache = SimpleCache()
        self.data_combiner = DataCombiner()
        
        # Initialize scrapers (these will be integrated later)
        self.scrapers = self._initialize_scrapers()

    def _initialize_scrapers(self) -> Dict[str, Any]:
        """Initialize available scrapers."""
        # TODO: Integrate with existing scrapers
        return {
            "kaggle_api": None,  # Will integrate with KaggleFetcher
            "overview_scraper": None,  # Will integrate with existing scrapers
            "notebook_scraper": None,
            "model_scraper": None,
            "discussion_scraper": None,
            "perplexity_search": None  # Will integrate with Perplexity API
        }

    def route_and_collect_data(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for data collection.
        
        Args:
            query: User query
            context: Additional context (section, competition, etc.)
            
        Returns:
            {
                "data": combined_data,
                "sources_used": ["KAGGLE_API", "SHALLOW_SCRAPING"],
                "reasoning": "explanation",
                "freshness": "fresh" | "cached" | "mixed"
            }
        """
        if context is None:
            context = {}
            
        logger.info(f"Scraper Router: Processing query '{query}'")
        
        try:
            # Step 1: Decide data sources
            source_decision = self._decide_data_sources(query, context)
            logger.info(f"Data sources decided: {source_decision['sources']}")
            
            # Step 2: Collect data from chosen sources
            collected_data = self._collect_data_from_sources(
                query, context, source_decision["sources"]
            )
            
            # Step 3: Combine and structure data
            combined_data = self.data_combiner.combine_data(collected_data, query)
            
            # Step 4: Determine freshness
            freshness = self._determine_freshness(collected_data)
            
            return {
                "data": combined_data,
                "sources_used": source_decision["sources"],
                "reasoning": source_decision["reasoning"],
                "freshness": freshness,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in scraper router: {e}")
            return {
                "data": {"error": str(e)},
                "sources_used": [],
                "reasoning": f"Error: {str(e)}",
                "freshness": "error",
                "timestamp": datetime.now().isoformat()
            }

    def _decide_data_sources(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide which data sources to use."""
        # Check for cached data
        cache_key = f"query:{hash(query)}"
        cached_data = self.cache.get(cache_key)
        cached_data_info = "Cached data available" if cached_data else "No cached data"
        
        # Determine data freshness requirement
        data_freshness = self._assess_freshness_requirement(query, context)
        
        return self.data_source_decider.decide_data_sources(
            query=query,
            context=context,
            cached_data_info=cached_data_info,
            data_freshness=data_freshness
        )

    def _collect_data_from_sources(self, query: str, context: Dict[str, Any], 
                                  sources: List[str]) -> Dict[str, Any]:
        """Collect data from the chosen sources."""
        collected_data = {
            "data": {},
            "sources": sources
        }
        
        for source in sources:
            try:
                if source == "KAGGLE_API":
                    data = self._collect_from_kaggle_api(query, context)
                elif source == "SHALLOW_SCRAPING":
                    data = self._collect_from_shallow_scraping(query, context)
                elif source == "PERPLEXITY_SEARCH":
                    data = self._collect_from_perplexity_search(query, context)
                elif source == "CACHED_DATA":
                    data = self._collect_from_cache(query, context)
                else:
                    logger.warning(f"Unknown data source: {source}")
                    continue
                    
                if data:
                    collected_data["data"][source.lower()] = data
                    
            except Exception as e:
                logger.error(f"Error collecting from {source}: {e}")
                continue
                
        return collected_data

    def _collect_from_kaggle_api(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from Kaggle API."""
        # TODO: Integrate with existing KaggleFetcher
        logger.info("Collecting from Kaggle API (not implemented yet)")
        return {
            "type": "kaggle_api",
            "items": [
                {"title": "Competition Overview", "content": "Mock Kaggle API data"},
                {"title": "Leaderboard", "content": "Mock leaderboard data"}
            ],
            "count": 2
        }

    def _collect_from_shallow_scraping(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from shallow scraping."""
        # TODO: Integrate with existing scrapers
        logger.info("Collecting from shallow scraping (not implemented yet)")
        return {
            "type": "scraped",
            "items": [
                {"title": "Discussion Post", "content": "Mock scraped data"},
                {"title": "Notebook", "content": "Mock notebook data"}
            ],
            "count": 2
        }

    def _collect_from_perplexity_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from Perplexity search."""
        # TODO: Integrate with Perplexity API
        logger.info("Collecting from Perplexity search (not implemented yet)")
        return {
            "type": "search",
            "items": [
                {"title": "Search Result", "content": "Mock Perplexity search data"}
            ],
            "count": 1
        }

    def _collect_from_cache(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from cache."""
        cache_key = f"query:{hash(query)}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return {
                "type": "cached",
                "items": cached_data.get("data", []),
                "count": len(cached_data.get("data", []))
            }
        else:
            return None

    def _assess_freshness_requirement(self, query: str, context: Dict[str, Any]) -> str:
        """Assess how fresh the data needs to be."""
        query_lower = query.lower()
        
        # High freshness indicators
        if any(word in query_lower for word in ["latest", "recent", "current", "now", "today"]):
            return "high"
            
        # Low freshness indicators
        if any(word in query_lower for word in ["historical", "past", "old", "archive"]):
            return "low"
            
        # Default to medium freshness
        return "medium"

    def _determine_freshness(self, collected_data: Dict[str, Any]) -> str:
        """Determine the overall freshness of collected data."""
        data = collected_data.get("data", {})
        
        has_fresh = any(source in ["kaggle_api", "scraped", "search"] for source in data.keys())
        has_cached = "cached" in data.keys()
        
        if has_fresh and has_cached:
            return "mixed"
        elif has_fresh:
            return "fresh"
        elif has_cached:
            return "cached"
        else:
            return "unknown"


