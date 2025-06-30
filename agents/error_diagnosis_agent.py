from .base_agent import BaseAgent
from typing import Optional, Dict

class ErrorDiagnosisAgent(BaseAgent):
    def run(self, query: str, context: Optional[Dict[str, any]] = None) -> str:
        return (
            "ErrorDiagnosisAgent: Placeholder response. I diagnose runtime errors, exceptions, and logic bugs in user code. "
            "I would also offer fixes. Received query: "
            f"{query} | Context: {context}"
        )