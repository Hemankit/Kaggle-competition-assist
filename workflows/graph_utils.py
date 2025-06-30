# workflow/graph_utils.py

from typing import Dict, Any

def merge_states(state1: Dict[str, Any], state2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two LangGraph states, prioritizing state2 on key collisions."""
    merged = state1.copy()
    merged.update(state2)
    return merged

def extract_agent_response(state: Dict[str, Any], agent_key: str) -> str:
    """Get a clean response from a specific agent's output."""
    return state.get("agent_outputs", {}).get(agent_key, "")

def add_to_history(state: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    state.setdefault("history", []).append({key: value})
    return state
