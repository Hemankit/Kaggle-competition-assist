"""
Dynamic Orchestrator - Mode 4
Self-selecting framework that analyzes query and picks the best orchestration approach.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime

# Import our orchestrators
from crewai_orchestrator import CrewAIOrchestrator
from autogen_orchestrator import AutoGenOrchestrator
from langgraph_orchestrator import LangGraphOrchestrator

# Import our components
from external_search_agent import ExternalSearchAgent
from rag_adapter import RAGAdapter

logger = logging.getLogger(__name__)

class DynamicOrchestrator:
    """
    Dynamic orchestrator that self-selects the best framework based on query analysis.
    Analyzes query characteristics and automatically chooses CrewAI, AutoGen, or LangGraph.
    """

    def __init__(self, perplexity_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        self.external_search_agent = ExternalSearchAgent(perplexity_api_key, google_api_key)
        self.rag_adapter = RAGAdapter(google_api_key)
        
        # Initialize all orchestrators
        self.orchestrators = {
            'crewai': CrewAIOrchestrator(perplexity_api_key, google_api_key),
            'autogen': AutoGenOrchestrator(perplexity_api_key, google_api_key),
            'langgraph': LangGraphOrchestrator(perplexity_api_key, google_api_key)
        }
        
        self.selection_history = []
        self.performance_metrics = {
            'crewai': {'success_rate': 0.0, 'avg_response_time': 0.0, 'usage_count': 0},
            'autogen': {'success_rate': 0.0, 'avg_response_time': 0.0, 'usage_count': 0},
            'langgraph': {'success_rate': 0.0, 'avg_response_time': 0.0, 'usage_count': 0}
        }

    def run(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for dynamic orchestration.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Complete orchestration result with framework selection info
        """
        if context is None:
            context = {}
            
        logger.info(f"Dynamic Orchestrator: Processing query '{query}'")
        
        try:
            # Step 1: Analyze query to determine best framework
            analysis_result = self._analyze_query_for_framework_selection(query, context)
            selected_framework = analysis_result['selected_framework']
            selection_reasoning = analysis_result['reasoning']
            
            # Step 2: Execute with selected framework
            start_time = datetime.now()
            orchestrator = self.orchestrators[selected_framework]
            result = orchestrator.run(query, context)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Step 3: Add dynamic orchestration metadata
            result['dynamic_orchestration'] = {
                'selected_framework': selected_framework,
                'selection_reasoning': selection_reasoning,
                'available_frameworks': list(self.orchestrators.keys()),
                'execution_time': execution_time,
                'framework_confidence': analysis_result['confidence']
            }
            
            # Step 4: Update performance metrics
            self._update_performance_metrics(selected_framework, result['success'], execution_time)
            
            # Step 5: Update selection history
            self._update_selection_history(query, selected_framework, result, analysis_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in dynamic orchestration: {e}")
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "success": False,
                "dynamic_orchestration": {
                    "selected_framework": "none",
                    "error": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }

    def _analyze_query_for_framework_selection(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to determine the best framework to use."""
        
        # Analyze query characteristics
        query_analysis = self._analyze_query_characteristics(query, context)
        
        # Score each framework based on query characteristics
        framework_scores = self._score_frameworks(query_analysis)
        
        # Select best framework
        selected_framework = max(framework_scores, key=framework_scores.get)
        confidence = framework_scores[selected_framework] / sum(framework_scores.values())
        
        # Generate reasoning
        reasoning = self._generate_selection_reasoning(selected_framework, query_analysis, framework_scores)
        
        return {
            'selected_framework': selected_framework,
            'reasoning': reasoning,
            'confidence': confidence,
            'query_analysis': query_analysis,
            'framework_scores': framework_scores
        }

    def _analyze_query_characteristics(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to extract characteristics for framework selection."""
        query_lower = query.lower()
        
        # Query type analysis
        query_type = self._classify_query_type(query)
        
        # Complexity analysis
        complexity = self._assess_complexity(query)
        
        # Collaboration needs
        collaboration_needs = self._assess_collaboration_needs(query)
        
        # Workflow requirements
        workflow_requirements = self._assess_workflow_requirements(query)
        
        # External search needs
        external_search_needed = self._needs_external_search(query)
        
        # Agent coordination needs
        agent_coordination = self._assess_agent_coordination_needs(query)
        
        return {
            'query_type': query_type,
            'complexity': complexity,
            'collaboration_needs': collaboration_needs,
            'workflow_requirements': workflow_requirements,
            'external_search_needed': external_search_needed,
            'agent_coordination': agent_coordination,
            'query_length': len(query.split()),
            'has_technical_terms': self._has_technical_terms(query),
            'requires_reasoning': self._requires_reasoning(query)
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

    def _assess_collaboration_needs(self, query: str) -> str:
        """Assess how much agent collaboration is needed."""
        query_lower = query.lower()
        
        collaboration_keywords = [
            'multiple', 'several', 'different', 'various', 'compare', 'combine',
            'together', 'collaborate', 'team', 'group', 'all', 'both'
        ]
        
        if any(keyword in query_lower for keyword in collaboration_keywords):
            return 'high'
        elif len(query.split()) > 15:
            return 'medium'
        else:
            return 'low'

    def _assess_workflow_requirements(self, query: str) -> str:
        """Assess if query requires structured workflow."""
        query_lower = query.lower()
        
        workflow_keywords = [
            'step', 'process', 'workflow', 'pipeline', 'sequence', 'order',
            'first', 'then', 'next', 'finally', 'stage', 'phase'
        ]
        
        if any(keyword in query_lower for keyword in workflow_keywords):
            return 'high'
        elif 'how' in query_lower and len(query.split()) > 10:
            return 'medium'
        else:
            return 'low'

    def _needs_external_search(self, query: str) -> bool:
        """Determine if query needs external search."""
        external_keywords = ['latest', 'recent', 'current', 'news', 'trend', 'update', 'now']
        return any(keyword in query.lower() for keyword in external_keywords)

    def _assess_agent_coordination_needs(self, query: str) -> str:
        """Assess how much agent coordination is needed."""
        query_lower = query.lower()
        
        coordination_keywords = [
            'analyze', 'review', 'check', 'verify', 'validate', 'examine',
            'investigate', 'research', 'study', 'evaluate', 'assess'
        ]
        
        if any(keyword in query_lower for keyword in coordination_keywords):
            return 'high'
        elif len(query.split()) > 20:
            return 'medium'
        else:
            return 'low'

    def _has_technical_terms(self, query: str) -> bool:
        """Check if query contains technical terms."""
        technical_terms = [
            'model', 'algorithm', 'feature', 'dataset', 'training', 'validation',
            'accuracy', 'precision', 'recall', 'f1', 'auc', 'rmse', 'mae',
            'neural', 'network', 'deep', 'learning', 'machine', 'ai', 'ml'
        ]
        return any(term in query.lower() for term in technical_terms)

    def _requires_reasoning(self, query: str) -> bool:
        """Check if query requires complex reasoning."""
        reasoning_keywords = [
            'why', 'how', 'explain', 'analyze', 'compare', 'evaluate',
            'assess', 'determine', 'decide', 'choose', 'recommend'
        ]
        return any(keyword in query.lower() for keyword in reasoning_keywords)

    def _score_frameworks(self, query_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Score each framework based on query characteristics."""
        scores = {'crewai': 0.0, 'autogen': 0.0, 'langgraph': 0.0}
        
        # CrewAI scoring
        if query_analysis['collaboration_needs'] == 'high':
            scores['crewai'] += 3.0
        elif query_analysis['collaboration_needs'] == 'medium':
            scores['crewai'] += 2.0
        else:
            scores['crewai'] += 1.0
        
        if query_analysis['query_type'] in ['recommendation', 'analytical']:
            scores['crewai'] += 2.0
        
        if query_analysis['complexity'] == 'high':
            scores['crewai'] += 1.5
        
        # AutoGen scoring
        if query_analysis['agent_coordination'] == 'high':
            scores['autogen'] += 3.0
        elif query_analysis['agent_coordination'] == 'medium':
            scores['autogen'] += 2.0
        else:
            scores['autogen'] += 1.0
        
        if query_analysis['query_type'] in ['instructional', 'troubleshooting']:
            scores['autogen'] += 2.0
        
        if query_analysis['requires_reasoning']:
            scores['autogen'] += 1.5
        
        # LangGraph scoring
        if query_analysis['workflow_requirements'] == 'high':
            scores['langgraph'] += 3.0
        elif query_analysis['workflow_requirements'] == 'medium':
            scores['langgraph'] += 2.0
        else:
            scores['langgraph'] += 1.0
        
        if query_analysis['query_type'] in ['informational', 'comparative']:
            scores['langgraph'] += 2.0
        
        if query_analysis['has_technical_terms']:
            scores['langgraph'] += 1.5
        
        # Adjust based on performance metrics
        for framework in scores:
            if self.performance_metrics[framework]['usage_count'] > 0:
                success_rate = self.performance_metrics[framework]['success_rate']
                scores[framework] *= (0.5 + success_rate)  # Boost successful frameworks
        
        return scores

    def _generate_selection_reasoning(self, selected_framework: str, query_analysis: Dict[str, Any], 
                                    framework_scores: Dict[str, float]) -> str:
        """Generate human-readable reasoning for framework selection."""
        
        reasoning_parts = []
        
        # Primary reason
        if selected_framework == 'crewai':
            if query_analysis['collaboration_needs'] == 'high':
                reasoning_parts.append("High collaboration needs - CrewAI excels at coordinated agent teams")
            elif query_analysis['query_type'] in ['recommendation', 'analytical']:
                reasoning_parts.append("Analytical/recommendation query - CrewAI's structured approach is ideal")
        elif selected_framework == 'autogen':
            if query_analysis['agent_coordination'] == 'high':
                reasoning_parts.append("High agent coordination needs - AutoGen's conversational approach is perfect")
            elif query_analysis['query_type'] in ['instructional', 'troubleshooting']:
                reasoning_parts.append("Instructional/troubleshooting query - AutoGen's back-and-forth reasoning is ideal")
        elif selected_framework == 'langgraph':
            if query_analysis['workflow_requirements'] == 'high':
                reasoning_parts.append("High workflow requirements - LangGraph's structured workflow is optimal")
            elif query_analysis['query_type'] in ['informational', 'comparative']:
                reasoning_parts.append("Informational/comparative query - LangGraph's systematic approach is best")
        
        # Secondary factors
        if query_analysis['complexity'] == 'high':
            reasoning_parts.append(f"High complexity query - {selected_framework.title()} handles complex scenarios well")
        
        if query_analysis['has_technical_terms']:
            reasoning_parts.append(f"Technical query - {selected_framework.title()} is well-suited for technical analysis")
        
        # Performance consideration
        if self.performance_metrics[selected_framework]['usage_count'] > 0:
            success_rate = self.performance_metrics[selected_framework]['success_rate']
            if success_rate > 0.8:
                reasoning_parts.append(f"High success rate with {selected_framework.title()} ({success_rate:.1%})")
        
        return "; ".join(reasoning_parts) if reasoning_parts else f"Selected {selected_framework.title()} based on query characteristics"

    def _update_performance_metrics(self, framework: str, success: bool, execution_time: float) -> None:
        """Update performance metrics for framework selection."""
        metrics = self.performance_metrics[framework]
        
        # Update usage count
        metrics['usage_count'] += 1
        
        # Update success rate (exponential moving average)
        alpha = 0.1  # Smoothing factor
        current_success_rate = metrics['success_rate']
        new_success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_success_rate
        metrics['success_rate'] = new_success_rate
        
        # Update average response time (exponential moving average)
        current_avg_time = metrics['avg_response_time']
        new_avg_time = alpha * execution_time + (1 - alpha) * current_avg_time
        metrics['avg_response_time'] = new_avg_time

    def _update_selection_history(self, query: str, selected_framework: str, result: Dict[str, Any], 
                                analysis: Dict[str, Any]) -> None:
        """Update selection history for analysis and optimization."""
        self.selection_history.append({
            "query": query,
            "selected_framework": selected_framework,
            "success": result.get('success', False),
            "execution_time": result.get('dynamic_orchestration', {}).get('execution_time', 0),
            "confidence": analysis.get('confidence', 0),
            "query_analysis": analysis.get('query_analysis', {}),
            "timestamp": datetime.now().isoformat()
        })

    def get_selection_history(self) -> List[Dict[str, Any]]:
        """Get selection history."""
        return self.selection_history.copy()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all frameworks."""
        return self.performance_metrics.copy()

    def get_framework_recommendations(self, query: str) -> Dict[str, Any]:
        """Get framework recommendations for a query without executing."""
        analysis = self._analyze_query_characteristics(query, {})
        framework_scores = self._score_frameworks(analysis)
        
        # Sort frameworks by score
        sorted_frameworks = sorted(framework_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "query": query,
            "analysis": analysis,
            "framework_scores": framework_scores,
            "recommendations": [
                {
                    "framework": framework,
                    "score": score,
                    "confidence": score / sum(framework_scores.values())
                }
                for framework, score in sorted_frameworks
            ],
            "performance_metrics": self.performance_metrics
        }

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get status of all orchestrators."""
        return {
            "available_orchestrators": list(self.orchestrators.keys()),
            "performance_metrics": self.performance_metrics,
            "total_queries_processed": len(self.selection_history),
            "most_used_framework": max(self.performance_metrics.keys(), 
                                     key=lambda k: self.performance_metrics[k]['usage_count']),
            "best_performing_framework": max(self.performance_metrics.keys(), 
                                           key=lambda k: self.performance_metrics[k]['success_rate'])
        }
