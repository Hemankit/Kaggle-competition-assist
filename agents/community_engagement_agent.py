"""
Community Engagement Agent - Tracks user's Kaggle community interactions and incorporates feedback into strategy.

This agent:
1. Tracks which discussions/threads user has engaged with
2. Analyzes community responses and feedback
3. Extracts actionable insights from crowd wisdom
4. Updates strategy based on validated community suggestions
5. Prioritizes ideas based on community validation

Differentiator: Unlike generic LLMs, this agent maintains continuity of YOUR community interactions
and incorporates REAL feedback from domain experts into personalized guidance.
"""

from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# CrewAI
from crewai import Agent as CrewAgent

# AutoGen
from autogen import ConversableAgent

# LLM support
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from llms.llm_loader import get_llm_from_config


# Prompt for analyzing community feedback
feedback_analysis_prompt = """
You are a community engagement expert analyzing feedback from Kaggle discussions.

**User's Engagement Report:**
{engagement_report}

**User's Current Approach:**
{current_approach}

**User's Progress Status:**
{progress_status}

**Your Task:**
1. Extract actionable technical insights from community feedback
2. Identify code snippets, algorithms, or techniques suggested
3. Prioritize suggestions based on:
   - Community validation (upvotes, multiple mentions)
   - Implementation difficulty
   - Expected impact on score
4. Flag any conflicting advice
5. Generate concrete next steps

**Output Format:**
## Extracted Insights
- [List key technical insights]

## Prioritized Recommendations
1. [Highest priority] - Expected impact: X%, Effort: Y hours
2. [Medium priority] - Expected impact: X%, Effort: Y hours

## Implementation Steps
- [Specific actionable steps]

## Notes
- [Any conflicts or warnings]
"""


engagement_strategy_prompt = """
You are a strategic advisor synthesizing community engagement history.

**User's Engagement History (last 5 interactions):**
{engagement_history}

**Current Query:**
{query}

**Competition Context:**
{competition_context}

**Your Task:**
Based on the user's community interaction history:
1. Recommend which past feedback to implement next
2. Suggest new discussions to engage with
3. Identify patterns in community suggestions
4. Show what's completed vs. pending from past engagements

**Output Format:**
## From Your Community Interactions

✅ **Implemented:**
- [List completed items from past feedback]

⏳ **Pending:**
- [List high-priority items from past feedback not yet implemented]

🎯 **Recommended Next:**
1. [Action item with rationale]
2. [Action item with rationale]

💬 **Suggested Engagement:**
- [New discussions to participate in based on current focus]
"""


