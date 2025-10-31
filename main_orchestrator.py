"""
Main Orchestrator - Coordinates the two-stage architecture
Stage 1: Scraper Router (data collection)
Stage 2: Agent Router (data processing) - to be implemented later
"""

import logging
from typing import Dict, Any, Optional

from scraper_router.scraper_router import ScraperRouter
from core_utils.simple_cache import SimpleCache

logger = logging.getLogger(__name__)

class MainOrchestrator:
    """
    Main orchestrator for the new two-stage architecture.
    Currently implements Stage 1 (Scraper Router) only.
    """

    def __init__(self, llm, perplexity_api_key: Optional[str] = None):
        self.llm = llm
        self.perplexity_api_key = perplexity_api_key
        
        # Initialize Stage 1: Scraper Router
        self.scraper_router = ScraperRouter(llm, perplexity_api_key)
        
        # Initialize utilities
        self.cache = SimpleCache()

    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for processing queries.
        
        Args:
            query: User query
            context: Additional context (section, competition, etc.)
            
        Returns:
            {
                "stage1_data": collected_data,
                "stage2_response": "Not implemented yet",
                "architecture": "two_stage",
                "current_stage": 1
            }
        """
        if context is None:
            context = {}
            
        logger.info(f"Main Orchestrator: Processing query '{query}'")
        
        try:
            # Stage 1: Scraper Router - Collect Data
            stage1_result = self.scraper_router.route_and_collect_data(query, context)
            logger.info(f"Stage 1 completed: {len(stage1_result.get('sources_used', []))} sources used")
            
            # Stage 2: Agent Router - Process Data (Not implemented yet)
            stage2_result = {
                "response": "Agent Router not implemented yet",
                "agent_used": "none",
                "reasoning": "Stage 2 pending implementation"
            }
            
            return {
                "query": query,
                "context": context,
                "stage1_data": stage1_result,
                "stage2_response": stage2_result,
                "architecture": "two_stage",
                "current_stage": 1,
                "timestamp": stage1_result.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Error in main orchestrator: {e}")
            return {
                "query": query,
                "context": context,
                "stage1_data": {"error": str(e)},
                "stage2_response": {"error": "Stage 1 failed"},
                "architecture": "two_stage",
                "current_stage": 0,
                "error": str(e)
            }

    def get_architecture_status(self) -> Dict[str, Any]:
        """Get the current status of the architecture implementation."""
        return {
            "architecture": "two_stage",
            "stages": {
                "stage1_scraper_router": {
                    "status": "implemented",
                    "description": "Data collection and source routing",
                    "components": [
                        "DataSourceDecider",
                        "ScraperRouter", 
                        "DataCombiner",
                        "SimpleCache"
                    ]
                },
                "stage2_agent_router": {
                    "status": "pending",
                    "description": "Data processing and response generation",
                    "components": [
                        "AgentSelector",
                        "ConversationAgent",
                        "ReasoningAgent",
                        "ResponseFormatter"
                    ]
                }
            },
            "current_capability": "Data collection only",
            "next_steps": "Implement Stage 2 (Agent Router)"
        }

