"""
IdeaInitiatorAgent - Competition-specific idea generator.

This agent generates tailored starter ideas for Kaggle competitions by:
1. Analyzing competition data characteristics
2. Understanding evaluation metrics
3. Studying top notebook approaches
4. Suggesting 3-5 validated ideas with expected scores
"""

from .base_agent import BaseAgent
from typing import Optional, Dict, Any, List

# CrewAI
from crewai import Agent as CrewAgent

# AutoGen
from autogen import ConversableAgent

# LLM support
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from llms.llm_loader import get_llm_from_config


IDEA_GENERATION_PROMPT = """
You are a Kaggle competition strategist specializing in generating competition-specific starter ideas.

Competition Context:
-------------------
{competition_context}

Your task: Generate 3-5 tailored starter ideas for this competition.

For EACH idea, provide:
1. **Name**: Short, descriptive name (e.g., "Quick XGBoost Baseline")
2. **Approach**: Specific technical approach (algorithms, features, techniques)
3. **Expected Score**: Realistic score estimate based on leaderboard data
4. **Effort**: Low/Medium/High time investment
5. **Rationale**: Why this approach fits THIS competition (cite data/metric/top approaches)

Requirements:
- Ideas must be competition-specific (NOT generic suggestions)
- Reference actual data characteristics, evaluation metric, and top approaches
- Progress from simple baseline → intermediate → advanced
- Include expected scores based on leaderboard benchmarks
- Be concrete and actionable

Format your response as a numbered list with clear sections for each idea.
"""


