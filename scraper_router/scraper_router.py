"""
Scraper Router - First stage of the new architecture
Decides what data to get and orchestrates data collection from multiple sources.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .data_source_decider import DataSourceDecider
from ..core_utils.simple_cache import SimpleCache
from ..core_utils.data_combiner import DataCombiner

# Import existing scrapers (we'll keep these)
from ...Kaggle_Fetcher.kaggle_fetcher import KaggleFetcher
from ...scraper.overview_scraper import OverviewScraper
from ...scraper.notebook_scraper_v2 import NotebookScraperV2
from ...scraper.model_scraper_v2 import ModelScraperV2
from ...scraper.discussion_scraper_v2 import DiscussionScraperV2

logger = logging.getLogger(__name__)

class ScraperRouter:
    """
    First stage of the new architecture.
    Decides what data to get and orchestrates collection from multiple sources.
    """

    def __init__(self, llm, perplexity_api_key: Optional[str] = None):
        self.llm = llm
        self.perplexity_api_key = perplexity_api_key
        
        # Initialize components
        self.data_source_decider = DataSourceDecider(llm)
        self.cache = SimpleCache()
        self.data_combiner = DataCombiner()
        
        # Initialize data sources
        self.kaggle_api = KaggleFetcher()
        self.overview_scraper = OverviewScraper()
        self.notebook_scraper = NotebookScraperV2()
        self.model_scraper = ModelScraperV2()
        self.discussion_scraper = DiscussionScraperV2()

    def route_and_collect_data(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for the scraper router.
        
        Args:
            query: User query
            context: Additional context (section, competition, etc.)
            
        Returns:
            {
                "data": collected_data,
                "sources_used": ["KAGGLE_API", "SHALLOW_SCRAPING"],
                "reasoning": "explanation",
                "freshness": "fresh" | "cached" | "mixed"
            }
        """
        if context is None:
            context = {}
            
        logger.info(f"Scraper Router: Processing query '{query}' with context {context}")
        
        try:
            # Step 1: Decide what data sources to use
            decision = self._decide_data_sources(query, context)
            logger.info(f"Data source decision: {decision}")
            
            # Step 2: Collect data from chosen sources
            collected_data = self._collect_data_from_sources(query, decision, context)
            logger.info(f"Collected data from {len(collected_data)} sources")
            
            # Step 3: Combine and structure the data
            combined_data = self.data_combiner.combine_data(collected_data, query)
            
            # Step 4: Determine data freshness
            freshness = self._determine_freshness(collected_data)
            
            return {
                "data": combined_data,
                "sources_used": decision["sources"],
                "reasoning": decision["reasoning"],
                "freshness": freshness,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in scraper router: {e}")
            return self._fallback_data_collection(query, context)

    def _decide_data_sources(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide which data sources to use."""
        # Check cache first
        cached_data_info = self._get_cached_data_info(query, context)
        
        # Get data freshness info
        data_freshness = self._assess_data_freshness(query, context)
        
        # Make decision
        return self.data_source_decider.decide_data_sources(
            query=query,
            context=context,
            cached_data_info=cached_data_info,
            data_freshness=data_freshness
        )

    def _collect_data_from_sources(self, query: str, decision: Dict[str, Any], 
                                 context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect data from the chosen sources."""
        collected_data = []
        sources = decision["sources"]
        
        for source in sources:
            try:
                if source == "CACHED_DATA":
                    data = self._get_cached_data(query, context)
                    if data:
                        collected_data.append({
                            "source": "CACHED_DATA",
                            "data": data,
                            "timestamp": "cached"
                        })
                        
                elif source == "KAGGLE_API":
                    data = self._get_kaggle_api_data(query, context)
                    if data:
                        collected_data.append({
                            "source": "KAGGLE_API",
                            "data": data,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                elif source == "SHALLOW_SCRAPING":
                    data = self._get_shallow_scraping_data(query, context)
                    if data:
                        collected_data.append({
                            "source": "SHALLOW_SCRAPING",
                            "data": data,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                elif source == "PERPLEXITY_SEARCH":
                    data = self._get_perplexity_data(query, context)
                    if data:
                        collected_data.append({
                            "source": "PERPLEXITY_SEARCH",
                            "data": data,
                            "timestamp": datetime.now().isoformat()
                        })
                        
            except Exception as e:
                logger.error(f"Error collecting data from {source}: {e}")
                continue
                
        return collected_data

    def _get_cached_data(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached data if available and fresh enough."""
        cache_key = self._generate_cache_key(query, context)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            # Check if data is fresh enough
            age_hours = self._get_data_age_hours(cached_data.get("timestamp"))
            if self.data_source_decider.should_use_cached_data(query, age_hours):
                return cached_data
                
        return None

    def _get_kaggle_api_data(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get data from Kaggle API."""
        section = context.get("section", "overview")
        
        try:
            if section == "leaderboard":
                return self.kaggle_api.fetch_leaderboard_metadata()
            elif section == "data":
                return self.kaggle_api.fetch_dataset_metadata()
            else:
                # For other sections, try to get competition metadata
                return self.kaggle_api.fetch_competition_metadata()
        except Exception as e:
            logger.error(f"Error fetching Kaggle API data: {e}")
            return None

    def _get_shallow_scraping_data(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get data from shallow scraping."""
        section = context.get("section", "overview")
        
        try:
            if section == "overview":
                return self.overview_scraper.scrape()
            elif section == "code":
                return self.notebook_scraper.scrape()
            elif section == "model":
                return self.model_scraper.scrape_models()
            elif section == "discussion":
                return self.discussion_scraper.scrape()
            else:
                logger.warning(f"Unknown section for shallow scraping: {section}")
                return None
        except Exception as e:
            logger.error(f"Error in shallow scraping: {e}")
            return None

    def _get_perplexity_data(self, query: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get real-time data from Perplexity API."""
        if not self.perplexity_api_key:
            logger.warning("Perplexity API key not provided")
            return None
            
        try:
            # This would be implemented with actual Perplexity API calls
            # For now, return a placeholder
            return {
                "type": "perplexity_search",
                "query": query,
                "results": "Real-time search results would go here"
            }
        except Exception as e:
            logger.error(f"Error fetching Perplexity data: {e}")
            return None

    def _get_cached_data_info(self, query: str, context: Dict[str, Any]) -> str:
        """Get information about available cached data."""
        cache_key = self._generate_cache_key(query, context)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            age_hours = self._get_data_age_hours(cached_data.get("timestamp"))
            return f"Cached data available, age: {age_hours:.1f} hours"
        else:
            return "No cached data available"

    def _assess_data_freshness(self, query: str, context: Dict[str, Any]) -> str:
        """Assess how fresh the data needs to be for this query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["latest", "recent", "now", "current"]):
            return "very_fresh"
        elif any(word in query_lower for word in ["today", "this week"]):
            return "fresh"
        else:
            return "any"

    def _determine_freshness(self, collected_data: List[Dict[str, Any]]) -> str:
        """Determine the overall freshness of collected data."""
        if not collected_data:
            return "none"
            
        timestamps = [item.get("timestamp") for item in collected_data if item.get("timestamp")]
        
        if all(ts == "cached" for ts in timestamps):
            return "cached"
        elif any(ts != "cached" for ts in timestamps):
            return "mixed"
        else:
            return "fresh"

    def _generate_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate a cache key for the query and context."""
        section = context.get("section", "general")
        return f"{section}:{hash(query)}"

    def _get_data_age_hours(self, timestamp: str) -> float:
        """Calculate data age in hours."""
        if not timestamp or timestamp == "cached":
            return 24  # Assume old if no timestamp
            
        try:
            if isinstance(timestamp, str):
                data_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                data_time = timestamp
                
            now = datetime.now(data_time.tzinfo) if data_time.tzinfo else datetime.now()
            age = now - data_time
            return age.total_seconds() / 3600
        except Exception:
            return 24  # Assume old if parsing fails

    def _fallback_data_collection(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback data collection when main process fails."""
        logger.warning("Using fallback data collection")
        
        try:
            # Try to get basic data from Kaggle API
            data = self._get_kaggle_api_data(query, context)
            return {
                "data": data or {},
                "sources_used": ["KAGGLE_API"],
                "reasoning": "Fallback to Kaggle API due to error",
                "freshness": "fresh",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Fallback data collection failed: {e}")
            return {
                "data": {},
                "sources_used": [],
                "reasoning": "No data available due to errors",
                "freshness": "none",
                "timestamp": datetime.now().isoformat()
            }

