from .base_agent import BaseAgent
from typing import Optional, Dict, Any

# CrewAI
from crewai import CrewAgent

# AutoGen
from autogen import ConversableAgent

class TimelineCoachAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TimelineCoachAgent",
            description=(
                "Helps plan personalized competition timelines, break down project milestones, and manage realistic deadlines "
                "based on competition end dates, phases, and user goals."
            )
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        return (
            f"{self.name}: Placeholder response. I help users organize their workflow for Kaggle competitions — "
            f"defining goals, phases, and deadlines.\n\nQuery: {query}\nContext: {context}"
        )

    def to_crewai(self) -> CrewAgent:
        return CrewAgent(
            role="Timeline Planner",
            goal="Help users define structured timelines and realistic milestones for participating in Kaggle competitions.",
            backstory=self.description,
            allow_delegation=False,
            verbose=True,
            tools=[]
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        config = llm_config or {"config_list": [{"model": "gpt-4", "temperature": 0.2}]}
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=self.description,
            human_input_mode="NEVER"
        )