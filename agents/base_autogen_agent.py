from abc import ABC, abstractmethod

class BaseAutoGenAgent(ABC):
    def __init__(self, name: str, role: str, goal: str, llm: any = None):
        self.name = name
        self.role = role
        self.goal = goal
        self.llm = llm

    @abstractmethod
    def plan_and_execute(self, query: dict) -> dict:
        """
        Plan and coordinate actions with other agents.
        """
        pass