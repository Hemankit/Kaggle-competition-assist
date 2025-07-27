from .base_agent import BaseAgent
from typing import Optional, Dict, Any

# For CrewAI
from crewai import CrewAgent

# For AutoGen
from autogen import ConversableAgent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

class MultiHopReasoningAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(name)
        self.description = (
            "An expert reasoning agent that performs multi-step, multi-source synthesis. It answers complex Kaggle "
            "competition queries by combining insights from notebooks, metadata, discussion posts, and previous agent outputs. "
            "It is skilled in chaining reasoning steps, identifying dependencies, and drawing conclusions from scattered signals."
        )
        self.llm = llm or ChatOpenAI(model_name="gpt-4")
        self.prompt = PromptTemplate.from_template(
            "You are a multi-hop reasoning agent. {description}\n\nUser Query: {query}\nContext: {context}\n"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)


    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        return (
            f"{self.name}: I perform multi-step reasoning across multiple sources, integrating insights from "
            f"agents or documents to solve complex queries.\n\nReceived query: {query}\nContext: {context}"
        )

    def to_crewai(self) -> CrewAgent:
        return CrewAgent(
            role="Multihop Reasoning Expert",
            goal=(
                "Answer complex or layered user questions by synthesizing evidence from multiple sources — including "
                "code, competition data, discussions, and feedback from other agents."
            ),
            backstory=(
                "You're a reasoning specialist who excels at solving ambiguous or multi-layered challenges that require "
                "chaining together logic from multiple domains. You are called upon when simpler agents can't fully "
                "resolve a query using isolated context."
            ),
            allow_delegation=True,
            verbose=True,
            tools=[],
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        config = llm_config or {"config_list": [{"model": "gpt-4", "temperature": 0.3}]}
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=(
                "You are a multi-hop reasoning agent working in a Kaggle competition assistant system. Your role is "
                "to integrate information across different documents and agents — such as notebook code, model summaries, "
                "feature pipelines, leaderboard metadata, and user discussions — to reason through complex or layered questions. "
                "When answering, chain your logic step-by-step, referencing relevant inputs or dependencies explicitly."
            ),
            human_input_mode="NEVER",
        )