"""
Data Source Decider - Refactored from ScrapingDecider
Decides what data sources to use based on query and context.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DataSourceDecider:
    """
    LLM-powered decision maker that determines what data sources to use
    based on user query and available context.
    """

    def __init__(self, llm):
        self.llm = llm
        self.chain = self._build_chain()

    def _build_chain(self) -> Runnable:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data retrieval strategist. Based on the user's query and available data sources, decide which sources to use and whether fresh data is needed.

Available data sources:
- CACHED_DATA: Previously scraped data (fast, but may be outdated)
- KAGGLE_API: Official Kaggle API data (reliable, real-time)
- SHALLOW_SCRAPING: Basic web scraping (good for overviews)
- PERPLEXITY_SEARCH: Real-time web search (for latest information)

Consider:
- Query urgency (real-time vs historical data)
- Data freshness requirements
- Query complexity
- Available cached data quality"""),
            ("human", """User query: {query}
Query context: {context}
Available cached data: {cached_data_info}
Data freshness: {data_freshness}

Which data sources should we use? 
Format: SOURCE1,SOURCE2,SOURCE3
Explain your reasoning briefly.""")
        ])

        return prompt | self.llm | StrOutputParser()

    def decide_data_sources(self, query: str, context: Dict[str, Any] = None, 
                          cached_data_info: str = "", data_freshness: str = "unknown") -> Dict[str, Any]:
        """
        Decide which data sources to use for the given query.
        
        Returns:
        {
            "sources": ["KAGGLE_API", "SHALLOW_SCRAPING"],
            "reasoning": "Need real-time data for this query",
            "priority": "high" | "medium" | "low"
        }
        """
        if context is None:
            context = {}
            
        metadata = {
            "query": query,
            "context": context.get("section", "general"),
            "cached_data_info": cached_data_info,
            "data_freshness": data_freshness
        }
        
        try:
            result = self.chain.invoke(metadata)
            
            # Parse the result
            lines = result.strip().split('\n')
            sources_line = lines[0] if lines else ""
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else "No reasoning provided"
            
            # Extract sources
            sources = [s.strip() for s in sources_line.split(',') if s.strip()]
            
            # Determine priority based on query urgency
            priority = self._determine_priority(query, sources)
            
            return {
                "sources": sources,
                "reasoning": reasoning,
                "priority": priority
            }
            
        except Exception as e:
            logger.error(f"Error in data source decision: {e}")
            # Fallback to safe defaults
            return {
                "sources": ["KAGGLE_API", "SHALLOW_SCRAPING"],
                "reasoning": "Fallback due to error",
                "priority": "medium"
            }

    def _determine_priority(self, query: str, sources: List[str]) -> str:
        """Determine query priority based on content and sources."""
        query_lower = query.lower()
        
        # High priority indicators
        if any(word in query_lower for word in ["urgent", "latest", "recent", "now", "current"]):
            return "high"
        
        # If using real-time sources, likely high priority
        if "PERPLEXITY_SEARCH" in sources or "KAGGLE_API" in sources:
            return "high"
            
        # If only using cached data, likely low priority
        if sources == ["CACHED_DATA"]:
            return "low"
            
        return "medium"

    def should_use_cached_data(self, query: str, cached_data_age_hours: float = 0) -> bool:
        """
        Determine if cached data is fresh enough for the query.
        
        Args:
            query: User query
            cached_data_age_hours: Age of cached data in hours
            
        Returns:
            True if cached data should be used, False if fresh data needed
        """
        query_lower = query.lower()
        
        # Always use fresh data for real-time queries
        if any(word in query_lower for word in ["latest", "recent", "now", "current", "today"]):
            return False
            
        # Use cached data if it's less than 6 hours old
        if cached_data_age_hours < 6:
            return True
            
        # Use cached data for historical queries
        if any(word in query_lower for word in ["historical", "past", "previous", "archive"]):
            return True
            
        # Default to fresh data for ambiguous cases
        return False

