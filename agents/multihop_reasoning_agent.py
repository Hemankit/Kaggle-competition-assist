from .base_agent import BaseAgent
from typing import Optional, Dict, Any

# For CrewAI
from crewai import Agent

# For AutoGen
from autogen import ConversableAgent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from llms.llm_loader import get_llm_from_config

class MultiHopReasoningAgent(BaseAgent):
    def __init__(self, llm=None):
        description = (
            "An expert reasoning agent that performs multi-step, multi-source synthesis. It answers complex Kaggle "
            "competition queries by combining insights from notebooks, metadata, discussion posts, and previous agent outputs. "
            "It is skilled in chaining reasoning steps, identifying dependencies, and drawing conclusions from scattered signals."
        )
        super().__init__("MultiHopReasoningAgent", description)
        self.llm = llm or get_llm_from_config(section="reasoning_and_interaction")
        self.prompt = PromptTemplate.from_template(
            "You are a multi-hop reasoning agent. {description}\n\nUser Query: {query}\nContext: {context}\n"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)


    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = (
            f"{self.name}: I perform multi-step reasoning across multiple sources, integrating insights from "
            f"agents or documents to solve complex queries.\n\nReceived query: {query}\nContext: {context}"
        )
        return {
            "agent_name": self.name,
            "response": response,
            "updated_context": context
        }

    def to_crewai(self) -> Agent:
        return Agent(
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
            llm=self.llm,  # Use Perplexity LLM
            allow_delegation=True,
            verbose=True,
            tools=[],
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        # Use Perplexity for reasoning via llm_loader config
        config = llm_config or {"config_list": [{"model": "sonar", "temperature": 0.3}]}
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