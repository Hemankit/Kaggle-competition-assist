# routing/capability_scoring.py

from routing.registry import AGENT_REGISTRY
from typing import List, Dict, Optional


def find_agents_by_subintent(
    subintent: str,
    reasoning_style: Optional[str] = None,
    include_scores: bool = True,
    min_score_threshold: float = 0.3
) -> List[Dict[str, float]]:
    matches = []

    for agent_name, metadata in AGENT_REGISTRY.items():
        score = 0.0
        explanation = []

        # Capability match
        if subintent in metadata.get("capabilities", []):
            score += 0.6
            explanation.append("capability match (+0.6)")

        # Reasoning style match
        if reasoning_style and reasoning_style in metadata.get("reasoning_styles", []):
            score += 0.3
            explanation.append("reasoning style match (+0.3)")

        # Tag match
        if subintent in metadata.get("tags", []):
            score += 0.2
            explanation.append("tag match (+0.2)")

        if score >= min_score_threshold:
            matches.append({
                "agent": agent_name,
                "score": round(score, 2),
                "explanation": ", ".join(explanation)
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches