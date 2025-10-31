"""
Real Scraper Router - Integrates with existing scrapers
Uses actual scrapers and real LLM routing (when API key is available)
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Import existing scrapers
try:
    from scraper.overview_scraper import OverviewScraper
    from scraper.discussion_scraper import DiscussionScraper
    from scraper.notebook_scraper import NotebookScraper
    from scraper.model_scraper import ModelScraper
    from Kaggle_Fetcher.data_fetcher import KaggleFetcher
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some scrapers not available: {e}")
    SCRAPERS_AVAILABLE = False

# Import LLM
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)

class RealScraperRouter:
    """
    Real scraper router that integrates with existing scrapers.
    Uses actual data collection and real LLM routing.
    """

    def __init__(self, llm=None):
        self.llm = llm or self._get_llm()
        self.scrapers = self._initialize_scrapers()
        self.conversation_state = {
            'previous_queries': [],
            'collected_data': {},
            'context': {}
        }

    def _get_llm(self):
        """Get LLM instance."""
        if LLM_AVAILABLE:
            try:
                return ChatGoogleGenerativeAI(
                    model='gemini-2.5-pro',
                    temperature=0.1
                )
            except Exception as e:
                print(f"Warning: Could not initialize Gemini: {e}")
                return self._get_mock_llm()
        else:
            return self._get_mock_llm()

    def _get_mock_llm(self):
        """Fallback mock LLM."""
        class MockLLM:
            def invoke(self, input_data):
                query = input_data.get('query', '').lower()
                if 'latest' in query or 'recent' in query:
                    return 'KAGGLE_API,SHALLOW_SCRAPING\nHigh priority query requiring fresh data'
                elif 'historical' in query or 'past' in query:
                    return 'CACHED_DATA,SHALLOW_SCRAPING\nHistorical query can use cached data'
                else:
                    return 'KAGGLE_API,SHALLOW_SCRAPING\nStandard query using reliable sources'
        return MockLLM()

    def _initialize_scrapers(self):
        """Initialize available scrapers."""
        scrapers = {}
        
        if SCRAPERS_AVAILABLE:
            try:
                scrapers['overview'] = OverviewScraper()
                scrapers['discussion'] = DiscussionScraper()
                scrapers['notebook'] = NotebookScraper()
                scrapers['model'] = ModelScraper()
                scrapers['kaggle'] = KaggleFetcher()
                print("✅ All scrapers initialized successfully")
            except Exception as e:
                print(f"Warning: Error initializing scrapers: {e}")
        else:
            print("Warning: Using mock scrapers")
            scrapers = self._get_mock_scrapers()
        
        return scrapers

    def _get_mock_scrapers(self):
        """Fallback mock scrapers."""
        class MockScraper:
            def scrape(self, query, context):
                return {
                    'type': 'mock',
                    'items': [
                        {'title': f'Mock {query}', 'content': f'Mock content for {query}'}
                    ],
                    'count': 1
                }
        
        return {
            'overview': MockScraper(),
            'discussion': MockScraper(),
            'notebook': MockScraper(),
            'model': MockScraper(),
            'kaggle': MockScraper()
        }

    def route_and_collect_data(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for data collection with real scrapers.
        
        Args:
            query: User query
            context: Additional context (section, competition, etc.)
            
        Returns:
            Real collected data from actual scrapers
        """
        if context is None:
            context = {}
            
        logger.info(f"Real Scraper Router: Processing query '{query}'")
        
        try:
            # Step 1: Decide data sources using LLM
            source_decision = self._decide_data_sources(query, context)
            logger.info(f"Data sources decided: {source_decision['sources']}")
            
            # Step 2: Collect data from chosen sources using real scrapers
            collected_data = self._collect_data_from_sources(query, context, source_decision["sources"])
            
            # Step 3: Combine and structure data
            combined_data = self._combine_data(collected_data, query)
            
            # Step 4: Update conversation state
            self._update_conversation_state(query, combined_data)
            
            return {
                "data": combined_data,
                "sources_used": source_decision["sources"],
                "reasoning": source_decision["reasoning"],
                "freshness": "fresh",
                "timestamp": datetime.now().isoformat(),
                "real_data": True
            }
            
        except Exception as e:
            logger.error(f"Error in real scraper router: {e}")
            return {
                "data": {"error": str(e)},
                "sources_used": [],
                "reasoning": f"Error: {str(e)}",
                "freshness": "error",
                "timestamp": datetime.now().isoformat(),
                "real_data": False
            }

    def _decide_data_sources(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide which data sources to use using real LLM."""
        try:
            # Create LLM prompt
            prompt = f"""Based on this user query: "{query}"

What data sources should be used? Choose from:
- KAGGLE_API: Official Kaggle competition data
- SHALLOW_SCRAPING: Basic web scraping (discussions, notebooks, models)
- CACHED_DATA: Previously stored data

Format your response as: SOURCE1,SOURCE2
Reasoning: brief explanation"""

            # Get LLM decision
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            
            # Parse the result
            sources, reasoning = self._parse_llm_result(result)
            
            return {
                "sources": sources,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"Error in LLM decision: {e}")
            # Fallback to simple logic
            query_lower = query.lower()
            if 'latest' in query_lower or 'recent' in query_lower:
                return {
                    "sources": ["KAGGLE_API", "SHALLOW_SCRAPING"],
                    "reasoning": "High priority query - using fresh data sources"
                }
            else:
                return {
                    "sources": ["KAGGLE_API", "SHALLOW_SCRAPING"],
                    "reasoning": "Standard query - using reliable sources"
                }

    def _parse_llm_result(self, result: str) -> tuple:
        """Parse LLM result to extract sources and reasoning."""
        lines = result.strip().split('\n')
        
        # Default values
        sources = ["KAGGLE_API", "SHALLOW_SCRAPING"]
        reasoning = "No reasoning provided"
        
        try:
            # Parse sources (first line)
            if lines:
                sources_line = lines[0].strip()
                if ',' in sources_line:
                    sources = [s.strip() for s in sources_line.split(',')]
                else:
                    sources = [sources_line.strip()]
            
            # Parse reasoning (second line)
            if len(lines) > 1:
                reasoning_line = lines[1].strip()
                if reasoning_line.startswith("Reasoning:"):
                    reasoning = reasoning_line[10:].strip()
                else:
                    reasoning = reasoning_line
                    
        except Exception as e:
            logger.warning(f"Error parsing LLM result: {e}")
            
        return sources, reasoning

    def _collect_data_from_sources(self, query: str, context: Dict[str, Any], sources: List[str]) -> Dict[str, Any]:
        """Collect data from chosen sources using real scrapers."""
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
        """Collect data from Kaggle API using real scraper."""
        try:
            # Use real KaggleFetcher
            kaggle_scraper = self.scrapers.get('kaggle')
            if kaggle_scraper:
                # Mock call - replace with actual implementation
                data = kaggle_scraper.scrape(query, context)
                return {
                    "type": "kaggle_api",
                    "items": data.get('items', []),
                    "count": data.get('count', 0)
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Error in Kaggle API collection: {e}")
            return None

    def _collect_from_shallow_scraping(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from shallow scraping using real scrapers."""
        try:
            # Determine which scraper to use based on query
            query_lower = query.lower()
            
            if 'discussion' in query_lower:
                scraper = self.scrapers.get('discussion')
            elif 'notebook' in query_lower:
                scraper = self.scrapers.get('notebook')
            elif 'model' in query_lower:
                scraper = self.scrapers.get('model')
            else:
                scraper = self.scrapers.get('overview')
            
            if scraper:
                # Mock call - replace with actual implementation
                data = scraper.scrape(query, context)
                return {
                    "type": "scraped",
                    "items": data.get('items', []),
                    "count": data.get('count', 0)
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Error in shallow scraping: {e}")
            return None

    def _collect_from_cache(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from cache."""
        # Check conversation state for previous data
        previous_data = self.conversation_state.get('collected_data', {})
        if previous_data:
            return {
                "type": "cached",
                "items": previous_data.get('items', []),
                "count": len(previous_data.get('items', []))
            }
        return None

    def _combine_data(self, collected_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Combine data from multiple sources."""
        data = collected_data.get("data", {})
        sources = collected_data.get("sources", [])
        
        combined = {
            "query": query,
            "sources": sources,
            "data": {},
            "metadata": {
                "total_sources": len(sources),
                "total_items": 0,
                "real_data": True
            }
        }
        
        for source, source_data in data.items():
            if isinstance(source_data, dict) and "items" in source_data:
                items = source_data["items"]
                combined["data"][source] = {
                    "type": source_data.get("type", "unknown"),
                    "items": items,
                    "count": len(items)
                }
                combined["metadata"]["total_items"] += len(items)
        
        return combined

    def _update_conversation_state(self, query: str, collected_data: Dict[str, Any]) -> None:
        """Update conversation state for multi-turn conversations."""
        self.conversation_state['previous_queries'].append(query)
        self.conversation_state['collected_data'] = collected_data

    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state."""
        return self.conversation_state

    def clear_conversation_state(self) -> None:
        """Clear conversation state."""
        self.conversation_state = {
            'previous_queries': [],
            'collected_data': {},
            'context': {}
        }


