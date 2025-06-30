from abc import ABC, abstractmethod
from typing import Any

class BaseCrewAgent(ABC):
    def __init__(self, name: str, role: str, goal: str, llm: Any = None):
        self.name = name
        self.role = role
        self.goal = goal
        self.llm = llm

    @abstractmethod
    def run(self, query: dict) -> dict:
        """
        Main reasoning entry point. To be implemented by subclasses.
        Should return a dict with 'agent_name' and 'response'.
        """
        pass
