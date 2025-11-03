"""
Intelligent Router - Uses the same scraper patterns as the old architecture
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Import ChromaDB RAG Pipeline
try:
    from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# Import scrapers exactly like the old architecture
try:
    from scraper.overview_scraper import OverviewScraper
    from scraper.notebook_scraper_v2 import NotebookScraperV2
    from scraper.model_scraper_v2 import ModelScraperV2
    from scraper.discussion_scraper_v2 import DiscussionScraperV2
    from Kaggle_Fetcher.kaggle_fetcher import KaggleFetcher
    SCRAPERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some scrapers not available: {e}")
    SCRAPERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class IntelligentRouter:
    """
    Intelligent Router that uses the same scraper patterns as the old architecture.
    Routes queries to appropriate data sources and stores results in ChromaDB.
    """
    
    def __init__(self, google_api_key: Optional[str] = None):
        self.google_api_key = google_api_key
        self.scrapers = self._initialize_scrapers()
        self.rag_pipeline = self._initialize_rag_pipeline()
        
        logger.info("✅ Intelligent Router initialized successfully")
    
    def _initialize_scrapers(self) -> Dict[str, Any]:
        """Initialize scrapers using the same patterns as old architecture."""
        scrapers = {}
        
        if SCRAPERS_AVAILABLE:
            try:
                # Initialize scrapers exactly like the old architecture
                scrapers = {
                    'overview': OverviewScraper('titanic'),
                    'notebook': NotebookScraperV2(),
                    'model': ModelScraperV2(),
                    'discussion': DiscussionScraperV2('https://www.kaggle.com/c/titanic/discussion'),
                    'kaggle': KaggleFetcher()
                }
                
                logger.info("✅ All scrapers initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing scrapers: {e}")
                scrapers = {}
        
        return scrapers
    
    def _initialize_rag_pipeline(self) -> Optional[ChromaDBRAGPipeline]:
        """Initialize ChromaDB RAG Pipeline."""
        if RAG_AVAILABLE:
            try:
                pipeline = ChromaDBRAGPipeline()
                logger.info("✅ ChromaDB RAG Pipeline initialized")
                return pipeline
            except Exception as e:
                logger.error(f"Error initializing RAG pipeline: {e}")
                return None
        else:
            logger.warning("RAG pipeline not available")
            return None
    
    def route_and_collect(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route query to appropriate data sources and collect data.
        Uses the same scraper patterns as the old architecture.
        """
        if context is None:
            context = {}
        
        logger.info(f"Intelligent Router: Processing query '{query}'")
        
        # Collect data using the same patterns as old architecture
        collected_data = self._collect_data_old_architecture(query, context)
        
        # Store in ChromaDB if available
        if self.rag_pipeline and collected_data:
            try:
                self.rag_pipeline.run(query=query, documents=collected_data)
                logger.info("✅ Data stored in ChromaDB")
            except Exception as e:
                logger.error(f"Error storing data in ChromaDB: {e}")
        
        return {
            'query': query,
            'context': context,
            'collected_data': collected_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _collect_data_old_architecture(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect data using the exact same patterns as the old architecture.
        """
        collected_data = []
        query_lower = query.lower()
        
        # Use the same scraper patterns as old architecture
        try:
            # Overview scraping
            if 'overview' in query_lower or 'description' in query_lower:
                overview_scraper = self.scrapers.get('overview')
                if overview_scraper:
                    data = overview_scraper.scrape()  # No arguments, like old architecture
                    collected_data.append({
                        'type': 'overview',
                        'data': data,
                        'source': 'overview_scraper'
                    })
            
            # Discussion scraping
            if 'discussion' in query_lower or 'forum' in query_lower:
                discussion_scraper = self.scrapers.get('discussion')
                if discussion_scraper:
                    data = discussion_scraper.scrape()  # No arguments, like old architecture
                    collected_data.append({
                        'type': 'discussion',
                        'data': data,
                        'source': 'discussion_scraper'
                    })
            
            # Model scraping
            if 'model' in query_lower or 'submission' in query_lower:
                model_scraper = self.scrapers.get('model')
                if model_scraper:
                    data = model_scraper.scrape_models()  # Like old architecture
                    collected_data.append({
                        'type': 'model',
                        'data': data,
                        'source': 'model_scraper'
                    })
            
            # Notebook scraping
            if 'notebook' in query_lower or 'code' in query_lower:
                notebook_scraper = self.scrapers.get('notebook')
                if notebook_scraper:
                    data = notebook_scraper.scrape()  # No arguments, like old architecture
                    collected_data.append({
                        'type': 'notebook',
                        'data': data,
                        'source': 'notebook_scraper'
                    })
            
            # Kaggle API data
            if 'data' in query_lower or 'dataset' in query_lower:
                kaggle_fetcher = self.scrapers.get('kaggle')
                if kaggle_fetcher:
                    data = kaggle_fetcher.fetch_dataset_metadata('titanic')  # Like old architecture
                    collected_data.append({
                        'type': 'kaggle_data',
                        'data': data,
                        'source': 'kaggle_fetcher'
                    })
            
            # Kaggle API leaderboard
            if 'leaderboard' in query_lower or 'ranking' in query_lower:
                kaggle_fetcher = self.scrapers.get('kaggle')
                if kaggle_fetcher:
                    data = kaggle_fetcher.fetch_leaderboard_metadata('titanic')  # Like old architecture
                    collected_data.append({
                        'type': 'kaggle_leaderboard',
                        'data': data,
                        'source': 'kaggle_fetcher'
                    })
            
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
        
        return collected_data

# Test function
if __name__ == "__main__":
    router = IntelligentRouter()
    
    # Test with a simple query
    result = router.route_and_collect("What are the latest discussions?")
    print("Test result:", result)








