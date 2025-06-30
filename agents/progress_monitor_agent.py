from agents.base_agent import BaseAgent
from typing import Dict, Any, Optional

# CrewAI
from crewai import CrewAgent

# AutoGen
from autogen import ConversableAgent

class ProgressMonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="progress_monitor_agent",
            description=(
                "Analyzes progress and leaderboard data, providing insights about score, rank, or "
                "user performance in a Kaggle competition context."
            )
        )

    def run(self, input_data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        summary_lines = []

        if "user_leaderboard_score" in context:
            summary_lines.append(f"Score: {context['user_leaderboard_score']}")
        if "user_leaderboard_rank" in context:
            summary_lines.append(f"Rank: {context['user_leaderboard_rank']}")

        if not summary_lines:
            summary_lines.append("No leaderboard data available in context.")

        response = " | ".join(summary_lines)

        return {
            "agent_name": self.name,
            "response": response,
            "updated_context": context
        }

    def to_crewai(self) -> CrewAgent:
        return CrewAgent(
            role="Progress Tracker",
            goal="Monitor and interpret competition progress based on leaderboard and performance data.",
            backstory=self.description,
            allow_delegation=False,
            verbose=True,
            tools=[]  # No tools; processes structured data only
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        config = llm_config or {"config_list": [{"model": "gpt-4", "temperature": 0.2}]}
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=self.description,
            human_input_mode="NEVER"
        )