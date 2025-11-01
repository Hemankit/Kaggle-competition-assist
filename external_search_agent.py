"""
External Search Agent - Perplexity API Integration
Specialized agent for external search with cost-aware decision making.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional, Tuple
import logging
import time
from datetime import datetime

# Import LLM for query analysis
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Import Perplexity API
try:
    from langchain_perplexity import ChatPerplexity
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False

logger = logging.getLogger(__name__)

class ExternalSearchAgent:
    """
    External Search Agent using Perplexity API.
    Specialized for real-time external information retrieval.
    """

    def __init__(self, perplexity_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        self.perplexity_llm = self._initialize_perplexity(perplexity_api_key)
        self.analysis_llm = self._initialize_analysis_llm(google_api_key)
        self.usage_stats = {
            'queries_processed': 0,
            'api_calls_made': 0,
            'total_response_time': 0.0,
            'average_response_time': 0.0,
            'last_reset': datetime.now()
        }
        self.rate_limit_delay = 1.0  # Seconds between API calls

    def _initialize_perplexity(self, api_key: Optional[str] = None):
        """Initialize Perplexity API client."""
        if PERPLEXITY_AVAILABLE and api_key:
            try:
                return ChatPerplexity(
                    model="llama-3.1-sonar-small-128k-online",
                    api_key=api_key,
                    temperature=0.1
                )
            except Exception as e:
                logger.error(f"Error initializing Perplexity: {e}")
                return None
        else:
            logger.warning("Perplexity API not available - using mock")
            return self._get_mock_perplexity()

    def _initialize_analysis_llm(self, api_key: Optional[str] = None):
        """Initialize LLM for query analysis."""
        if LLM_AVAILABLE and api_key:
            try:
                return ChatGoogleGenerativeAI(
                    model='gemini-2.5-flash',
                    temperature=0.1
                )
            except Exception as e:
                logger.error(f"Error initializing analysis LLM: {e}")
                return self._get_mock_analysis_llm()
        else:
            return self._get_mock_analysis_llm()

    def _get_mock_perplexity(self):
        """Mock Perplexity for testing."""
        class MockPerplexity:
            def invoke(self, query):
                return f"Mock external search result for: {query}"
        return MockPerplexity()

    def _get_mock_analysis_llm(self):
        """Mock analysis LLM for testing."""
        class MockAnalysisLLM:
            def invoke(self, query):
                if "latest" in query.lower() or "recent" in query.lower():
                    return "EXTERNAL_SEARCH_NEEDED: Query requires fresh external data"
                else:
                    return "INTERNAL_SUFFICIENT: Query can be answered with internal data"
        return MockAnalysisLLM()

    def should_use_external_search(self, query: str, internal_data: Dict[str, Any], 
                                 context: Dict[str, Any] = None) -> Tuple[bool, str, float]:
        """
        Determine if external search is needed for comprehensive results.
        
        Args:
            query: User query
            internal_data: Data from internal sources (ChromaDB, scrapers)
            context: Additional context
            
        Returns:
            (should_search, reasoning, confidence_score)
        """
        if context is None:
            context = {}
            
        try:
            # Analyze query characteristics
            analysis_prompt = f"""Analyze this query to determine if external search would add value.

Query: "{query}"
Internal Data Available: {len(internal_data.get('retrieved_docs', []))} documents
Context: {context}

Consider these factors:
1. Query requires latest/real-time information
2. Query is about current events or recent developments
3. Internal data is insufficient or outdated
4. Query complexity requires external knowledge
5. User would benefit from comprehensive external perspective

