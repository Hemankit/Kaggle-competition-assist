from .base_agent import BaseAgent
from typing import Optional, Dict

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

error_diagnosis_prompt = """
You are an expert code assistant. Given the following error message and code context, diagnose the likely cause of the error and suggest a fix.

Error/Exception:
----------------
{query}

Code Context:
----------------
{context}

Respond with a concise diagnosis and actionable fix.
"""

class ErrorDiagnosisAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(name="ErrorDiagnosisAgent")
        self.llm = llm or ChatOpenAI(model_name="gpt-4")
        self.prompt = PromptTemplate.from_template(error_diagnosis_prompt)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, query: str, context: Optional[Dict[str, any]] = None) -> str:
        context_str = str(context) if context else ""
        return self.chain.run(query=query, context=context_str)