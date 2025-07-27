from agents.base_agent import BaseAgent
from typing import Dict, Any, Optional

# CrewAI
from crewai import CrewAgent

# AutoGen
from autogen import ConversableAgent

# LLM support
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

progress_monitor_prompt = """
You are a strategic oversight agent monitoring user progress in a Kaggle competition.
Given the following context, identify any skipped critical phases (e.g., EDA, CV), score decisions against best practices, flag strategic risks (like poor validation or rushed modeling), and suggest targeted feedback or routing to other agents.

User Progress Context:
----------------------
{progress_context}

Respond with a concise, actionable summary.
"""

class StrategicMonitorAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(
            name="StrategicMonitorAgent",
            description=(
                "A strategic oversight agent that monitors user progress in a Kaggle competition. "
                "It checks for skipped critical phases (e.g., EDA, CV), scores decisions against best practices, "
                "flags strategic risks (like poor validation or rushed modeling), and routes targeted feedback to other agents."
            )
        )
        self.llm = llm or ChatOpenAI(model_name="gpt-4")
        self.prompt = PromptTemplate.from_template(progress_monitor_prompt)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, input_data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Convert context to a readable string for the LLM
        progress_context = "\n".join(f"{k}: {v}" for k, v in context.items())
        summary = self.chain.run(progress_context=progress_context)
        return {
            "agent_name": self.name,
            "response": summary,
            "updated_context": context
        }

    def to_crewai(self) -> CrewAgent:
        return CrewAgent(
            role="Strategic Progress Monitor",
            goal="Track competition progress and flag strategic risks such as skipped EDA, missing validation, or premature submissions. Suggest interventions or route to other agents.",
            backstory=(
                "You're responsible for ensuring the user follows a robust strategy throughout the Kaggle competition lifecycle. "
                "You identify skipped phases, misaligned priorities, or bad modeling practices and route alerts to relevant expert agents for action."
            ),
            allow_delegation=True,
            verbose=True,
            tools=[]
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        config = llm_config or {"config_list": [{"model": "gpt-4", "temperature": 0.2}]}
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=(
                "You are a strategic oversight agent. Monitor user competition progress for skipped steps, poor practices, "
                "or risk factors such as too many models too early, no cross-validation strategy, or missing EDA. "
                "Summarize your findings, score strategic soundness, and if necessary, suggest routing to other agents "
                "(e.g., CodeFeedbackAgent, TimelineCoachAgent). Be concise but directive."
            ),
            human_input_mode="NEVER"
        )