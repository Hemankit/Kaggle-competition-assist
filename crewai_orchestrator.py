"""
CrewAI Orchestrator - Mode 1
Crew-based collaboration with external search integration.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio
from datetime import datetime

# Import CrewAI
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

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

class CrewAIOrchestrator:
    """
    CrewAI-based multi-agent orchestrator with external search integration.
    Uses crew-based collaboration for coordinated agent interactions.
    """

    def __init__(self, perplexity_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        self.external_search_agent = ExternalSearchAgent(perplexity_api_key, google_api_key)
        self.rag_adapter = RAGAdapter(google_api_key)
        self.agents = self._initialize_agents()
        self.crews = self._initialize_crews()
        self.execution_history = []

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

    def _initialize_crews(self) -> Dict[str, Crew]:
        """Initialize CrewAI crews for different collaboration patterns."""
        if not CREWAI_AVAILABLE:
            logger.warning("CrewAI not available - using mock crews")
            return {}
        
        try:
            # Create specialized crews
            crews = {}
            
            # 1. Data Analysis Crew
            data_crew = self._create_data_analysis_crew()
            if data_crew:
                crews['data_analysis'] = data_crew
            
            # 2. Code Review Crew
            code_crew = self._create_code_review_crew()
            if code_crew:
                crews['code_review'] = code_crew
            
            # 3. Strategy Planning Crew
            strategy_crew = self._create_strategy_planning_crew()
            if strategy_crew:
                crews['strategy_planning'] = strategy_crew
            
            # 4. Community Engagement Crew
            community_crew = self._create_community_engagement_crew()
            if community_crew:
                crews['community_engagement'] = community_crew
            
            logger.info(f"✅ Initialized {len(crews)} CrewAI crews")
            return crews
            
        except Exception as e:
            logger.error(f"Error initializing crews: {e}")
            return {}

    def _create_data_analysis_crew(self) -> Optional[Crew]:
        """Create crew for data analysis tasks."""
        try:
            # Data Analyst Agent
            data_analyst = Agent(
                role="Data Analyst",
                goal="Analyze competition data and provide insights",
                backstory="Expert in data analysis with deep knowledge of Kaggle competitions",
                tools=[],  # Will add tools later
                verbose=True
            )
            
            # Competition Summary Agent
            competition_expert = Agent(
                role="Competition Expert",
                goal="Provide comprehensive competition overview",
                backstory="Specialist in understanding competition requirements and evaluation metrics",
                tools=[],
                verbose=True
            )
            
            # Data Analysis Task
            data_task = Task(
                description="Analyze the competition data and provide comprehensive insights",
                agent=data_analyst,
                expected_output="Detailed data analysis with actionable insights"
            )
            
            # Competition Overview Task
            overview_task = Task(
                description="Provide competition overview and context",
                agent=competition_expert,
                expected_output="Clear competition summary with key requirements"
            )
            
            return Crew(
                agents=[data_analyst, competition_expert],
                tasks=[data_task, overview_task],
                process=Process.sequential,
                verbose=True
            )
            
        except Exception as e:
            logger.error(f"Error creating data analysis crew: {e}")
            return None

    def _create_code_review_crew(self) -> Optional[Crew]:
        """Create crew for code review tasks."""
        try:
            # Code Reviewer Agent
            code_reviewer = Agent(
                role="Code Reviewer",
                goal="Review and improve code quality",
                backstory="Expert in code review with focus on best practices and optimization",
                tools=[],
                verbose=True
            )
            
            # Error Diagnosis Agent
            error_expert = Agent(
                role="Error Diagnosis Expert",
                goal="Identify and fix code errors",
                backstory="Specialist in debugging and error resolution",
                tools=[],
                verbose=True
            )
            
            # Code Review Task
            review_task = Task(
                description="Review the provided code and suggest improvements",
                agent=code_reviewer,
                expected_output="Comprehensive code review with specific recommendations"
            )
            
            # Error Diagnosis Task
            error_task = Task(
                description="Diagnose any errors in the code and provide solutions",
                agent=error_expert,
                expected_output="Clear error diagnosis with step-by-step solutions"
            )
            
            return Crew(
                agents=[code_reviewer, error_expert],
                tasks=[review_task, error_task],
                process=Process.sequential,
                verbose=True
            )
            
        except Exception as e:
            logger.error(f"Error creating code review crew: {e}")
            return None

    def _create_strategy_planning_crew(self) -> Optional[Crew]:
        """Create crew for strategy planning tasks."""
        try:
            # Strategy Planner Agent
            strategy_planner = Agent(
                role="Strategy Planner",
                goal="Develop winning strategies for competitions",
                backstory="Expert in competition strategy with track record of success",
                tools=[],
                verbose=True
            )
            
            # Progress Monitor Agent
            progress_monitor = Agent(
                role="Progress Monitor",
                goal="Track and optimize competition progress",
                backstory="Specialist in progress tracking and optimization",
                tools=[],
                verbose=True
            )
            
            # Strategy Planning Task
            strategy_task = Task(
                description="Develop a comprehensive strategy for the competition",
                agent=strategy_planner,
                expected_output="Detailed strategy with actionable steps"
            )
            
            # Progress Monitoring Task
            progress_task = Task(
                description="Monitor progress and suggest optimizations",
                agent=progress_monitor,
                expected_output="Progress analysis with optimization recommendations"
            )
            
            return Crew(
                agents=[strategy_planner, progress_monitor],
                tasks=[strategy_task, progress_task],
                process=Process.sequential,
                verbose=True
            )
            
        except Exception as e:
            logger.error(f"Error creating strategy planning crew: {e}")
            return None

    def _create_community_engagement_crew(self) -> Optional[Crew]:
        """Create crew for community engagement tasks."""
        try:
            # Community Engagement Agent
            community_agent = Agent(
                role="Community Engagement Specialist",
                goal="Facilitate community interactions and knowledge sharing",
                backstory="Expert in community engagement with deep understanding of Kaggle culture",
                tools=[],
                verbose=True
            )
            
            # Discussion Helper Agent
            discussion_helper = Agent(
                role="Discussion Helper",
                goal="Help with discussion analysis and insights",
                backstory="Specialist in analyzing discussions and extracting valuable insights",
                tools=[],
                verbose=True
            )
            
            # Community Engagement Task
            community_task = Task(
                description="Engage with the community and share insights",
                agent=community_agent,
                expected_output="Community engagement strategy and insights"
            )
            
            # Discussion Analysis Task
            discussion_task = Task(
                description="Analyze discussions and provide insights",
                agent=discussion_helper,
                expected_output="Discussion analysis with key insights"
            )
            
            return Crew(
                agents=[community_agent, discussion_helper],
                tasks=[community_task, discussion_task],
                process=Process.sequential,
                verbose=True
            )
            
        except Exception as e:
            logger.error(f"Error creating community engagement crew: {e}")
            return None

    def run(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for CrewAI orchestration.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Complete orchestration result
        """
        if context is None:
            context = {}
            
        logger.info(f"CrewAI Orchestrator: Processing query '{query}'")
        
        try:
            # Step 1: Analyze query and determine approach
            analysis_result = self._analyze_query(query, context)
            
            # Step 2: Get data from RAG adapter
            rag_result = self.rag_adapter.process_query(query, context)
            
            # Step 3: Determine if external search is needed
            external_search_needed, reasoning, confidence = self.external_search_agent.should_use_external_search(
                query, rag_result.get('rag_retrieval', {}), context
            )
            
            # Step 4: Execute appropriate crew
            crew_result = self._execute_crew(analysis_result, query, context, rag_result)
            
            # Step 5: Get external search results if needed
            external_result = None
            if external_search_needed:
                external_result = self.external_search_agent.search_external(query, context)
            
            # Step 6: Synthesize results
            final_result = self._synthesize_results(
                query, context, rag_result, crew_result, external_result, analysis_result
            )
            
            # Step 7: Update execution history
            self._update_execution_history(query, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in CrewAI orchestration: {e}")
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

    def _analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to determine which crew and agents to use."""
        query_lower = query.lower()
        
        # Determine crew type based on query
        if any(keyword in query_lower for keyword in ['data', 'analysis', 'dataset', 'features', 'columns']):
            crew_type = 'data_analysis'
        elif any(keyword in query_lower for keyword in ['code', 'error', 'bug', 'debug', 'review']):
            crew_type = 'code_review'
        elif any(keyword in query_lower for keyword in ['strategy', 'plan', 'approach', 'method']):
            crew_type = 'strategy_planning'
        elif any(keyword in query_lower for keyword in ['discussion', 'community', 'forum', 'post']):
            crew_type = 'community_engagement'
        else:
            crew_type = 'data_analysis'  # Default
        
        return {
            "crew_type": crew_type,
            "query_type": self._classify_query_type(query),
            "complexity": self._assess_complexity(query),
            "requires_external_search": self._needs_external_search(query)
        }

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

    def _execute_crew(self, analysis: Dict[str, Any], query: str, context: Dict[str, Any], rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate crew."""
        crew_type = analysis.get('crew_type', 'data_analysis')
        
        if crew_type not in self.crews:
            return {
                "success": False,
                "error": f"Crew type '{crew_type}' not available",
                "crew_type": crew_type
            }
        
        try:
            crew = self.crews[crew_type]
            
            # Prepare inputs for crew
            crew_inputs = {
                "query": query,
                "context": context,
                "rag_data": rag_result.get('rag_retrieval', {}),
                "analysis": analysis
            }
            
            # Execute crew
            result = crew.kickoff(inputs=crew_inputs)
            
            return {
                "success": True,
                "crew_type": crew_type,
                "result": result,
                "agents_used": [agent.role for agent in crew.agents],
                "tasks_completed": [task.description for task in crew.tasks]
            }
            
        except Exception as e:
            logger.error(f"Error executing crew '{crew_type}': {e}")
            return {
                "success": False,
                "error": str(e),
                "crew_type": crew_type
            }

    def _synthesize_results(self, query: str, context: Dict[str, Any], rag_result: Dict[str, Any], 
                          crew_result: Dict[str, Any], external_result: Optional[Dict[str, Any]], 
                          analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all results into a coherent response."""
        
        # Base result
        result = {
            "query": query,
            "context": context,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "orchestrator": "CrewAI",
            "analysis": analysis
        }
        
        # Add RAG results
        result["rag_retrieval"] = {
            "success": rag_result.get('rag_retrieval', {}).get('success', False),
            "retrieved_count": rag_result.get('rag_retrieval', {}).get('retrieved_count', 0),
            "sources": rag_result.get('data_collection', {}).get('sources_used', [])
        }
        
        # Add crew results
        result["crew_execution"] = {
            "success": crew_result.get('success', False),
            "crew_type": crew_result.get('crew_type', 'unknown'),
            "agents_used": crew_result.get('agents_used', []),
            "tasks_completed": crew_result.get('tasks_completed', [])
        }
        
        # Add external search results
        if external_result:
            result["external_search"] = {
                "success": external_result.get('success', False),
                "results_count": len(external_result.get('results', [])),
                "search_time": external_result.get('search_time', 0),
                "source": external_result.get('source', 'perplexity_api')
            }
        else:
            result["external_search"] = {
                "success": False,
                "reason": "Not needed or not available"
            }
        
        # Create synthesized response
        result["synthesized_response"] = self._create_synthesized_response(
            query, rag_result, crew_result, external_result
        )
        
        return result

    def _create_synthesized_response(self, query: str, rag_result: Dict[str, Any], 
                                   crew_result: Dict[str, Any], external_result: Optional[Dict[str, Any]]) -> str:
        """Create a synthesized response from all sources."""
        
        response_parts = []
        
        # Add crew response
        if crew_result.get('success') and crew_result.get('result'):
            response_parts.append(f"**Crew Analysis:**\n{crew_result['result']}")
        
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
            return "I've analyzed your query using our multi-agent system. While I couldn't find specific information, I'm ready to help with any follow-up questions."

    def _update_execution_history(self, query: str, result: Dict[str, Any]) -> None:
        """Update execution history for debugging and optimization."""
        self.execution_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "success": result.get('success', False),
            "crew_type": result.get('crew_execution', {}).get('crew_type', 'unknown'),
            "agents_used": result.get('crew_execution', {}).get('agents_used', []),
            "external_search_used": result.get('external_search', {}).get('success', False)
        })

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history.copy()

    def get_available_crews(self) -> List[str]:
        """Get list of available crews."""
        return list(self.crews.keys())

    def get_crew_info(self, crew_type: str) -> Dict[str, Any]:
        """Get information about a specific crew."""
        if crew_type not in self.crews:
            return {"error": f"Crew '{crew_type}' not found"}
        
        crew = self.crews[crew_type]
        return {
            "crew_type": crew_type,
            "agents": [agent.role for agent in crew.agents],
            "tasks": [task.description for task in crew.tasks],
            "process": crew.process.value if hasattr(crew.process, 'value') else str(crew.process)
        }
