from .base_agent import BaseAgent
from typing import Optional, Dict, Any

# CrewAI
from crewai import Agent

# AutoGen
from autogen import ConversableAgent

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from llms.llm_loader import get_llm_from_config

class TimelineCoachAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(
            name="TimelineCoachAgent",
            description=(
                "Expert in structuring personalized Kaggle competition timelines. Helps users break down the competition "
                "into realistic milestones across the typical phases: EDA, baseline modeling, feature engineering, modeling, "
                "ensembling, and final submissions. Also coaches users on best practices for time management, experiment tracking, "
                "and resource prioritization based on the competition length and user goals."
            )
        )
        self.llm = llm or get_llm_from_config(section="reasoning_and_interaction")
        self.prompt = PromptTemplate.from_template(
            "You are a Kaggle Timeline Coach. {description}\n\nUser Query: {query}\n"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # ✅ FIXED: Actually use the LLM chain to generate meaningful response
        try:
            response = self.chain.run(
                description=self.description,
                query=query
            )
        except Exception as e:
            # Fallback if LLM fails
            response = (
                f"I help structure Kaggle competition timelines. "
                f"For your query: {query}\n\n"
                f"Typical competition phases:\n"
                f"1. Problem Understanding & EDA (~10-15%)\n"
                f"2. Baseline & Validation Setup (~10%)\n"
                f"3. Feature Engineering (~20-25%)\n"
                f"4. Modeling & Experimentation (~25-30%)\n"
                f"5. Ensembling & Optimization (~15-20%)\n"
                f"6. Final Submission & Cleanup (~5-10%)\n\n"
                f"Adjust these based on your available time and competition length."
            )
        
        return {
            "agent_name": self.name,
            "response": response,
            "updated_context": context
        }
    
    def to_crewai(self) -> Agent:
        return Agent(
            role="Competition Timeline Coach",
            goal="Help users create effective, phase-based timelines for Kaggle competitions — balancing deep exploration, fast iteration, and submission reliability.",
            backstory=(
                "You're a seasoned Kaggle competition strategist. You've studied how top competitors approach their workflows, "
                "and you specialize in helping users manage their time effectively across different competition phases. "
                "You coach users on EDA, baseline modeling, feature engineering, model experimentation, ensembling, and submission prep. "
                "You're practical, realistic, and prioritize building reliable pipelines over chasing leaderboard noise."
            ),
            llm=self.llm,  # Use Perplexity LLM
            allow_delegation=False,
            verbose=True,
            tools=[]
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        # Use Perplexity for reasoning via llm_loader config
        config = llm_config or {"config_list": [{"model": "sonar", "temperature": 0.3}]}

        system_prompt = (
            "You are a Kaggle Timeline Coach. Your job is to help users structure their competition strategy using best practices from top Kaggle competitors.\n\n"
            "You break down the timeline into clear phases:\n"
            "1. Problem Understanding & EDA (~10–15%)\n"
            "2. Baseline & Validation Setup (~10%)\n"
            "3. Feature Engineering (~20–25%)\n"
            "4. Modeling & Experimentation (~25–30%)\n"
            "5. Ensembling & Optimization (~15–20%)\n"
            "6. Final Submission & Cleanup (~5–10%)\n\n"
            "Your responsibilities:\n"
            "- Adjust these phases to fit the user’s available time (e.g. 1-month vs 3-month competition)\n"
            "- Incorporate the user’s goals, e.g., top 5%, learning-focused, or team-based efforts\n"
            "- Recommend practices like logging experiments, modularizing pipelines, or setting LB buffers\n"
            "- Encourage users to balance exploration and delivery — not just leaderboard chasing\n\n"
            "Respond with structured plans, tables, or step-by-step advice as appropriate."
        )

        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=system_prompt,
            human_input_mode="NEVER"
        )