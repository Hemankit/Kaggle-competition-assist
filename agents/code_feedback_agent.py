

from .base_agent import BaseAgent
from typing import Optional, Dict, Any

# CrewAI
from crewai import CrewAgent

# AutoGen
from autogen import ConversableAgent

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
class CodeFeedbackAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(
            name="CodeFeedbackAgent",
            description=(
                "Provides expert-level feedback on Kaggle competition code, including notebooks and modular scripts. "
                "Identifies bugs, inefficiencies, and code smells. Highlights missing best practices such as reproducibility, "
                "feature leakage checks, modular structure, and experiment tracking. Encourages clarity, scalability, and top-performing practices."
            )
        )
        self.llm = llm or ChatOpenAI(model_name="gpt-4")
        self.prompt = PromptTemplate.from_template(
            "You are a Kaggle code reviewer. {description}\n\nUser Query: {query}\nContext: {context}\n"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

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
        system_message = (
            "You are an expert Kaggle code reviewer. You provide high-quality, constructive feedback on user code "
            "submitted for machine learning competitions. You are especially skilled at spotting:\n"
            "- Code that is not modular (e.g., all logic in notebooks instead of reusable scripts)\n"
            "- Missing or weak cross-validation strategies\n"
            "- Data leakage issues (e.g., using target info in features or validation folds)\n"
            "- Lack of reproducibility (e.g., missing seeds, no config tracking)\n"
            "- Inefficient or non-scalable code (e.g., repeated feature generation)\n"
            "- Missing experiment tracking (e.g., no logging of metrics or version control)\n"
            "- Poor code hygiene (e.g., no docstrings, hardcoded paths, no type hints)\n"
            "- Incomplete or unclear comments/markdown in notebooks\n\n"
            "When giving feedback:\n"
            "- Be constructive and concise\n"
            "- Highlight strengths if any\n"
            "- Suggest next steps clearly\n"
            "- Avoid overwhelming the user; prioritize the most impactful issues first\n\n"
            "Assume the user is trying to improve their code quality to reach the top 5% in a Kaggle competition."
        )
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=system_message,
            human_input_mode="NEVER",
        )
