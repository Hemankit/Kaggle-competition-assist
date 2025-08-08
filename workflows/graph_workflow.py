from langgraph.graph import StateGraph
from typing import TypedDict, Dict, Any

from workflow.graph_nodes import (
    preprocessing_node,
    router_node,
    competition_summary_node,
    notebook_explainer_node,
    discussion_helper_node,
    error_diagnosis_node,
    execution_bridge_node,
    reasoning_node,
    conversational_node,
    memory_update_node,
    meta_monitor_node,
    meta_intervention_node,
    scoring_node,
    aggregation_node,
)

class OrchestratorState(TypedDict, total=False):
    original_query: str
    memory: Dict[str, Any]
    metadata: Dict[str, Any]
    cleaned_query: str
    tokens: list[str]
    structured_query: Dict[str, Any]
    selected_backend: str
    selected_agents: list[str]
    agent_outputs: list[Dict[str, Any]]
    reasoning_trace: list[str]
    conversation_trace: list[str]
    final_response: str
    intent: str
    meta_intervention_needed: bool

graph_builder = StateGraph(OrchestratorState)

graph_builder.add_node("preprocessing", preprocessing_node)
graph_builder.add_node("router", router_node)
graph_builder.add_node("competition_summary", competition_summary_node)
graph_builder.add_node("notebook_explainer", notebook_explainer_node)
graph_builder.add_node("discussion_helper", discussion_helper_node)
graph_builder.add_node("error_diagnosis", error_diagnosis_node)
graph_builder.add_node("execution_bridge", execution_bridge_node)
graph_builder.add_node("reasoning", reasoning_node)
graph_builder.add_node("conversational", conversational_node)
graph_builder.add_node("memory_update", memory_update_node)
graph_builder.add_node("meta_monitor", meta_monitor_node)
graph_builder.add_node("meta_intervention", meta_intervention_node)
graph_builder.add_node("scoring", scoring_node)
graph_builder.add_node("aggregation", aggregation_node)

graph_builder.set_entry_point("preprocessing")
graph_builder.add_edge("preprocessing", "router")
graph_builder.add_edge("router", "competition_summary")
graph_builder.add_edge("router", "notebook_explainer")
graph_builder.add_edge("router", "discussion_helper")
graph_builder.add_edge("router", "error_diagnosis")
graph_builder.add_edge("router", "execution_bridge")
graph_builder.add_edge("router", "reasoning")
graph_builder.add_edge("router", "conversational")

graph_builder.add_edge("competition_summary", "memory_update")
graph_builder.add_edge("notebook_explainer", "memory_update")
graph_builder.add_edge("discussion_helper", "memory_update")
graph_builder.add_edge("error_diagnosis", "memory_update")
graph_builder.add_edge("execution_bridge", "memory_update")
graph_builder.add_edge("reasoning", "memory_update")
graph_builder.add_edge("conversational", "memory_update")

graph_builder.add_edge("memory_update", "meta_monitor")
graph_builder.add_conditional_edges(
    "meta_monitor",
    lambda state: "meta_intervention" if state.get("meta_intervention_needed") else "scoring"
)
graph_builder.add_edge("meta_intervention", "scoring")
graph_builder.add_edge("scoring", "aggregation")
graph_builder.set_finish_point("aggregation")

compiled_graph = graph_builder.compile()


    
    