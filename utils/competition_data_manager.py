"""
Competition Data Manager - Lazy Loading with ChromaDB Caching

This module provides on-demand data fetching for any Kaggle competition:
1. Check if competition data exists in ChromaDB cache
2. If not, scrape competition data (overview, notebooks, discussions)
3. Index into ChromaDB for future queries (caching)
4. Return success status

This enables V2.0 to work with ANY competition dynamically!
"""

import logging
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CompetitionDataManager:
    """
    Manages competition data availability in ChromaDB.
    Ensures data exists by scraping on-demand if needed.
    """
    
    def __init__(self, rag_pipeline, kaggle_fetcher=None, discussion_scraper=None):
        """
        Initialize with RAG pipeline and optional scrapers.
        
        Args:
            rag_pipeline: ChromaDBRAGPipeline instance for caching
            kaggle_fetcher: Optional Kaggle API fetcher for overview/notebooks
            discussion_scraper: Optional discussion scraper
        """
        self.rag_pipeline = rag_pipeline
        self.kaggle_fetcher = kaggle_fetcher
        self.discussion_scraper = discussion_scraper
        
    def check_data_exists(self, competition_slug: str, section: str) -> bool:
        """
        Check if data exists in ChromaDB for given competition and section.
        
        Args:
            competition_slug: Competition identifier (e.g., "titanic", "house-prices")
            section: Section to check ("overview", "discussion", "code")
            
        Returns:
            bool: True if data exists, False otherwise
        """
        try:
            # Try to retrieve documents for this competition/section
            results = self.rag_pipeline.rerank_document_store(
                query="test",  # Dummy query
                top_k_retrieval=1,
                top_k_final=1,
                competition_slug=competition_slug,
                section=section
            )
            
            # If we got results, data exists
            exists = len(results) > 0
            logger.info(f"Data check for {competition_slug}/{section}: {'EXISTS' if exists else 'MISSING'}")
            return exists
            
        except Exception as e:
            logger.warning(f"Error checking data for {competition_slug}/{section}: {e}")
            return False
    
    def ensure_data_available(self, competition_slug: str, sections: List[str] = None) -> Dict[str, bool]:
        """
        Ensure competition data is available for specified sections.
        Scrapes and indexes if missing from cache.
        
        Args:
            competition_slug: Competition identifier
            sections: List of sections to ensure (default: ["overview", "code", "discussion"])
            
        Returns:
            Dict mapping section to success status
        """
        if sections is None:
            sections = ["overview", "code", "discussion"]
        
        results = {}
        
        for section in sections:
            # Check if data exists
            if self.check_data_exists(competition_slug, section):
                logger.info(f"[CACHE HIT] {competition_slug}/{section} already in ChromaDB")
                results[section] = True
                continue
            
            # Data missing - scrape and index
            logger.info(f"[CACHE MISS] {competition_slug}/{section} not found. Scraping...")
            
            try:
                if section == "overview":
                    success = self._fetch_and_index_overview(competition_slug)
                elif section == "code":
                    success = self._fetch_and_index_notebooks(competition_slug)
                elif section == "discussion":
                    success = self._fetch_and_index_discussions(competition_slug)
                else:
                    logger.warning(f"Unknown section: {section}")
                    success = False
                
                results[section] = success
                
            except Exception as e:
                logger.error(f"Failed to fetch {competition_slug}/{section}: {e}")
                results[section] = False
        
        return results
    
    def _fetch_and_index_overview(self, competition_slug: str) -> bool:
        """Fetch competition overview from Kaggle API and index."""
        if not self.kaggle_fetcher:
            logger.warning("No Kaggle fetcher available for overview")
            return False
        
        try:
            # Use Kaggle API to fetch competition details
            from kaggle import api
            api.authenticate()
            
            competitions = api.competitions_list(search=competition_slug)
            if not competitions:
                logger.error(f"Competition not found: {competition_slug}")
                return False
            
            comp = competitions[0]
            
            # Create overview document
            content = f"""
Competition: {comp.title}
Slug: {competition_slug}
Category: {getattr(comp, 'category', 'Unknown')}
Deadline: {getattr(comp, 'deadline', 'Unknown')}
Reward: {getattr(comp, 'reward', 'Knowledge')}

Description:
{getattr(comp, 'description', 'No description available')}

URL: https://www.kaggle.com/c/{competition_slug}
"""
            
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
            
            doc = {
                'content': content,
                'section': 'overview',
                'content_hash': content_hash,
                'competition_slug': competition_slug,
                'title': comp.title,
                'source': 'kaggle_api'
            }
            
            # Index into ChromaDB
            result = self.rag_pipeline.chunker.chunk_and_index(
                pydantic_results=[],
                structured_results=[doc],
                indexer=self.rag_pipeline.indexer
            )
            
            logger.info(f"Indexed overview for {competition_slug}")
            return result.get("status") == "success"
            
        except Exception as e:
            logger.error(f"Error fetching overview for {competition_slug}: {e}")
            return False
    
    def _fetch_and_index_notebooks(self, competition_slug: str) -> bool:
        """Fetch competition notebooks from Kaggle API and index."""
        try:
            from kaggle import api
            api.authenticate()
            
            notebooks = api.kernels_list(
                competition=competition_slug,
                page_size=20,
                sort_by='voteCount'
            )
            
            if not notebooks:
                logger.warning(f"No notebooks found for {competition_slug}")
                return False
            
            notebook_docs = []
            
            for notebook in notebooks:
                ref_parts = notebook.ref.split('/')
                author = ref_parts[0] if len(ref_parts) > 0 else 'Unknown'
                is_pinned = notebook.totalVotes > 1000 if hasattr(notebook, 'totalVotes') else False
                
                content = f"""
Notebook: {notebook.title}
Author: {author}
Type: {'PINNED (Official/Featured)' if is_pinned else 'Community Notebook'}
URL: https://www.kaggle.com/code/{notebook.ref}

Competition: {competition_slug}

This notebook demonstrates various techniques and approaches for the {competition_slug} competition.
"""
                
                content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
                
                notebook_docs.append({
                    'content': content,
                    'section': 'code',
                    'content_hash': content_hash,
                    'competition_slug': competition_slug,
                    'title': notebook.title,
                    'author': author,
                    'notebook_ref': notebook.ref,
                    'is_pinned': is_pinned,
                    'source': 'kaggle_api_notebooks'
                })
            
            # Index into ChromaDB
            result = self.rag_pipeline.chunker.chunk_and_index(
                pydantic_results=[],
                structured_results=notebook_docs,
                indexer=self.rag_pipeline.indexer
            )
            
            logger.info(f"Indexed {len(notebook_docs)} notebooks for {competition_slug}")
            return result.get("status") == "success"
            
        except Exception as e:
            logger.error(f"Error fetching notebooks for {competition_slug}: {e}")
            return False
    
    def _fetch_and_index_discussions(self, competition_slug: str) -> bool:
        """Fetch competition discussions using scraper and index."""
        if not self.discussion_scraper:
            logger.warning("No discussion scraper available")
            return False
        
        try:
            from scraper.discussion_scraper_v2 import DiscussionScraperV2
            
            scraper = DiscussionScraperV2(
                input_link=competition_slug,
                output_dir="data/discussions"
            )
            
            discussions_data = scraper.scrape(retries=2, apply_ocr=False)
            
            if not discussions_data:
                logger.warning(f"No discussions scraped for {competition_slug}")
                return False
            
            discussion_docs = []
            
            for disc in discussions_data:
                title = disc.get('title', 'Unknown')
                author = disc.get('author', 'Unknown')
                content = disc.get('content', '')
                date = disc.get('date', 'Unknown')
                is_pinned = disc.get('is_pinned', False)
                
                doc_content = f"""
Discussion: {title}
Author: {author}
Date: {date}
Type: {'[PINNED]' if is_pinned else 'Community Discussion'}

Content:
{content}

Competition: {competition_slug}
"""
                
                content_hash = hashlib.sha256(doc_content.encode('utf-8')).hexdigest()[:16]
                
                discussion_docs.append({
                    'content': doc_content,
                    'section': 'discussion',
                    'content_hash': content_hash,
                    'competition_slug': competition_slug,
                    'title': title,
                    'author': author,
                    'is_pinned': is_pinned,
                    'date': date,
                    'source': 'discussion_scraper_v2'
                })
            
            # Index into ChromaDB
            result = self.rag_pipeline.chunker.chunk_and_index(
                pydantic_results=[],
                structured_results=discussion_docs,
                indexer=self.rag_pipeline.indexer
            )
            
            logger.info(f"Indexed {len(discussion_docs)} discussions for {competition_slug}")
            return result.get("status") == "success"
            
        except Exception as e:
            logger.error(f"Error fetching discussions for {competition_slug}: {e}")
            return False
    
    def get_cached_competitions(self) -> List[str]:
        """
        Get list of competitions currently cached in ChromaDB.
        
        Returns:
            List of competition slugs
        """
        try:
            # Query ChromaDB collection for unique competition_slugs
            collection = self.rag_pipeline.indexer._get_collection()
            
            # Get all documents (limit to reasonable number)
            results = collection.get(limit=1000)
            
            # Extract unique competition slugs
            slugs = set()
            for metadata in results.get('metadatas', []):
                if 'competition_slug' in metadata:
                    slugs.add(metadata['competition_slug'])
            
            logger.info(f"Found {len(slugs)} cached competitions: {slugs}")
            return list(slugs)
            
        except Exception as e:
            logger.error(f"Error getting cached competitions: {e}")
            return []