class CommunityEngagementAgent(BaseAgent):
    """
    Agent for tracking and analyzing user's Kaggle community engagement.
    
    Maintains continuity of community interactions and incorporates
    crowd-validated insights into personalized strategy.
    """
    
    def __init__(self, llm=None, chromadb_pipeline=None):
        super().__init__(
            name="CommunityEngagementAgent",
            description=(
                "Tracks user's Kaggle community interactions (discussions, comments, feedback received), "
                "analyzes community responses, extracts actionable insights, and updates strategy based on "
                "crowd-validated suggestions. Maintains continuity across engagements."
            )
        )
        self.llm = llm or get_llm_from_config(section="reasoning_and_interaction")
        self.chromadb_pipeline = chromadb_pipeline
        
        # Prompts
        self.feedback_prompt = PromptTemplate.from_template(feedback_analysis_prompt)
        self.strategy_prompt = PromptTemplate.from_template(engagement_strategy_prompt)
        
        # Chains
        self.feedback_chain = LLMChain(llm=self.llm, prompt=self.feedback_prompt)
        self.strategy_chain = LLMChain(llm=self.llm, prompt=self.strategy_prompt)
    
    
    def store_engagement(
        self, 
        user: str, 
        competition: str, 
        engagement_data: Dict[str, Any]
    ) -> str:
        """
        Store user's community engagement in ChromaDB.
        
        Args:
            user: Kaggle username
            competition: Competition slug
            engagement_data: Dict with:
                - discussion_title: Title of discussion engaged with
                - discussion_url: URL to discussion (optional)
                - user_action: What user did (comment, question, upvote)
                - community_responses: List of responses received
                - timestamp: When engagement occurred
        
        Returns:
            engagement_id: UUID for this engagement record
        """
        if not self.chromadb_pipeline:
            return None
        
        engagement_id = str(uuid.uuid4())
        timestamp = engagement_data.get('timestamp', datetime.now().isoformat())
        
        # Build document content
        content = f"""
Community Engagement: {engagement_data.get('discussion_title', 'Unknown Discussion')}

User Action: {engagement_data.get('user_action', 'engaged')}

Community Responses:
{self._format_responses(engagement_data.get('community_responses', []))}
"""
        
        # Store in ChromaDB with metadata
        self.chromadb_pipeline.indexer.index_documents(
            documents=[{
                'content': content,
                'metadata': {
                    'engagement_id': engagement_id,
                    'user': user,
                    'competition': competition,
                    'section': 'community_engagement',
                    'discussion_title': engagement_data.get('discussion_title', ''),
                    'discussion_url': engagement_data.get('discussion_url', ''),
                    'timestamp': timestamp,
                    'status': 'pending_analysis',
                    'engagement_type': engagement_data.get('engagement_type', 'comment')
                }
            }]
        )
        
        return engagement_id
    
    
    def retrieve_engagement_history(
        self, 
        user: str, 
        competition: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve user's past community engagements for a competition.
        
        Args:
            user: Kaggle username
            competition: Competition slug
            limit: Max number of engagements to retrieve
        
        Returns:
            List of engagement records (most recent first)
        """
        if not self.chromadb_pipeline:
            return []
        
        try:
            results = self.chromadb_pipeline.retriever.retrieve(
                query=f"community engagement for {user} in {competition}",
                top_k=limit,
                filters={
                    "section": "community_engagement",
                    "user": user,
                    "competition": competition
                }
            )
            
            return results
        except Exception as e:
            print(f"[ERROR] Failed to retrieve engagement history: {e}")
            return []
    
    
    def analyze_feedback(
        self, 
        engagement_report: str,
        current_approach: str = "",
        progress_status: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze community feedback and extract actionable insights.
        
        Args:
            engagement_report: User's description of community interaction
            current_approach: User's current modeling approach (optional)
            progress_status: User's progress/stagnation status (optional)
        
        Returns:
            Dict with:
                - insights: List of extracted insights
                - recommendations: Prioritized list of suggestions
                - implementation_steps: Concrete next steps
                - warnings: Any conflicting advice or red flags
        """
        try:
            analysis = self.feedback_chain.run(
                engagement_report=engagement_report,
                current_approach=current_approach or "Not specified",
                progress_status=progress_status or "Unknown"
            )
            
            return {
                "agent_name": self.name,
                "analysis": analysis,
                "status": "analyzed"
            }
        except Exception as e:
            print(f"[ERROR] Feedback analysis failed: {e}")
            return {
                "agent_name": self.name,
                "analysis": f"Analysis failed: {str(e)}",
                "status": "error"
            }
    
    
    def generate_engagement_strategy(
        self, 
        user: str,
        competition: str,
        query: str,
        competition_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate strategy recommendations based on engagement history.
        
        Args:
            user: Kaggle username
            competition: Competition slug
            query: User's current query
            competition_context: Dict with competition details
        
        Returns:
            Dict with strategic recommendations incorporating past feedback
        """
        # Retrieve engagement history
        history = self.retrieve_engagement_history(user, competition, limit=5)
        
        # Format history
        history_text = self._format_history(history)
        
        # Format competition context
        context_text = "\n".join(f"{k}: {v}" for k, v in competition_context.items())
        
        try:
            strategy = self.strategy_chain.run(
                engagement_history=history_text or "No prior engagements recorded",
                query=query,
                competition_context=context_text
            )
            
            return {
                "agent_name": self.name,
                "response": strategy,
                "engagement_count": len(history)
            }
        except Exception as e:
            print(f"[ERROR] Strategy generation failed: {e}")
            return {
                "agent_name": self.name,
                "response": f"Strategy generation failed: {str(e)}",
                "engagement_count": 0
            }
    
    
    def run(self, input_data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            input_data: User's query or engagement report
            context: Dict with user, competition, and other context
        
        Returns:
            Dict with agent response
        """
        mode = context.get('mode', 'analyze_feedback')
        
        if mode == 'analyze_feedback':
            # Analyze new community feedback
            return self.analyze_feedback(
                engagement_report=input_data,
                current_approach=context.get('current_approach', ''),
                progress_status=context.get('progress_status', '')
            )
        
        elif mode == 'generate_strategy':
            # Generate strategy based on engagement history
            return self.generate_engagement_strategy(
                user=context.get('user', 'Unknown'),
                competition=context.get('competition', 'Unknown'),
                query=input_data,
                competition_context=context.get('competition_context', {})
            )
        
        else:
            return {
                "agent_name": self.name,
                "response": f"Unknown mode: {mode}",
                "status": "error"
            }
    
    
    def to_crewai(self) -> CrewAgent:
        """Convert to CrewAI agent for multi-agent collaboration."""
        return CrewAgent(
            role="Community Engagement Strategist",
            goal=(
                "Track user's Kaggle community interactions, analyze feedback from domain experts, "
                "extract actionable insights, and update strategy based on crowd-validated suggestions. "
                "Maintain continuity across engagements to provide personalized, community-informed guidance."
            ),
            backstory=(
                "You're the bridge between the user and the Kaggle community. You remember every discussion "
                "they've participated in, every piece of advice they've received, and every suggestion that's "
                "been validated by multiple experts. Your job is to synthesize this crowd wisdom into concrete, "
                "prioritized action items that build on what the community has already validated."
            ),
            llm=self.llm,
            allow_delegation=True,
            verbose=True,
            tools=[]
        )
    
    
    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        """Convert to AutoGen agent for conversational multi-agent systems."""
        config = llm_config or {"config_list": [{"model": "sonar", "temperature": 0.3}]}
        
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=(
                "You are a community engagement strategist. Track and analyze user's interactions with "
                "the Kaggle community. When they report feedback from discussions, extract actionable insights, "
                "prioritize based on community validation, and generate concrete implementation steps. "
                "Maintain continuity by remembering past engagements and showing what's completed vs. pending. "
                "Your responses should be data-driven, referencing specific community members and validated approaches."
            ),
            human_input_mode="NEVER"
        )
    
    
    # Helper methods
    
    def _format_responses(self, responses: List[Dict[str, Any]]) -> str:
        """Format community responses for storage/display."""
        if not responses:
            return "No responses yet"
        
        formatted = []
        for r in responses:
            author = r.get('author', 'Unknown')
            response = r.get('response', '')
            formatted.append(f"- {author}: {response}")
        
        return "\n".join(formatted)
    
    
    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format engagement history for LLM consumption."""
        if not history:
            return "No prior engagements recorded"
        
        formatted = []
        for i, record in enumerate(history, 1):
            metadata = record.get('metadata', {})
            content = record.get('content', '')
            
            formatted.append(f"""
{i}. Discussion: {metadata.get('discussion_title', 'Unknown')}
   Date: {metadata.get('timestamp', 'Unknown')}
   Status: {metadata.get('status', 'pending')}
   
   {content[:300]}...
""")
        
        return "\n".join(formatted)



