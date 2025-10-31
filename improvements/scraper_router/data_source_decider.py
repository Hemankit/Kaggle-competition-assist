"""
Data Source Decider - Refactored from ScrapingDecider
LLM-powered decision making about what data sources to use.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DataSourceDecider:
    """
    LLM-powered decision making about what data sources to use.
    Refactored from ScrapingDecider to focus on data source selection.
    """

    def __init__(self, llm):
        self.llm = llm
        self.chain = self._build_chain()

    def _build_chain(self) -> Runnable:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data source router. Based on the user's query and available metadata, decide the optimal data retrieval strategy.

Available data sources:
- KAGGLE_API: Official Kaggle competition data (reliable, structured)
- SHALLOW_SCRAPING: Basic web scraping (fast, limited depth)
- PERPLEXITY_SEARCH: Real-time search for current information
- CACHED_DATA: Previously stored data (fast, may be outdated)

Consider:
- Query urgency (latest vs historical)
- Data freshness requirements
- Available cached data
- Query complexity and specificity"""),
            ("human", """User query: {query}
Context: {context}
Cached data info: {cached_data_info}
Data freshness: {data_freshness}

What data sources should be used? List them in order of priority.
Format: SOURCE1,SOURCE2,SOURCE3
Reasoning: brief explanation""")
        ])

        return prompt | self.llm | StrOutputParser()

    def decide_data_sources(self, query: str, context: Dict[str, Any], 
                           cached_data_info: str = "No cached data", 
                           data_freshness: str = "unknown") -> Dict[str, Any]:
        """
        Decide which data sources to use for a given query.
        
        Args:
            query: User query
            context: Additional context (section, competition, etc.)
            cached_data_info: Information about available cached data
            data_freshness: How fresh the data needs to be
            
        Returns:
            {
                "sources": ["KAGGLE_API", "SHALLOW_SCRAPING"],
                "priority": "high" | "medium" | "low",
                "reasoning": "explanation"
            }
        """
        try:
            metadata = {
                "query": query,
                "context": context,
                "cached_data_info": cached_data_info,
                "data_freshness": data_freshness
            }
            
            result = self.chain.invoke(metadata)
            
            # Parse the result
            sources, reasoning = self._parse_result(result)
            
            # Determine priority
            priority = self._determine_priority(query, sources, context)
            
            return {
                "sources": sources,
                "priority": priority,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"Error in data source decision: {e}")
            # Fallback to basic sources
            return {
                "sources": ["KAGGLE_API", "SHALLOW_SCRAPING"],
                "priority": "medium",
                "reasoning": f"Fallback due to error: {str(e)}"
            }

    def _parse_result(self, result: str) -> tuple:
        """Parse the LLM result to extract sources and reasoning."""
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
            logger.warning(f"Error parsing data source result: {e}")
            
        return sources, reasoning

    def _determine_priority(self, query: str, sources: List[str], context: Dict[str, Any]) -> str:
        """Determine the priority level based on query and sources."""
        query_lower = query.lower()
        
        # High priority indicators
        high_priority_indicators = [
            "latest", "recent", "current", "now", "today",
            "urgent", "asap", "immediately", "quickly"
        ]
        
        # Low priority indicators
        low_priority_indicators = [
            "historical", "past", "old", "archive", "summary",
            "overview", "general", "background"
        ]
        
        # Check for high priority indicators
        if any(indicator in query_lower for indicator in high_priority_indicators):
            return "high"
            
        # Check for low priority indicators
        if any(indicator in query_lower for indicator in low_priority_indicators):
            return "low"
            
        # Check if real-time sources are used
        if "PERPLEXITY_SEARCH" in sources:
            return "high"
            
        # Check if only cached data is used
        if sources == ["CACHED_DATA"]:
            return "low"
            
        # Default to medium priority
        return "medium"