Respond with:
EXTERNAL_SEARCH_NEEDED: [reasoning] | CONFIDENCE: [0.0-1.0]
or
INTERNAL_SUFFICIENT: [reasoning] | CONFIDENCE: [0.0-1.0]"""

            response = self.analysis_llm.invoke(analysis_prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            should_search, reasoning, confidence = self._parse_analysis(result)
            
            # Additional checks
            if self._is_rate_limited():
                should_search = False
                reasoning = "Rate limited - using internal data only"
                confidence = 0.9
                
            return should_search, reasoning, confidence
            
        except Exception as e:
            logger.error(f"Error in external search analysis: {e}")
            return False, f"Analysis error: {str(e)}", 0.0

    def _parse_analysis(self, result: str) -> Tuple[bool, str, float]:
        """Parse analysis result."""
        try:
            lines = result.strip().split('\n')
            decision_line = lines[0] if lines else ""
            
            if "EXTERNAL_SEARCH_NEEDED" in decision_line:
                should_search = True
                reasoning = decision_line.split(":", 1)[1].split("|")[0].strip()
            else:
                should_search = False
                reasoning = decision_line.split(":", 1)[1].split("|")[0].strip() if ":" in decision_line else "Internal data sufficient"
            
            # Extract confidence
            confidence = 0.7  # Default
            if "CONFIDENCE:" in decision_line:
                try:
                    conf_part = decision_line.split("CONFIDENCE:")[1].strip()
                    confidence = float(conf_part)
                except:
                    pass
                    
            return should_search, reasoning, confidence
            
        except Exception as e:
            logger.warning(f"Error parsing analysis: {e}")
            return False, "Parse error", 0.0

    def _is_rate_limited(self) -> bool:
        """Check if we're rate limited."""
        # Simple rate limiting - can be enhanced
        return self.usage_stats['api_calls_made'] > 10  # Max 10 calls per session

    def _is_cost_prohibitive(self, query: str) -> bool:
        """Check if query is too expensive - DISABLED since user has free access."""
        # Cost checks disabled since user has free Perplexity access
        return False

    def search_external(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform external search using Perplexity API.
        
        Args:
            query: Search query
            context: Additional context
            
        Returns:
            Search results with metadata
        """
        if context is None:
            context = {}
            
        logger.info(f"External Search Agent: Searching for '{query}'")
        
        try:
            # Rate limiting
            if self._is_rate_limited():
                return {
                    "success": False,
                    "error": "Rate limited",
                    "results": [],
                    "cost_estimate": 0.0
                }
            
            # Prepare search query
            search_query = self._prepare_search_query(query, context)
            
            # Perform search
            start_time = time.time()
            response = self.perplexity_llm.invoke(search_query)
            search_time = time.time() - start_time
            
            # Process results
            results = self._process_search_results(response, query)
            
            # Update usage stats
            self._update_usage_stats(query, search_time)
            
            return {
                "success": True,
                "results": results,
                "query": query,
                "search_time": search_time,
                "cost_estimate": self._estimate_cost(query),
                "timestamp": datetime.now().isoformat(),
                "source": "perplexity_api"
            }
            
        except Exception as e:
            logger.error(f"Error in external search: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "cost_estimate": 0.0
            }

    def _prepare_search_query(self, query: str, context: Dict[str, Any]) -> str:
        """Prepare query for external search."""
        # Enhance query with context
        enhanced_query = query
        
        if context.get('competition'):
            enhanced_query += f" related to {context['competition']} competition"
            
        if context.get('section'):
            enhanced_query += f" in {context['section']} section"
            
        # Add specific instructions for Perplexity
        enhanced_query += " Please provide recent, accurate information with sources."
        
        return enhanced_query

    def _process_search_results(self, response, original_query: str) -> List[Dict[str, Any]]:
        """Process Perplexity API response."""
        try:
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Create structured result
            result = {
                "title": f"External Search Result for: {original_query}",
                "content": content,
                "source": "perplexity_api",
                "timestamp": datetime.now().isoformat(),
                "relevance_score": 0.8,  # Default relevance
                "metadata": {
                    "query": original_query,
                    "search_type": "external",
                    "api_provider": "perplexity"
                }
            }
            
            return [result]
            
        except Exception as e:
            logger.error(f"Error processing search results: {e}")
            return []

    def _update_usage_stats(self, query: str, search_time: float) -> None:
        """Update usage statistics."""
        self.usage_stats['queries_processed'] += 1
        self.usage_stats['api_calls_made'] += 1
        self.usage_stats['total_response_time'] += search_time
        self.usage_stats['average_response_time'] = (
            self.usage_stats['total_response_time'] / self.usage_stats['api_calls_made']
        )

    def _estimate_cost(self, query: str) -> float:
        """Estimate API cost for query."""
        # Rough estimate based on query length
        # Perplexity pricing: ~$0.20 per 1M tokens
        estimated_tokens = len(query.split()) * 1.3  # Rough token estimation
        return estimated_tokens * 0.0000002  # Very rough cost estimate

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return self.usage_stats.copy()

    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        self.usage_stats = {
            'queries_processed': 0,
            'api_calls_made': 0,
            'total_response_time': 0.0,
            'average_response_time': 0.0,
            'last_reset': datetime.now()
        }

    def is_available(self) -> bool:
        """Check if external search is available."""
        return self.perplexity_llm is not None

    def get_cost_estimate(self, query: str) -> float:
        """Get cost estimate for a query."""
        return self._estimate_cost(query)

    def should_retry(self, error: str) -> bool:
        """Determine if we should retry after an error."""
        retryable_errors = [
            "rate limit",
            "timeout",
            "network",
            "temporary"
        ]
        return any(err in error.lower() for err in retryable_errors)
