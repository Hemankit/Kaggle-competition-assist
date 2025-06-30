from .base_agent import BaseAgent
from typing import Optional, Dict, Any

# CrewAI
from crewai import CrewAgent

# AutoGen
from autogen import ConversableAgent

class CodeFeedbackAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CodeFeedbackAgent",
            description=(
                "Provides feedback on notebook or model code quality, identifying potential bugs, inefficiencies, or "
                "opportunities for improved style and clarity."
            )
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        return (
            f"{self.name}: Placeholder response. I would review user code, detect weaknesses or bad practices, "
            f"and suggest improvements.\n\nReceived query: {query}\nContext: {context}"
        )

    def to_crewai(self) -> CrewAgent:
        return CrewAgent(
            role="Code Reviewer",
            goal="Review code from Kaggle notebooks or models and provide suggestions for improvement.",
            backstory=self.description,
            allow_delegation=False,
            verbose=True,
            tools=[],
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        config = llm_config or {"config_list": [{"model": "gpt-4", "temperature": 0.2}]}
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=self.description,
            human_input_mode="NEVER",
        )