class IdeaInitiatorAgent(BaseAgent):
    """
    Competition-specific idea generator.
    
    Differentiator vs ChatGPT:
    - Uses actual competition data, not generic advice
    - Suggests validated approaches from top notebooks
    - Provides expected scores based on leaderboard
    - Tailored to evaluation metric and data characteristics
    """
    
    def __init__(self, llm=None):
        super().__init__(
            name="IdeaInitiatorAgent",
            description=(
                "Competition-specific idea generator that creates tailored starter approaches by analyzing "
                "data characteristics, evaluation metrics, and top notebook strategies. Provides expected "
                "scores and effort estimates for each idea, helping users choose the right starting point."
            )
        )
        self.llm = llm or get_llm_from_config(section="reasoning_and_interaction")
        self.prompt = PromptTemplate.from_template(IDEA_GENERATION_PROMPT)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def generate_ideas(
        self, 
        competition_slug: str,
        data_summary: str = "",
        evaluation_metric: str = "",
        top_approaches: List[str] = None,
        leaderboard_scores: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Generate competition-specific ideas.
        
        Args:
            competition_slug: Competition identifier
            data_summary: Summary of data files and characteristics
            evaluation_metric: How submissions are scored
            top_approaches: List of approaches from top notebooks
            leaderboard_scores: Dict of percentile → score mappings
        
        Returns:
            Dict with generated ideas and metadata
        """
        top_approaches = top_approaches or []
        leaderboard_scores = leaderboard_scores or {}
        
        # Build context
        competition_context = self._build_competition_context(
            competition_slug=competition_slug,
            data_summary=data_summary,
            evaluation_metric=evaluation_metric,
            top_approaches=top_approaches,
            leaderboard_scores=leaderboard_scores
        )
        
        # Generate ideas using LLM
        ideas_text = self.chain.run(competition_context=competition_context)
        
        return {
            "agent_name": self.name,
            "competition": competition_slug,
            "ideas": ideas_text,
            "context_used": {
                "data_available": bool(data_summary),
                "metric_available": bool(evaluation_metric),
                "approaches_count": len(top_approaches),
                "leaderboard_available": bool(leaderboard_scores)
            }
        }
    
    def _build_competition_context(
        self,
        competition_slug: str,
        data_summary: str,
        evaluation_metric: str,
        top_approaches: List[str],
        leaderboard_scores: Dict[str, float]
    ) -> str:
        """Build comprehensive context for idea generation."""
        
        context_parts = [f"**Competition**: {competition_slug}\n"]
        
        # Data section
        if data_summary:
            context_parts.append(f"**Data Characteristics**:\n{data_summary}\n")
        else:
            context_parts.append("**Data Characteristics**: Not yet analyzed\n")
        
        # Evaluation metric
        if evaluation_metric:
            context_parts.append(f"**Evaluation Metric**: {evaluation_metric}\n")
        else:
            context_parts.append("**Evaluation Metric**: Check competition page\n")
        
        # Top approaches
        if top_approaches:
            approaches_text = "\n".join([f"  - {approach}" for approach in top_approaches[:5]])
            context_parts.append(f"**Top Notebook Approaches**:\n{approaches_text}\n")
        else:
            context_parts.append("**Top Notebook Approaches**: Not yet analyzed\n")
        
        # Leaderboard benchmarks
        if leaderboard_scores:
            scores_text = "\n".join([
                f"  - {percentile}: {score}" 
                for percentile, score in sorted(leaderboard_scores.items())
            ])
            context_parts.append(f"**Leaderboard Benchmarks**:\n{scores_text}\n")
        else:
            context_parts.append("**Leaderboard Benchmarks**: Not yet available\n")
        
        return "\n".join(context_parts)
    
    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Standard run method for orchestrator compatibility.
        
        Args:
            query: User query (e.g., "Give me starter ideas for this competition")
            context: Dict with competition_slug and optional data/metric/approaches
        
        Returns:
            Dict with agent_name, response, and updated_context
        """
        context = context or {}
        competition_slug = context.get("competition_slug", "unknown-competition")
        
        # Extract context if available
        data_summary = context.get("data_summary", "")
        evaluation_metric = context.get("evaluation_metric", "")
        top_approaches = context.get("top_approaches", [])
        leaderboard_scores = context.get("leaderboard_scores", {})
        
        # Generate ideas
        result = self.generate_ideas(
            competition_slug=competition_slug,
            data_summary=data_summary,
            evaluation_metric=evaluation_metric,
            top_approaches=top_approaches,
            leaderboard_scores=leaderboard_scores
        )
        
        return {
            "agent_name": self.name,
            "response": result["ideas"],
            "updated_context": context
        }
    
    def to_crewai(self) -> CrewAgent:
        """Convert to CrewAI agent for task-based collaboration."""
        return CrewAgent(
            role="Competition Idea Strategist",
            goal=(
                "Generate 3-5 competition-specific starter ideas that are validated by top notebooks, "
                "tailored to the data and evaluation metric, and include realistic score expectations."
            ),
            backstory=(
                "You're a Kaggle competition strategist with deep knowledge of winning approaches across "
                "different competition types. You specialize in analyzing competition characteristics and "
                "suggesting validated starter ideas that balance quick wins with learning opportunities. "
                "You always ground your suggestions in actual competition data, not generic advice."
            ),
            llm=self.llm,  # Use Perplexity LLM
            allow_delegation=False,
            verbose=True,
            tools=[]
        )
    
    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        """Convert to AutoGen conversational agent."""
        # Use Perplexity for reasoning via llm_loader config
        config = llm_config or {"config_list": [{"model": "sonar", "temperature": 0.3}]}
        
        system_prompt = (
            "You are a Kaggle Competition Idea Strategist. Your role is to generate competition-specific "
            "starter ideas for users entering Kaggle competitions.\n\n"
            "Your process:\n"
            "1. Analyze the competition's data characteristics (file types, sizes, columns)\n"
            "2. Understand the evaluation metric (accuracy, F1, RMSE, etc.)\n"
            "3. Study top notebook approaches to identify winning patterns\n"
            "4. Generate 3-5 tailored ideas that progress from baseline → intermediate → advanced\n\n"
            "For each idea, provide:\n"
            "- **Name**: Clear, descriptive title\n"
            "- **Approach**: Specific algorithms, features, techniques\n"
            "- **Expected Score**: Realistic estimate based on leaderboard\n"
            "- **Effort**: Low/Medium/High time investment\n"
            "- **Rationale**: Why this fits THIS competition (cite data/metric/approaches)\n\n"
            "Key principles:\n"
            "- Be competition-specific, not generic\n"
            "- Reference actual data, metrics, and top approaches\n"
            "- Provide expected scores based on benchmarks\n"
            "- Balance quick wins with learning opportunities\n"
            "- Prioritize validated approaches over experimental ones"
        )
        
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=system_prompt,
            human_input_mode="NEVER"
        )


