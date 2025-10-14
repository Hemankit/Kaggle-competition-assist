
import json
from typing import Dict, Any, Optional
from routing.intent_router import parse_user_intent
from routing.capability_scoring import find_agents_by_subintent
from routing.registry import AGENT_CAPABILITY_REGISTRY


class BaseOrchestratorUtils:
    """
    Shared utility functions for orchestrators to reduce duplication.
    Adds support for execution trace logging.
    """

    def __init__(self):
        self.last_execution_trace = []  # Stores the last execution trace (list of activated nodes)

    def log_execution_trace(self, trace: list):
        """
        Stores the execution trace (list of activated nodes) for the last query.
        """
        self.last_execution_trace = trace

    def get_last_execution_trace(self) -> list:
        """
        Returns the list of activated nodes for the last query.
        """
        return self.last_execution_trace

    def parse_intent(self, user_query: str) -> Dict[str, Any]:
        try:
            return parse_user_intent(user_query)
        except Exception as e:
            return {
                "intent": "reasoning",
                "sub_intents": [],
                "input_references": [],
                "reasoning_style": "default",
                "preferred_agents": [],
                "metadata_flags": {},
                "confidence_score": 0.0,
                "uncertain_parse": True,
                "query_mode": "exploration",
                "llm_parse_error": str(e),
                "raw_output": user_query
            }

    def get_agent_matches(
        self,
        subintent: str,
        reasoning_style: Optional[str] = None,
        min_score: float = 0.3
    ):
        return find_agents_by_subintent(
            subintent=subintent,
            reasoning_style=reasoning_style,
            min_score_threshold=min_score
        )

    def explain_matches(self, subintents: list, style: Optional[str] = None):
        explanations = []
        for subintent in subintents:
            matches = self.get_agent_matches(subintent, style)
            for match in matches:
                explanations.append(f"{match['agent']} matched for {subintent} ({match['explanation']})")
        return explanations