"""
Hybrid Agent Router - Smart agent selection and coordination
Integrates internal agents with external search for optimal routing.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

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

class HybridAgentRouter:
    """
    Hybrid agent router that intelligently selects and coordinates agents.
    Combines internal agents with external search for comprehensive responses.
    """

    def __init__(self, perplexity_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        self.external_search_agent = ExternalSearchAgent(perplexity_api_key, google_api_key)
        self.rag_adapter = RAGAdapter(google_api_key)
        self.agents = self._initialize_agents()
        self.agent_capabilities = self._build_agent_capabilities()
        self.routing_history = []

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
                logger.info("✅ All agents initialized for hybrid routing")
            except Exception as e:
                logger.error(f"Error initializing agents: {e}")
        
        return agents

    def _build_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Build capability matrix for all agents."""
        return {
            'competition_summary': {
                'keywords': ['competition', 'overview', 'summary', 'description', 'rules', 'evaluation'],
                'query_types': ['informational', 'general'],
                'complexity': ['low', 'medium'],
                'specialties': ['competition_analysis', 'overview_generation'],
                'priority': 1
            },
            'notebook_explainer': {
                'keywords': ['notebook', 'kernel', 'code', 'implementation', 'tutorial', 'example'],
                'query_types': ['instructional', 'informational'],
                'complexity': ['medium', 'high'],
                'specialties': ['code_explanation', 'tutorial_generation'],
                'priority': 2
            },
            'discussion_helper': {
                'keywords': ['discussion', 'forum', 'post', 'comment', 'community', 'feedback'],
                'query_types': ['informational', 'analytical'],
                'complexity': ['low', 'medium', 'high'],
                'specialties': ['discussion_analysis', 'community_insights'],
                'priority': 2
            },
            'error_diagnosis': {
                'keywords': ['error', 'bug', 'debug', 'fix', 'problem', 'issue', 'troubleshoot'],
                'query_types': ['troubleshooting', 'instructional'],
                'complexity': ['medium', 'high'],
                'specialties': ['error_analysis', 'debugging'],
                'priority': 1
            },
            'code_feedback': {
                'keywords': ['code', 'review', 'feedback', 'improve', 'optimize', 'best practice'],
                'query_types': ['instructional', 'recommendation'],
                'complexity': ['medium', 'high'],
                'specialties': ['code_review', 'optimization'],
                'priority': 2
            },
            'progress_monitor': {
                'keywords': ['progress', 'monitor', 'track', 'status', 'performance', 'metrics'],
                'query_types': ['analytical', 'informational'],
                'complexity': ['medium', 'high'],
                'specialties': ['progress_analysis', 'performance_tracking'],
                'priority': 3
            },
            'timeline_coach': {
                'keywords': ['timeline', 'schedule', 'plan', 'deadline', 'milestone', 'roadmap'],
                'query_types': ['instructional', 'recommendation'],
                'complexity': ['medium', 'high'],
                'specialties': ['timeline_planning', 'project_management'],
                'priority': 3
            },
            'multihop_reasoning': {
                'keywords': ['reasoning', 'analysis', 'complex', 'multi-step', 'deep', 'thorough'],
                'query_types': ['analytical', 'comparative'],
                'complexity': ['high'],
                'specialties': ['complex_reasoning', 'multi_step_analysis'],
                'priority': 1
            },
            'idea_initiator': {
                'keywords': ['idea', 'suggestion', 'approach', 'strategy', 'innovation', 'creative'],
                'query_types': ['recommendation', 'instructional'],
                'complexity': ['medium', 'high'],
                'specialties': ['idea_generation', 'strategy_development'],
                'priority': 2
            },
            'community_engagement': {
                'keywords': ['community', 'engagement', 'social', 'interaction', 'collaboration'],
                'query_types': ['informational', 'recommendation'],
                'complexity': ['low', 'medium'],
                'specialties': ['community_management', 'social_interaction'],
                'priority': 3
            }
        }

    def route_agents(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route query to appropriate agents and external search.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Routing decision with selected agents and external search info
        """
        if context is None:
            context = {}
            
        logger.info(f"Hybrid Agent Router: Routing query '{query}'")
        
        try:
            # Step 1: Analyze query
            query_analysis = self._analyze_query(query, context)
            
            # Step 2: Get RAG data
            rag_result = self.rag_adapter.process_query(query, context)
            
            # Step 3: Select internal agents
            selected_agents = self._select_internal_agents(query, query_analysis)
            
            # Step 4: Determine external search need
            external_search_needed, external_reasoning, external_confidence = self.external_search_agent.should_use_external_search(
                query, rag_result.get('rag_retrieval', {}), context
            )
            
            # Step 5: Create routing plan
            routing_plan = self._create_routing_plan(
                query, context, selected_agents, external_search_needed, 
                external_reasoning, rag_result, query_analysis
            )
            
            # Step 6: Update routing history
            self._update_routing_history(query, routing_plan)
            
            return routing_plan
            
        except Exception as e:
            logger.error(f"Error in hybrid agent routing: {e}")
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

    def _analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to extract routing information."""
        query_lower = query.lower()
        
        return {
            'query_type': self._classify_query_type(query),
            'complexity': self._assess_complexity(query),
            'keywords': self._extract_keywords(query),
            'requires_external_search': self._needs_external_search(query),
            'requires_reasoning': self._requires_reasoning(query),
            'has_technical_terms': self._has_technical_terms(query),
            'query_length': len(query.split()),
            'urgency': self._assess_urgency(query)
        }

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query."""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ['what', 'explain', 'describe', 'tell me about']):
            return 'informational'
        elif any(keyword in query_lower for keyword in ['how', 'help', 'guide', 'tutorial']):
            return 'instructional'
        elif any(keyword in query_lower for keyword in ['why', 'reason', 'cause', 'explain why']):
            return 'analytical'
        elif any(keyword in query_lower for keyword in ['best', 'recommend', 'suggest', 'advice']):
            return 'recommendation'
        elif any(keyword in query_lower for keyword in ['compare', 'difference', 'vs', 'versus']):
            return 'comparative'
        elif any(keyword in query_lower for keyword in ['debug', 'error', 'fix', 'problem']):
            return 'troubleshooting'
        else:
            return 'general'

    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity."""
        word_count = len(query.split())
        
        if word_count > 25:
            return 'high'
        elif word_count > 15:
            return 'medium'
        else:
            return 'low'

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query."""
        query_lower = query.lower()
        keywords = []
        
        # Check against agent capabilities
        for agent_name, capabilities in self.agent_capabilities.items():
            agent_keywords = capabilities['keywords']
            for keyword in agent_keywords:
                if keyword in query_lower and keyword not in keywords:
                    keywords.append(keyword)
        
        return keywords

    def _needs_external_search(self, query: str) -> bool:
        """Determine if query needs external search."""
        external_keywords = ['latest', 'recent', 'current', 'news', 'trend', 'update', 'now']
        return any(keyword in query.lower() for keyword in external_keywords)

    def _requires_reasoning(self, query: str) -> bool:
        """Check if query requires complex reasoning."""
        reasoning_keywords = [
            'why', 'how', 'explain', 'analyze', 'compare', 'evaluate',
            'assess', 'determine', 'decide', 'choose', 'recommend'
        ]
        return any(keyword in query.lower() for keyword in reasoning_keywords)

    def _has_technical_terms(self, query: str) -> bool:
        """Check if query contains technical terms."""
        technical_terms = [
            'model', 'algorithm', 'feature', 'dataset', 'training', 'validation',
            'accuracy', 'precision', 'recall', 'f1', 'auc', 'rmse', 'mae',
            'neural', 'network', 'deep', 'learning', 'machine', 'ai', 'ml'
        ]
        return any(term in query.lower() for term in technical_terms)

    def _assess_urgency(self, query: str) -> str:
        """Assess query urgency."""
        urgent_keywords = ['urgent', 'asap', 'quickly', 'immediately', 'now', 'fast']
        if any(keyword in query.lower() for keyword in urgent_keywords):
            return 'high'
        elif 'latest' in query.lower() or 'recent' in query.lower():
            return 'medium'
        else:
            return 'low'

    def _select_internal_agents(self, query: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select appropriate internal agents based on query analysis."""
        selected_agents = []
        query_lower = query.lower()
        
        # Score each agent based on query analysis
        agent_scores = {}
        
        for agent_name, capabilities in self.agent_capabilities.items():
            score = 0
            
            # Keyword matching
            for keyword in capabilities['keywords']:
                if keyword in query_lower:
                    score += 2
            
            # Query type matching
            if analysis['query_type'] in capabilities['query_types']:
                score += 3
            
            # Complexity matching
            if analysis['complexity'] in capabilities['complexity']:
                score += 2
            
            # Special requirements
            if analysis['requires_reasoning'] and 'complex_reasoning' in capabilities['specialties']:
                score += 3
            
            if analysis['has_technical_terms'] and 'technical_analysis' in capabilities['specialties']:
                score += 2
            
            # Priority adjustment
            score += (4 - capabilities['priority'])  # Higher priority = higher score
            
            if score > 0:
                agent_scores[agent_name] = score
        
        # Select top agents (limit to 3 for performance)
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        top_agents = sorted_agents[:3]
        
        for agent_name, score in top_agents:
            selected_agents.append({
                'agent_name': agent_name,
                'score': score,
                'confidence': min(score / 10.0, 1.0),  # Normalize to 0-1
                'reasoning': self._generate_agent_reasoning(agent_name, query, analysis)
            })
        
        return selected_agents

    def _generate_agent_reasoning(self, agent_name: str, query: str, analysis: Dict[str, Any]) -> str:
        """Generate reasoning for agent selection."""
        capabilities = self.agent_capabilities[agent_name]
        reasoning_parts = []
        
        # Keyword match reasoning
        matched_keywords = [kw for kw in capabilities['keywords'] if kw in query.lower()]
        if matched_keywords:
            reasoning_parts.append(f"Keywords matched: {', '.join(matched_keywords)}")
        
        # Query type reasoning
        if analysis['query_type'] in capabilities['query_types']:
            reasoning_parts.append(f"Query type '{analysis['query_type']}' matches agent specialty")
        
        # Complexity reasoning
        if analysis['complexity'] in capabilities['complexity']:
            reasoning_parts.append(f"Complexity level '{analysis['complexity']}' is appropriate")
        
        # Special requirements reasoning
        if analysis['requires_reasoning'] and 'complex_reasoning' in capabilities['specialties']:
            reasoning_parts.append("Query requires complex reasoning")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "General match based on query characteristics"

    def _create_routing_plan(self, query: str, context: Dict[str, Any], selected_agents: List[Dict[str, Any]], 
                           external_search_needed: bool, external_reasoning: str, rag_result: Dict[str, Any], 
                           analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive routing plan."""
        
        return {
            "query": query,
            "context": context,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "rag_data": {
                "success": rag_result.get('rag_retrieval', {}).get('success', False),
                "retrieved_count": rag_result.get('rag_retrieval', {}).get('retrieved_count', 0),
                "sources": rag_result.get('data_collection', {}).get('sources_used', [])
            },
            "selected_agents": selected_agents,
            "external_search": {
                "needed": external_search_needed,
                "reasoning": external_reasoning,
                "confidence": 0.8 if external_search_needed else 0.2
            },
            "routing_strategy": self._determine_routing_strategy(selected_agents, external_search_needed),
            "execution_plan": self._create_execution_plan(selected_agents, external_search_needed),
            "expected_outcome": self._predict_outcome(selected_agents, external_search_needed, analysis)
        }

    def _determine_routing_strategy(self, selected_agents: List[Dict[str, Any]], external_search_needed: bool) -> str:
        """Determine the routing strategy based on selected agents and external search."""
        agent_count = len(selected_agents)
        
        if external_search_needed and agent_count > 2:
            return "parallel_with_external"  # Run agents and external search in parallel
        elif external_search_needed and agent_count <= 2:
            return "sequential_with_external"  # Run agents first, then external search
        elif agent_count > 2:
            return "parallel_internal"  # Run multiple agents in parallel
        else:
            return "sequential_internal"  # Run agents sequentially

    def _create_execution_plan(self, selected_agents: List[Dict[str, Any]], external_search_needed: bool) -> Dict[str, Any]:
        """Create detailed execution plan."""
        plan = {
            "phase_1": {
                "name": "Internal Agent Execution",
                "agents": [agent['agent_name'] for agent in selected_agents],
                "execution_mode": "parallel" if len(selected_agents) > 1 else "sequential"
            }
        }
        
        if external_search_needed:
            plan["phase_2"] = {
                "name": "External Search Execution",
                "type": "perplexity_api",
                "execution_mode": "parallel"  # Can run parallel with phase 1
            }
        
        plan["phase_3"] = {
            "name": "Result Synthesis",
            "description": "Combine all results into coherent response"
        }
        
        return plan

    def _predict_outcome(self, selected_agents: List[Dict[str, Any]], external_search_needed: bool, 
                        analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Predict the expected outcome of the routing plan."""
        total_confidence = sum(agent['confidence'] for agent in selected_agents) / len(selected_agents) if selected_agents else 0
        
        return {
            "expected_quality": "high" if total_confidence > 0.7 else "medium" if total_confidence > 0.4 else "low",
            "completeness": "comprehensive" if external_search_needed and len(selected_agents) > 1 else "focused",
            "response_time": "fast" if len(selected_agents) <= 2 and not external_search_needed else "moderate",
            "confidence": total_confidence,
            "coverage_areas": [agent['agent_name'] for agent in selected_agents]
        }

    def _update_routing_history(self, query: str, routing_plan: Dict[str, Any]) -> None:
        """Update routing history for analysis and optimization."""
        self.routing_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "selected_agents": [agent['agent_name'] for agent in routing_plan.get('selected_agents', [])],
            "external_search_needed": routing_plan.get('external_search', {}).get('needed', False),
            "routing_strategy": routing_plan.get('routing_strategy', 'unknown'),
            "expected_quality": routing_plan.get('expected_outcome', {}).get('expected_quality', 'unknown')
        })

    def get_routing_history(self) -> List[Dict[str, Any]]:
        """Get routing history."""
        return self.routing_history.copy()

    def get_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get agent capabilities matrix."""
        return self.agent_capabilities.copy()

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics for analysis."""
        if not self.routing_history:
            return {"error": "No routing history available"}
        
        total_queries = len(self.routing_history)
        agent_usage = {}
        external_search_usage = 0
        strategy_usage = {}
        
        for entry in self.routing_history:
            # Count agent usage
            for agent in entry.get('selected_agents', []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
            
            # Count external search usage
            if entry.get('external_search_needed', False):
                external_search_usage += 1
            
            # Count strategy usage
            strategy = entry.get('routing_strategy', 'unknown')
            strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
        
        return {
            "total_queries": total_queries,
            "agent_usage": agent_usage,
            "external_search_usage": external_search_usage,
            "external_search_percentage": (external_search_usage / total_queries) * 100,
            "strategy_usage": strategy_usage,
            "most_used_agent": max(agent_usage.keys(), key=lambda k: agent_usage[k]) if agent_usage else "none",
            "most_used_strategy": max(strategy_usage.keys(), key=lambda k: strategy_usage[k]) if strategy_usage else "none"
        }
