"""
Master Orchestrator - Coordinates all 4 orchestration modes
Main entry point for the complete multi-agent system.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Import all orchestrators
from crewai_orchestrator import CrewAIOrchestrator
from autogen_orchestrator import AutoGenOrchestrator
from langgraph_orchestrator import LangGraphOrchestrator
from dynamic_orchestrator import DynamicOrchestrator
from hybrid_agent_router import HybridAgentRouter

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    """
    Master orchestrator that coordinates all 4 orchestration modes.
    Provides a unified interface for the complete multi-agent system.
    """

    def __init__(self, perplexity_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        self.perplexity_api_key = perplexity_api_key
        self.google_api_key = google_api_key
        
        # Initialize all orchestrators
        self.orchestrators = {
            'crewai': CrewAIOrchestrator(perplexity_api_key, google_api_key),
            'autogen': AutoGenOrchestrator(perplexity_api_key, google_api_key),
            'langgraph': LangGraphOrchestrator(perplexity_api_key, google_api_key),
            'dynamic': DynamicOrchestrator(perplexity_api_key, google_api_key)
        }
        
        # Initialize hybrid agent router
        self.hybrid_router = HybridAgentRouter(perplexity_api_key, google_api_key)
        
        # System state
        self.execution_history = []
        self.performance_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'mode_usage': {'crewai': 0, 'autogen': 0, 'langgraph': 0, 'dynamic': 0},
            'average_response_time': 0.0
        }

    def run(self, query: str, context: Dict[str, Any] = None, mode: str = "dynamic") -> Dict[str, Any]:
        """
        Main entry point for the master orchestrator.
        
        Args:
            query: User query
            context: Additional context
            mode: Orchestration mode ("crewai", "autogen", "langgraph", "dynamic")
            
        Returns:
            Complete orchestration result
        """
        if context is None:
            context = {}
            
        logger.info(f"Master Orchestrator: Processing query '{query}' with mode '{mode}'")
        
        start_time = datetime.now()
        
        try:
            # Validate mode
            if mode not in self.orchestrators:
                return {
                    "query": query,
                    "context": context,
                    "error": f"Invalid mode '{mode}'. Available modes: {list(self.orchestrators.keys())}",
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Execute with selected mode
            orchestrator = self.orchestrators[mode]
            result = orchestrator.run(query, context)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Add master orchestrator metadata
            result['master_orchestrator'] = {
                'mode': mode,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'available_modes': list(self.orchestrators.keys())
            }
            
            # Update performance metrics
            self._update_performance_metrics(mode, result['success'], execution_time)
            
            # Update execution history
            self._update_execution_history(query, mode, result, execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in master orchestration: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "success": False,
                "master_orchestrator": {
                    "mode": mode,
                    "execution_time": execution_time,
                    "error": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }

    def run_with_hybrid_routing(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run with hybrid agent routing (recommended approach).
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Complete orchestration result with hybrid routing
        """
        if context is None:
            context = {}
            
        logger.info(f"Master Orchestrator: Processing query '{query}' with hybrid routing")
        
        start_time = datetime.now()
        
        try:
            # Get routing plan from hybrid router
            routing_plan = self.hybrid_router.route_agents(query, context)
            
            if not routing_plan.get('success', False):
                return {
                    "query": query,
                    "context": context,
                    "error": "Hybrid routing failed",
                    "success": False,
                    "routing_plan": routing_plan,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Execute based on routing plan
            execution_result = self._execute_routing_plan(query, context, routing_plan)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Combine results
            final_result = {
                "query": query,
                "context": context,
                "success": execution_result.get('success', False),
                "routing_plan": routing_plan,
                "execution_result": execution_result,
                "master_orchestrator": {
                    "mode": "hybrid_routing",
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Update performance metrics
            self._update_performance_metrics("hybrid", final_result['success'], execution_time)
            
            # Update execution history
            self._update_execution_history(query, "hybrid", final_result, execution_time)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in hybrid routing: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "success": False,
                "master_orchestrator": {
                    "mode": "hybrid_routing",
                    "execution_time": execution_time,
                    "error": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }

    def _execute_routing_plan(self, query: str, context: Dict[str, Any], routing_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the routing plan."""
        try:
            selected_agents = routing_plan.get('selected_agents', [])
            external_search_needed = routing_plan.get('external_search', {}).get('needed', False)
            strategy = routing_plan.get('routing_strategy', 'sequential_internal')
            
            results = {
                "internal_agents": {},
                "external_search": None,
                "synthesis": None
            }
            
            # Execute internal agents
            for agent_info in selected_agents:
                agent_name = agent_info['agent_name']
                if agent_name in self.hybrid_router.agents:
                    try:
                        agent = self.hybrid_router.agents[agent_name]
                        agent_result = agent.run(query, context)
                        results["internal_agents"][agent_name] = agent_result
                    except Exception as e:
                        logger.error(f"Error executing agent {agent_name}: {e}")
                        results["internal_agents"][agent_name] = {"error": str(e)}
            
            # Execute external search if needed
            if external_search_needed:
                try:
                    external_result = self.hybrid_router.external_search_agent.search_external(query, context)
                    results["external_search"] = external_result
                except Exception as e:
                    logger.error(f"Error executing external search: {e}")
                    results["external_search"] = {"error": str(e)}
            
            # Synthesize results
            results["synthesis"] = self._synthesize_hybrid_results(query, results, routing_plan)
            
            return {
                "success": True,
                "results": results,
                "strategy_used": strategy
            }
            
        except Exception as e:
            logger.error(f"Error executing routing plan: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _synthesize_hybrid_results(self, query: str, results: Dict[str, Any], routing_plan: Dict[str, Any]) -> str:
        """Synthesize results from hybrid routing."""
        response_parts = []
        
        # Add internal agent results
        internal_results = results.get("internal_agents", {})
        if internal_results:
            agent_responses = []
            for agent_name, result in internal_results.items():
                if isinstance(result, dict) and "response" in result:
                    agent_responses.append(f"**{agent_name.replace('_', ' ').title()}:** {result['response']}")
                elif isinstance(result, str):
                    agent_responses.append(f"**{agent_name.replace('_', ' ').title()}:** {result}")
            
            if agent_responses:
                response_parts.append("\n".join(agent_responses))
        
        # Add external search results
        external_result = results.get("external_search")
        if external_result and external_result.get('success'):
            results_count = len(external_result.get('results', []))
            if results_count > 0:
                response_parts.append(f"**External Search:** Found {results_count} additional insights from external sources.")
        
        # Add RAG insights
        rag_data = routing_plan.get('rag_data', {})
        if rag_data.get('success'):
            retrieved_count = rag_data.get('retrieved_count', 0)
            if retrieved_count > 0:
                response_parts.append(f"**Internal Data:** Found {retrieved_count} relevant documents from our knowledge base.")
        
        # Combine all parts
        if response_parts:
            return "\n\n".join(response_parts)
        else:
            return "I've analyzed your query using our hybrid multi-agent system. While I couldn't find specific information, I'm ready to help with any follow-up questions."

    def _update_performance_metrics(self, mode: str, success: bool, execution_time: float) -> None:
        """Update performance metrics."""
        self.performance_metrics['total_queries'] += 1
        
        if success:
            self.performance_metrics['successful_queries'] += 1
        else:
            self.performance_metrics['failed_queries'] += 1
        
        if mode in self.performance_metrics['mode_usage']:
            self.performance_metrics['mode_usage'][mode] += 1
        
        # Update average response time (exponential moving average)
        alpha = 0.1
        current_avg = self.performance_metrics['average_response_time']
        new_avg = alpha * execution_time + (1 - alpha) * current_avg
        self.performance_metrics['average_response_time'] = new_avg

    def _update_execution_history(self, query: str, mode: str, result: Dict[str, Any], execution_time: float) -> None:
        """Update execution history."""
        self.execution_history.append({
            "query": query,
            "mode": mode,
            "success": result.get('success', False),
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        })

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "orchestrators": {
                "available": list(self.orchestrators.keys()),
                "status": "operational"
            },
            "hybrid_router": {
                "available": True,
                "status": "operational"
            },
            "performance_metrics": self.performance_metrics,
            "execution_history": {
                "total_queries": len(self.execution_history),
                "recent_queries": self.execution_history[-10:] if self.execution_history else []
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history.copy()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.performance_metrics.copy()

    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self.performance_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'mode_usage': {'crewai': 0, 'autogen': 0, 'langgraph': 0, 'dynamic': 0},
            'average_response_time': 0.0
        }
        self.execution_history = []

    def get_available_modes(self) -> List[str]:
        """Get list of available orchestration modes."""
        return list(self.orchestrators.keys()) + ["hybrid_routing"]

    def get_mode_info(self, mode: str) -> Dict[str, Any]:
        """Get information about a specific mode."""
        if mode == "hybrid_routing":
            return {
                "mode": "hybrid_routing",
                "description": "Hybrid agent routing with smart selection",
                "features": ["Smart agent selection", "External search integration", "Adaptive routing"],
                "best_for": ["Complex queries", "Multi-domain questions", "Optimal performance"]
            }
        elif mode in self.orchestrators:
            return {
                "mode": mode,
                "description": f"{mode.title()} orchestration mode",
                "features": self._get_mode_features(mode),
                "best_for": self._get_mode_use_cases(mode)
            }
        else:
            return {"error": f"Mode '{mode}' not found"}

    def _get_mode_features(self, mode: str) -> List[str]:
        """Get features for a specific mode."""
        features = {
            "crewai": ["Crew-based collaboration", "Sequential/parallel execution", "Built-in delegation"],
            "autogen": ["Conversational agents", "Back-and-forth reasoning", "Automatic conversation management"],
            "langgraph": ["Workflow-based", "Structured reasoning", "Deterministic paths"],
            "dynamic": ["Self-selecting", "Adaptive framework", "Performance-based selection"]
        }
        return features.get(mode, [])

    def _get_mode_use_cases(self, mode: str) -> List[str]:
        """Get use cases for a specific mode."""
        use_cases = {
            "crewai": ["Team collaboration", "Structured tasks", "Clear workflows"],
            "autogen": ["Complex reasoning", "Interactive problem solving", "Multi-turn conversations"],
            "langgraph": ["Deterministic workflows", "Structured processes", "Step-by-step analysis"],
            "dynamic": ["Optimal performance", "Adaptive selection", "Best framework choice"]
        }
        return use_cases.get(mode, [])
