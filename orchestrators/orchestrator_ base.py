
import json
from typing import Dict, Any, Optional
from routing.intent_router import parse_user_intent
from routing.capability_scoring import find_agents_by_subintent
from routing.registry import AGENT_CAPABILITY_REGISTRY


class BaseOrchestratorUtils:
    """
    Shared utility functions for orchestrators to reduce duplication.
    """

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
        registry: Dict[str, Any] = AGENT_CAPABILITY_REGISTRY,
        min_score: float = 0.3
    ):
        return find_agents_by_subintent(
            subintent=subintent,
            reasoning_style=reasoning_style,
            registry=registry,
            min_score_threshold=min_score
        )

    def explain_matches(self, subintents: list, style: Optional[str] = None):
        explanations = []
        for subintent in subintents:
            matches = self.get_agent_matches(subintent, style)
            for match in matches:
                explanations.append(f"{match['agent']} matched for {subintent} ({match['explanation']})")
        return explanations