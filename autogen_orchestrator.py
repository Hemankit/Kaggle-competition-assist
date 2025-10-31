"""
AutoGen Orchestrator - Mode 2
Conversational multi-agent with external search integration.
"""

import sys
import os
sys.path.append('.')

from typing import Dict, Any, List, Optional, Tuple
import logging
import asyncio
from datetime import datetime

# Import AutoGen
try:
    import autogen
    from autogen import ConversableAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

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

class AutoGenOrchestrator:
    """
    AutoGen-based multi-agent orchestrator with external search integration.
    Uses conversational agents for back-and-forth reasoning and collaboration.
    """

    def __init__(self, perplexity_api_key: Optional[str] = None, google_api_key: Optional[str] = None):
        self.external_search_agent = ExternalSearchAgent(perplexity_api_key, google_api_key)
        self.rag_adapter = RAGAdapter(google_api_key)
        self.agents = self._initialize_agents()
        self.conversation_groups = self._initialize_conversation_groups()
        self.conversation_history = []

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

    def _initialize_conversation_groups(self) -> Dict[str, GroupChat]:
        """Initialize AutoGen conversation groups for different scenarios."""
        if not AUTOGEN_AVAILABLE:
            logger.warning("AutoGen not available - using mock conversation groups")
            return {}
        
        try:
            groups = {}
            
            # 1. Data Analysis Group
            data_group = self._create_data_analysis_group()
            if data_group:
                groups['data_analysis'] = data_group
            
            # 2. Code Review Group
            code_group = self._create_code_review_group()
            if code_group:
                groups['code_review'] = code_group
            
            # 3. Strategy Planning Group
            strategy_group = self._create_strategy_planning_group()
            if strategy_group:
                groups['strategy_planning'] = strategy_group
            
            # 4. Community Engagement Group
            community_group = self._create_community_engagement_group()
            if community_group:
                groups['community_engagement'] = community_group
            
            logger.info(f"✅ Initialized {len(groups)} AutoGen conversation groups")
            return groups
            
        except Exception as e:
            logger.error(f"Error initializing conversation groups: {e}")
            return {}

    def _create_data_analysis_group(self) -> Optional[GroupChat]:
        """Create conversation group for data analysis tasks."""
        try:
            # Data Analyst Agent
            data_analyst = ConversableAgent(
                name="DataAnalyst",
                system_message="""You are a data analysis expert specializing in Kaggle competitions. 
                Your role is to analyze datasets, identify patterns, and provide insights.
                You work collaboratively with other agents to provide comprehensive analysis.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Competition Expert Agent
            competition_expert = ConversableAgent(
                name="CompetitionExpert",
                system_message="""You are a competition expert with deep knowledge of Kaggle competitions.
                Your role is to provide context about competition requirements, evaluation metrics, and best practices.
                You help other agents understand the competition framework.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Data Visualization Agent
            viz_agent = ConversableAgent(
                name="VisualizationExpert",
                system_message="""You are a data visualization expert.
                Your role is to suggest appropriate visualizations and help interpret data patterns.
                You work with data analysts to create meaningful visual representations.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Create group chat
            group_chat = GroupChat(
                agents=[data_analyst, competition_expert, viz_agent],
                messages=[],
                max_round=10,
                speaker_selection_method="auto"
            )
            
            return group_chat
            
        except Exception as e:
            logger.error(f"Error creating data analysis group: {e}")
            return None

    def _create_code_review_group(self) -> Optional[GroupChat]:
        """Create conversation group for code review tasks."""
        try:
            # Code Reviewer Agent
            code_reviewer = ConversableAgent(
                name="CodeReviewer",
                system_message="""You are a code review expert specializing in data science and machine learning code.
                Your role is to review code quality, identify issues, and suggest improvements.
                You focus on best practices, performance, and maintainability.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Error Diagnosis Agent
            error_expert = ConversableAgent(
                name="ErrorDiagnostician",
                system_message="""You are an error diagnosis expert.
                Your role is to identify bugs, analyze error messages, and provide solutions.
                You work with code reviewers to resolve technical issues.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Performance Optimizer Agent
            optimizer = ConversableAgent(
                name="PerformanceOptimizer",
                system_message="""You are a performance optimization expert.
                Your role is to suggest code optimizations, improve efficiency, and enhance performance.
                You work with other agents to create high-quality, efficient code.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Create group chat
            group_chat = GroupChat(
                agents=[code_reviewer, error_expert, optimizer],
                messages=[],
                max_round=8,
                speaker_selection_method="auto"
            )
            
            return group_chat
            
        except Exception as e:
            logger.error(f"Error creating code review group: {e}")
            return None

    def _create_strategy_planning_group(self) -> Optional[GroupChat]:
        """Create conversation group for strategy planning tasks."""
        try:
            # Strategy Planner Agent
            strategy_planner = ConversableAgent(
                name="StrategyPlanner",
                system_message="""You are a strategy planning expert for Kaggle competitions.
                Your role is to develop winning strategies, analyze approaches, and plan execution.
                You consider multiple factors including data, techniques, and competition dynamics.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Progress Monitor Agent
            progress_monitor = ConversableAgent(
                name="ProgressMonitor",
                system_message="""You are a progress monitoring expert.
                Your role is to track progress, identify bottlenecks, and suggest optimizations.
                You help ensure strategies are executed effectively and efficiently.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Risk Assessor Agent
            risk_assessor = ConversableAgent(
                name="RiskAssessor",
                system_message="""You are a risk assessment expert.
                Your role is to identify potential risks, evaluate trade-offs, and suggest mitigations.
                You help ensure strategies are robust and well-balanced.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Create group chat
            group_chat = GroupChat(
                agents=[strategy_planner, progress_monitor, risk_assessor],
                messages=[],
                max_round=12,
                speaker_selection_method="auto"
            )
            
            return group_chat
            
        except Exception as e:
            logger.error(f"Error creating strategy planning group: {e}")
            return None

    def _create_community_engagement_group(self) -> Optional[GroupChat]:
        """Create conversation group for community engagement tasks."""
        try:
            # Community Engagement Agent
            community_agent = ConversableAgent(
                name="CommunityEngagement",
                system_message="""You are a community engagement specialist for Kaggle.
                Your role is to facilitate community interactions, share insights, and build relationships.
                You understand Kaggle culture and help create valuable community contributions.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Discussion Helper Agent
            discussion_helper = ConversableAgent(
                name="DiscussionHelper",
                system_message="""You are a discussion analysis expert.
                Your role is to analyze discussions, extract insights, and provide helpful responses.
                You help community members by understanding their questions and providing relevant information.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Knowledge Synthesizer Agent
            knowledge_synthesizer = ConversableAgent(
                name="KnowledgeSynthesizer",
                system_message="""You are a knowledge synthesis expert.
                Your role is to combine information from multiple sources and create comprehensive insights.
                You help distill complex information into clear, actionable knowledge.""",
                llm_config=self._get_llm_config(),
                human_input_mode="NEVER"
            )
            
            # Create group chat
            group_chat = GroupChat(
                agents=[community_agent, discussion_helper, knowledge_synthesizer],
                messages=[],
                max_round=10,
                speaker_selection_method="auto"
            )
            
            return group_chat
            
        except Exception as e:
            logger.error(f"Error creating community engagement group: {e}")
            return None

    def _get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for AutoGen agents."""
        # This would be configured based on your LLM setup
        return {
            "model": "gpt-3.5-turbo",  # Placeholder - would use actual LLM
            "temperature": 0.1,
            "max_tokens": 1000
        }

    def run(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for AutoGen orchestration.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Complete orchestration result
        """
        if context is None:
            context = {}
            
        logger.info(f"AutoGen Orchestrator: Processing query '{query}'")
        
        try:
            # Step 1: Analyze query and determine approach
            analysis_result = self._analyze_query(query, context)
            
            # Step 2: Get data from RAG adapter
            rag_result = self.rag_adapter.process_query(query, context)
            
            # Step 3: Determine if external search is needed
            external_search_needed, reasoning, confidence = self.external_search_agent.should_use_external_search(
                query, rag_result.get('rag_retrieval', {}), context
            )
            
            # Step 4: Execute appropriate conversation group
            conversation_result = self._execute_conversation_group(analysis_result, query, context, rag_result)
            
            # Step 5: Get external search results if needed
            external_result = None
            if external_search_needed:
                external_result = self.external_search_agent.search_external(query, context)
            
            # Step 6: Synthesize results
            final_result = self._synthesize_results(
                query, context, rag_result, conversation_result, external_result, analysis_result
            )
            
            # Step 7: Update conversation history
            self._update_conversation_history(query, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in AutoGen orchestration: {e}")
            return {
                "query": query,
                "context": context,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

    def _analyze_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to determine which conversation group to use."""
        query_lower = query.lower()
        
        # Determine group type based on query
        if any(keyword in query_lower for keyword in ['data', 'analysis', 'dataset', 'features', 'columns']):
            group_type = 'data_analysis'
        elif any(keyword in query_lower for keyword in ['code', 'error', 'bug', 'debug', 'review']):
            group_type = 'code_review'
        elif any(keyword in query_lower for keyword in ['strategy', 'plan', 'approach', 'method']):
            group_type = 'strategy_planning'
        elif any(keyword in query_lower for keyword in ['discussion', 'community', 'forum', 'post']):
            group_type = 'community_engagement'
        else:
            group_type = 'data_analysis'  # Default
        
        return {
            "group_type": group_type,
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

    def _execute_conversation_group(self, analysis: Dict[str, Any], query: str, context: Dict[str, Any], rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate conversation group."""
        group_type = analysis.get('group_type', 'data_analysis')
        
        if group_type not in self.conversation_groups:
            return {
                "success": False,
                "error": f"Conversation group type '{group_type}' not available",
                "group_type": group_type
            }
        
        try:
            group_chat = self.conversation_groups[group_type]
            
            # Create group chat manager
            manager = GroupChatManager(
                groupchat=group_chat,
                llm_config=self._get_llm_config()
            )
            
            # Prepare conversation context
            conversation_context = f"""
            Query: {query}
            Context: {context}
            RAG Data: {rag_result.get('rag_retrieval', {})}
            Analysis: {analysis}
            
            Please collaborate to provide a comprehensive response to the user's query.
            """
            
            # Execute conversation
            result = manager.initiate_chat(
                message=conversation_context,
                recipient=group_chat.agents[0]  # Start with first agent
            )
            
            return {
                "success": True,
                "group_type": group_type,
                "conversation_result": result,
                "agents_participated": [agent.name for agent in group_chat.agents],
                "messages_exchanged": len(group_chat.messages)
            }
            
        except Exception as e:
            logger.error(f"Error executing conversation group '{group_type}': {e}")
            return {
                "success": False,
                "error": str(e),
                "group_type": group_type
            }

    def _synthesize_results(self, query: str, context: Dict[str, Any], rag_result: Dict[str, Any], 
                          conversation_result: Dict[str, Any], external_result: Optional[Dict[str, Any]], 
                          analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all results into a coherent response."""
        
        # Base result
        result = {
            "query": query,
            "context": context,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "orchestrator": "AutoGen",
            "analysis": analysis
        }
        
        # Add RAG results
        result["rag_retrieval"] = {
            "success": rag_result.get('rag_retrieval', {}).get('success', False),
            "retrieved_count": rag_result.get('rag_retrieval', {}).get('retrieved_count', 0),
            "sources": rag_result.get('data_collection', {}).get('sources_used', [])
        }
        
        # Add conversation results
        result["conversation_execution"] = {
            "success": conversation_result.get('success', False),
            "group_type": conversation_result.get('group_type', 'unknown'),
            "agents_participated": conversation_result.get('agents_participated', []),
            "messages_exchanged": conversation_result.get('messages_exchanged', 0)
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
            query, rag_result, conversation_result, external_result
        )
        
        return result

    def _create_synthesized_response(self, query: str, rag_result: Dict[str, Any], 
                                   conversation_result: Dict[str, Any], external_result: Optional[Dict[str, Any]]) -> str:
        """Create a synthesized response from all sources."""
        
        response_parts = []
        
        # Add conversation response
        if conversation_result.get('success') and conversation_result.get('conversation_result'):
            response_parts.append(f"**Multi-Agent Analysis:**\n{conversation_result['conversation_result']}")
        
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
            return "I've analyzed your query using our conversational multi-agent system. While I couldn't find specific information, I'm ready to help with any follow-up questions."

    def _update_conversation_history(self, query: str, result: Dict[str, Any]) -> None:
        """Update conversation history for debugging and optimization."""
        self.conversation_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "success": result.get('success', False),
            "group_type": result.get('conversation_execution', {}).get('group_type', 'unknown'),
            "agents_participated": result.get('conversation_execution', {}).get('agents_participated', []),
            "external_search_used": result.get('external_search', {}).get('success', False)
        })

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def get_available_groups(self) -> List[str]:
        """Get list of available conversation groups."""
        return list(self.conversation_groups.keys())

    def get_group_info(self, group_type: str) -> Dict[str, Any]:
        """Get information about a specific conversation group."""
        if group_type not in self.conversation_groups:
            return {"error": f"Conversation group '{group_type}' not found"}
        
        group_chat = self.conversation_groups[group_type]
        return {
            "group_type": group_type,
            "agents": [agent.name for agent in group_chat.agents],
            "max_rounds": group_chat.max_round,
            "speaker_selection": group_chat.speaker_selection_method
        }
