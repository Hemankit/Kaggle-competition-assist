from .base_agent import BaseAgent
from typing import Optional, Dict, Any

# For CrewAI
from crewai import CrewAgent

# For AutoGen
from autogen import ConversableAgent

class MultiHopReasoningAgent(BaseAgent):
    def __init__(self, name: str = "MultiHopReasoningAgent"):
        super().__init__(name)
        self.description = (
            "This agent performs multi-step reasoning across multiple sources, "
            "integrating insights from other agents or documents to solve complex queries."
        )

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        return (
            f"{self.name}: I perform multi-step reasoning across multiple sources, integrating insights from "
            f"agents or documents to solve complex queries.\n\nReceived query: {query}\nContext: {context}"
        )

    def to_crewai(self) -> CrewAgent:
        return CrewAgent(
            role="Multihop Reasoner",
            goal="Solve complex user queries by combining multiple sources of information and reasoning steps.",
            backstory=self.description,
            allow_delegation=True,
            verbose=True,
            tools=[],  # This agent does not use external tools directly
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        config = llm_config or {"config_list": [{"model": "gpt-4", "temperature": 0.2}]}
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=self.description,
            human_input_mode="NEVER",  # AutoGen agents communicate with each other, not the user directly
        )