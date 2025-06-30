from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract base class for all expert system agents.
    Enforces a common interface across agents.
    """

    def __init__(self, name: str, description: str, tools: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.tools = tools or {}

    @abstractmethod
    def run(self, input_data: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's logic.

        Args:
            input_data (str): The query or subtask assigned to the agent.
            context (dict): Shared memory passed between agents.

        Returns:
            dict: {
                "agent_name": str,
                "response": str,
                "updated_context": dict (optional)
            }
        """
        pass
