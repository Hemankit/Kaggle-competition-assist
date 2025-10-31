"""
LangGraph Orchestrator - Mode 3
Workflow-based orchestration with external search integration.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional, Tuple, TypedDict
import logging
from datetime import datetime

# Import LangGraph
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

# Import our components
from external_search_agent import ExternalSearchAgent
from rag_adapter import RAGAdapter

# Import existing agents
try:
    from agents import (
        CompetitionSummaryAgent, NotebookExplainerAgent, DiscussionHelperAgent,
        ErrorDiagnosisAgent, CodeFeedbackAgent, ProgressMonitorAgent,
        TimelineCoachAgent, MultiHopReasoningAgent, IdeaInitiatorAgent,
        CommunityEngagementAgent
    )
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class WorkflowState(TypedDict):
    """State for LangGraph workflow."""
    query: str
    context: Dict[str, Any]
    analysis: Dict[str, Any]
    rag_result: Dict[str, Any]
    external_search_result: Optional[Dict[str, Any]]
    agent_results: Dict[str, Any]
    final_response: str
    success: bool
    error: Optional[str]

class LangGraphOrchestrator:
    """
    LangGraph-based multi-agent orchestrator with external search integration.
    Uses workflow-based orchestration for structured reasoning paths.
    """

    def __init__(self, perplexity_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        self.external_search_agent = ExternalSearchAgent(perplexity_api_key, google_api_key)
        self.rag_adapter = RAGAdapter(google_api_key)
        self.agents = self._initialize_agents()
        self.workflow_graph = self._build_workflow_graph()
        self.execution_traces = []

    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all available agents."""
        agents = {}
        
        if AGENTS_AVAILABLE:
            try:
                # Initialize existing agents
                agents.update({
                    'competition_summary': CompetitionSummaryAgent(),
                    'notebook_explainer': NotebookExplainerAgent(),
                    'discussion_helper': DiscussionHelperAgent(),
                    'error_diagnosis': ErrorDiagnosisAgent(),
                    'code_feedback': CodeFeedbackAgent(),
                    'progress_monitor': ProgressMonitorAgent(),
                    'timeline_coach': TimelineCoachAgent(),
                    'multihop_reasoning': MultiHopReasoningAgent(),
                    'idea_initiator': IdeaInitiatorAgent(),
                    'community_engagement': CommunityEngagementAgent()
                })
                logger.info("✅ All existing agents initialized")
            except Exception as e:
                logger.error(f"Error initializing agents: {e}")
        
        return agents

    def _build_workflow_graph(self) -> Optional[StateGraph]:
        """Build the LangGraph workflow for orchestration."""
        if not LANGGRAPH_AVAILABLE:
            logger.warning("LangGraph not available - using mock workflow")
            return None
        
        try:
            # Create the workflow graph
            workflow = StateGraph(WorkflowState)
            
            # Add nodes
            workflow.add_node("analyze_query", self._analyze_query_node)
            workflow.add_node("get_rag_data", self._get_rag_data_node)
            workflow.add_node("check_external_search", self._check_external_search_node)
            workflow.add_node("execute_external_search", self._execute_external_search_node)
            workflow.add_node("route_to_agents", self._route_to_agents_node)
            workflow.add_node("synthesize_results", self._synthesize_results_node)
            workflow.add_node("error_handler", self._error_handler_node)
            
            # Add edges
            workflow.add_edge("analyze_query", "get_rag_data")
            workflow.add_edge("get_rag_data", "check_external_search")
            
            # Conditional edge for external search
            workflow.add_conditional_edges(
                "check_external_search",
                self._should_use_external_search,
                {
                    "external_search": "execute_external_search",
                    "skip_external": "route_to_agents"
                }
            )
            
            workflow.add_edge("execute_external_search", "route_to_agents")
            workflow.add_edge("route_to_agents", "synthesize_results")
            workflow.add_edge("synthesize_results", END)
            
            # Error handling
            workflow.add_edge("error_handler", END)
            
            # Compile the graph
            compiled_graph = workflow.compile()
            logger.info("✅ LangGraph workflow compiled successfully")
            return compiled_graph
            
        except Exception as e:
            logger.error(f"Error building workflow graph: {e}")
            return None

    def _analyze_query_node(self, state: WorkflowState) -> WorkflowState:
        """Analyze the query to determine processing approach."""
        try:
            query = state["query"]
            context = state["context"]
            
            # Analyze query characteristics
            analysis = {
                "query_type": self._classify_query_type(query),
                "complexity": self._assess_complexity(query),
                "requires_external_search": self._needs_external_search(query),
                "suggested_agents": self._suggest_agents(query),
                "workflow_path": self._determine_workflow_path(query)
            }
            
            state["analysis"] = analysis
            logger.info(f"Query analyzed: {analysis}")
            
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            state["error"] = str(e)
            state["success"] = False
        
        return state

    def _get_rag_data_node(self, state: WorkflowState) -> WorkflowState:
        """Get data from RAG adapter."""
        try:
            query = state["query"]
            context = state["context"]
            
            # Get RAG data
            rag_result = self.rag_adapter.process_query(query, context)
            state["rag_result"] = rag_result
            
            logger.info(f"RAG data retrieved: {rag_result.get('rag_retrieval', {}).get('retrieved_count', 0)} documents")
            
        except Exception as e:
            logger.error(f"Error getting RAG data: {e}")
            state["error"] = str(e)
            state["success"] = False
        
        return state

    def _check_external_search_node(self, state: WorkflowState) -> WorkflowState:
        """Check if external search is needed."""
        try:
            query = state["query"]
            context = state["context"]
            rag_result = state["rag_result"]
            
            # Check if external search is needed
            should_search, reasoning, confidence = self.external_search_agent.should_use_external_search(
                query, rag_result.get('rag_retrieval', {}), context
            )
            
            # Update analysis with external search decision
            if "analysis" not in state:
                state["analysis"] = {}
            state["analysis"]["external_search_decision"] = {
                "should_search": should_search,
                "reasoning": reasoning,
                "confidence": confidence
            }
            
            logger.info(f"External search decision: {should_search} ({reasoning})")
            
        except Exception as e:
            logger.error(f"Error checking external search: {e}")
            state["error"] = str(e)
            state["success"] = False
        
        return state

    def _execute_external_search_node(self, state: WorkflowState) -> WorkflowState:
        """Execute external search if needed."""
        try:
            query = state["query"]
            context = state["context"]
            
            # Execute external search
            external_result = self.external_search_agent.search_external(query, context)
            state["external_search_result"] = external_result
            
            logger.info(f"External search completed: {external_result.get('success', False)}")
            
        except Exception as e:
            logger.error(f"Error executing external search: {e}")
            state["error"] = str(e)
            state["success"] = False
        
        return state

    def _route_to_agents_node(self, state: WorkflowState) -> WorkflowState:
        """Route to appropriate agents based on analysis."""
        try:
            query = state["query"]
            context = state["context"]
            analysis = state["analysis"]
            rag_result = state["rag_result"]
            
            # Get suggested agents
            suggested_agents = analysis.get("suggested_agents", [])
            agent_results = {}
            
            # Execute agents
            for agent_name in suggested_agents:
                if agent_name in self.agents:
                    try:
                        agent = self.agents[agent_name]
                        result = agent.run(query, context)
                        agent_results[agent_name] = result
                        logger.info(f"Agent {agent_name} executed successfully")
                    except Exception as e:
                        logger.error(f"Error executing agent {agent_name}: {e}")
                        agent_results[agent_name] = {"error": str(e)}
            
            state["agent_results"] = agent_results
            logger.info(f"Executed {len(agent_results)} agents")
            
        except Exception as e:
            logger.error(f"Error routing to agents: {e}")
            state["error"] = str(e)
            state["success"] = False
        
        return state

    def _synthesize_results_node(self, state: WorkflowState) -> WorkflowState:
        """Synthesize all results into a final response."""
        try:
            query = state["query"]
            context = state["context"]
            analysis = state["analysis"]
            rag_result = state["rag_result"]
            external_result = state.get("external_search_result")
            agent_results = state["agent_results"]
            
            # Create synthesized response
            final_response = self._create_synthesized_response(
                query, analysis, rag_result, external_result, agent_results
            )
            
            state["final_response"] = final_response
            state["success"] = True
            
            logger.info("Results synthesized successfully")
            
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            state["error"] = str(e)
            state["success"] = False
        
        return state

    def _error_handler_node(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in the workflow."""
        error = state.get("error", "Unknown error")
        logger.error(f"Workflow error: {error}")
        
        state["final_response"] = f"I encountered an error while processing your query: {error}. Please try again or rephrase your question."
        state["success"] = False
        
        return state

    def _should_use_external_search(self, state: WorkflowState) -> str:
        """Determine if external search should be used."""
        analysis = state.get("analysis", {})
        external_decision = analysis.get("external_search_decision", {})
        
        if external_decision.get("should_search", False):
            return "external_search"
        else:
            return "skip_external"

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query."""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['what', 'explain', 'describe']):
            return 'informational'
        elif any(keyword in query_lower for keyword in ['how', 'help', 'guide']):
            return 'instructional'
        elif any(keyword in query_lower for keyword in ['why', 'reason', 'cause']):
            return 'analytical'
        elif any(keyword in query_lower for keyword in ['best', 'recommend', 'suggest']):
            return 'recommendation'
        else:
            return 'general'

    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity."""
        if len(query.split()) > 20:
            return 'high'
        elif len(query.split()) > 10:
            return 'medium'
        else:
            return 'low'

    def _needs_external_search(self, query: str) -> bool:
        """Determine if query needs external search."""
        external_keywords = ['latest', 'recent', 'current', 'news', 'trend', 'update']
        return any(keyword in query.lower() for keyword in external_keywords)

    def _suggest_agents(self, query: str) -> List[str]:
        """Suggest which agents to use based on query."""
        query_lower = query.lower()
        suggested = []
        
        # Data analysis keywords
        if any(keyword in query_lower for keyword in ['data', 'analysis', 'dataset', 'features']):
            suggested.extend(['competition_summary', 'data_section'])
        
        # Code-related keywords
        if any(keyword in query_lower for keyword in ['code', 'error', 'bug', 'debug']):
            suggested.extend(['error_diagnosis', 'code_feedback'])
        
        # Discussion keywords
        if any(keyword in query_lower for keyword in ['discussion', 'community', 'forum']):
            suggested.extend(['discussion_helper', 'community_engagement'])
        
        # Strategy keywords
        if any(keyword in query_lower for keyword in ['strategy', 'plan', 'approach']):
            suggested.extend(['progress_monitor', 'timeline_coach', 'idea_initiator'])
        
        # Notebook keywords
        if any(keyword in query_lower for keyword in ['notebook', 'kernel', 'code']):
            suggested.append('notebook_explainer')
        
        # Default agents if no specific keywords
        if not suggested:
            suggested = ['competition_summary', 'multihop_reasoning']
        
        return suggested

    def _determine_workflow_path(self, query: str) -> str:
        """Determine the workflow path based on query."""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['data', 'analysis']):
            return 'data_analysis'
        elif any(keyword in query_lower for keyword in ['code', 'error']):
            return 'code_review'
        elif any(keyword in query_lower for keyword in ['strategy', 'plan']):
            return 'strategy_planning'
        elif any(keyword in query_lower for keyword in ['discussion', 'community']):
            return 'community_engagement'
        else:
            return 'general'

    def _create_synthesized_response(self, query: str, analysis: Dict[str, Any], 
                                   rag_result: Dict[str, Any], external_result: Optional[Dict[str, Any]], 
                                   agent_results: Dict[str, Any]) -> str:
        """Create a synthesized response from all sources."""
        
        response_parts = []
        
        # Add agent responses
        if agent_results:
            agent_responses = []
            for agent_name, result in agent_results.items():
                if isinstance(result, dict) and "response" in result:
                    agent_responses.append(f"**{agent_name.replace('_', ' ').title()}:** {result['response']}")
                elif isinstance(result, str):
                    agent_responses.append(f"**{agent_name.replace('_', ' ').title()}:** {result}")
            
            if agent_responses:
                response_parts.append("\n".join(agent_responses))
        
        # Add RAG insights
        if rag_result.get('rag_retrieval', {}).get('success'):
            retrieved_count = rag_result.get('rag_retrieval', {}).get('retrieved_count', 0)
            if retrieved_count > 0:
                response_parts.append(f"**Internal Data Insights:** Found {retrieved_count} relevant documents from our knowledge base.")
        
        # Add external search insights
        if external_result and external_result.get('success'):
            results_count = len(external_result.get('results', []))
            if results_count > 0:
                response_parts.append(f"**External Search:** Found {results_count} additional insights from external sources.")
        
        # Combine all parts
        if response_parts:
            return "\n\n".join(response_parts)
        else:
            return "I've analyzed your query using our workflow-based multi-agent system. While I couldn't find specific information, I'm ready to help with any follow-up questions."

    def run(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for LangGraph orchestration.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Complete orchestration result
        """
        if context is None:
            context = {}
            
        logger.info(f"LangGraph Orchestrator: Processing query '{query}'")
        
        try:
            if not self.workflow_graph:
                return {
                    "query": query,
                    "context": context,
                    "error": "LangGraph workflow not available",
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Initialize state
            initial_state = WorkflowState(
                query=query,
                context=context,
                analysis={},
                rag_result={},
                external_search_result=None,
                agent_results={},
                final_response="",
                success=False,
                error=None
            )
            
            # Execute workflow
            final_state = self.workflow_graph.invoke(initial_state)
            
            # Create result
            result = {
                "query": query,
                "context": context,
                "success": final_state.get("success", False),
                "final_response": final_state.get("final_response", ""),
                "analysis": final_state.get("analysis", {}),
                "rag_retrieval": {
                    "success": final_state.get("rag_result", {}).get('rag_retrieval', {}).get('success', False),
                    "retrieved_count": final_state.get("rag_result", {}).get('rag_retrieval', {}).get('retrieved_count', 0)
                },
                "external_search": {
                    "success": final_state.get("external_search_result", {}).get('success', False),
                    "results_count": len(final_state.get("external_search_result", {}).get('results', []))
                },
                "agent_results": final_state.get("agent_results", {}),
                "orchestrator": "LangGraph",
                "timestamp": datetime.now().isoformat()
            }
            
            # Update execution traces
            self._update_execution_traces(query, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in LangGraph orchestration: {e}")
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

    def _update_execution_traces(self, query: str, result: Dict[str, Any]) -> None:
        """Update execution traces for debugging and optimization."""
        self.execution_traces.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "success": result.get('success', False),
            "workflow_path": result.get('analysis', {}).get('workflow_path', 'unknown'),
            "agents_used": list(result.get('agent_results', {}).keys()),
            "external_search_used": result.get('external_search', {}).get('success', False)
        })

    def get_execution_traces(self) -> List[Dict[str, Any]]:
        """Get execution traces."""
        return self.execution_traces.copy()

    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the workflow."""
        if not self.workflow_graph:
            return {"error": "Workflow not available"}
        
        return {
            "workflow_type": "LangGraph",
            "nodes": [
                "analyze_query", "get_rag_data", "check_external_search",
                "execute_external_search", "route_to_agents", "synthesize_results"
            ],
            "conditional_edges": ["check_external_search"],
            "available_agents": list(self.agents.keys())
        }
