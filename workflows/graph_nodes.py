
from typing import Any, Dict
import asyncio
from agents import (
    CompetitionSummaryAgent,
    NotebookExplainerAgent,
    DiscussionHelperAgent,
    ErrorDiagnosisAgent,
    ProgressMonitorAgent
)
from crewai import Crew, Task
from orchestrators.expert_orchestrator_langgraph import ExpertSystemOrchestratorLangGraph as orchestrator
from orchestrators.reasoning_orchestrator import ReasoningOrchestrator as crewAI_orchestrator
from orchestrators.reasoning_orchestrator import ReasoningOrchestrator as autogen_conversational_orchestrator
from routing.intent_router import parse_user_intent
from query_processing.preprocessing import preprocess_query

# === Preprocessing ===
def preprocessing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    original_query = state.get("original_query", "")
    processed = preprocess_query(original_query)

    state.update({
        "cleaned_query": processed["cleaned"],
        "tokens": processed.get("tokens", []),
        "metadata": processed.get("metadata", {})
    })

    memory = state.get("memory") or {}
    past_queries = memory.get("past_queries", [])
    past_queries.append(original_query)
    memory["past_queries"] = past_queries[-10:]
    state["memory"] = memory

    return state

# === Routing ===
def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    original_query = state.get("original_query", "")
    memory = state.get("memory", {})
    past_queries = memory.get("past_queries", [])

    if past_queries.count(original_query) >= 3:
        state["intent"] = "meta-intervention"
        reasoning_trace = state.setdefault("reasoning_trace", [])
        if reasoning_trace is not None:
            reasoning_trace.append(f"Loop detected: '{original_query}' appeared {past_queries.count(original_query)} times. Escalating to meta-intervention.")
        else:
            state["reasoning_trace"] = [f"Loop detected: '{original_query}' appeared {past_queries.count(original_query)} times. Escalating to meta-intervention."]
        return state

    route_result = parse_user_intent(original_query)
    
    # Handle case where parse_user_intent returns None
    if route_result is None:
        route_result = {}

    structured_query = {
        "intent": route_result.get("intent", "reasoning"),
        "sub_intents": route_result.get("sub_intents", []),
        "input_references": route_result.get("input_references", []),
        "reasoning_style": route_result.get("reasoning_style", "default"),
        "preferred_agents": route_result.get("preferred_agents", []),
        "metadata_flags": route_result.get("metadata_flags", {})
    }

    state["structured_query"] = structured_query
    state["intent"] = structured_query["intent"]
    reasoning_trace = state.setdefault("reasoning_trace", [])
    if reasoning_trace is not None:
        reasoning_trace.append(f"Structured query generated: {structured_query}")
    else:
        state["reasoning_trace"] = [f"Structured query generated: {structured_query}"]

    # Simple agent selection based on intent
    if structured_query["intent"] in ["competition", "overview"]:
        state["selected_agents"] = ["competition_summary"]
        state["selected_backend"] = "langgraph"
    elif structured_query["intent"] in ["notebook", "code", "explanation"]:
        state["selected_agents"] = ["notebook_explainer"]
        state["selected_backend"] = "langgraph"
    elif structured_query["intent"] in ["discussion", "forum"]:
        state["selected_agents"] = ["discussion_helper"]
        state["selected_backend"] = "langgraph"
    elif structured_query["intent"] in ["error", "debug"]:
        state["selected_agents"] = ["error_diagnosis"]
        state["selected_backend"] = "langgraph"
    else:
        state["selected_agents"] = ["competition_summary"]
        state["selected_backend"] = "langgraph"
    
    state.setdefault("reasoning_trace", []).extend([
        f"Selected backend: {state['selected_backend']} with agents: {state['selected_agents']}",
        f"Selection reasoning: Based on intent '{structured_query['intent']}'"
    ])

    return state

# === Reasoning Nodes ===
async def run_concurrent_orchestrators(user_query: str, metadata: dict):
    crewai_task = asyncio.create_task(crewAI_orchestrator.run({"query": user_query, "mode": "crewai"}))
    autogen_task = asyncio.create_task(autogen_conversational_orchestrator.run({"query": user_query, "mode": "autogen"}))

    crew_output = await crewai_task
    autogen_output = await autogen_task
    return crew_output, autogen_output

def execution_bridge_node(state: Dict[str, Any]) -> Dict[str, Any]:
    user_query = state.get("user_query", "")
    metadata = state.get("metadata", {})

    try:
        crew_output, autogen_output = asyncio.run(run_concurrent_orchestrators(user_query, metadata))
    except Exception as e:
        crew_output = f"[Error from CrewAI]: {str(e)}"
        autogen_output = f"[Error from AutoGen]: {str(e)}"

    return {
        **state,
        "crew_output": crew_output,
        "autogen_output": autogen_output,
        "agent_outputs": [str(crew_output), str(autogen_output)],
        "last_completed": "execution_bridge"
    }

def reasoning_node(state: Dict[str, Any]) -> Dict[str, Any]:
    user_query = state.get("original_query", "")
    metadata = state.get("metadata", {})
    try:
        result = crewAI_orchestrator.run({"query": user_query, "mode": "crewai"})
        state["crew_result"] = result
        state.setdefault("reasoning_trace", []).append("Multi-agent reasoning node executed.")
        state.setdefault("agent_outputs", []).append(result)
    except Exception as e:
        state["crew_result"] = {"error": str(e)}
        state.setdefault("reasoning_trace", []).append(f"Multi-agent reasoning node failed: {str(e)}")
    return state

def conversational_node(state: Dict[str, Any]) -> Dict[str, Any]:
    user_query = state.get("original_query", "")
    metadata = state.get("metadata", {})
    try:
        result = autogen_conversational_orchestrator.run({"query": user_query, "mode": "autogen"})
        state.setdefault("agent_outputs", []).append(result)
        state.setdefault("conversation_trace", []).append("AutoGen conversational agent executed")
    except Exception as e:
        state.setdefault("agent_outputs", []).append({"error": str(e)})
        state.setdefault("conversation_trace", []).append(f"AutoGen conversational agent failed: {str(e)}")
    return state

# === Agent Execution Nodes ===
def run_agent_if_intent_matches(state, valid_intents, agent, agent_name):
    intent = state.get("intent", "")
    if intent in valid_intents:
        response = agent.run(state["structured_query"])
        state.setdefault("agent_outputs", []).append(response)
        state.setdefault("reasoning_trace", []).append(f"{agent_name} executed for intent: {intent}")
    return state

def run_agent_if_intent_matches(state: Dict[str, Any], target_intents: list, agent_class, agent_name: str) -> Dict[str, Any]:
    """Helper function to run agent if intent matches"""
    current_intent = state.get("intent", "")
    if current_intent in target_intents or any(intent in current_intent for intent in target_intents):
        try:
            agent = agent_class()
            query = state.get("cleaned_query", state.get("original_query", ""))
            result = agent.run(query)
            state.setdefault("agent_outputs", []).append({
                "agent_name": agent_name, 
                "response": result.get("response", str(result))
            })
            state.setdefault("reasoning_trace", []).append(f"Executed {agent_name} for intent '{current_intent}'")
        except Exception as e:
            state.setdefault("reasoning_trace", []).append(f"Failed to execute {agent_name}: {e}")
    return state

def competition_summary_node(state: Dict[str, Any]) -> Dict[str, Any]: 
    return run_agent_if_intent_matches(state, ["competition", "overview", "data"], CompetitionSummaryAgent, "CompetitionSummary")

def notebook_explainer_node(state: Dict[str, Any]) -> Dict[str, Any]: 
    return run_agent_if_intent_matches(state, ["notebook", "code", "model", "explanation"], NotebookExplainerAgent, "NotebookExplainer")

def discussion_helper_node(state: Dict[str, Any]) -> Dict[str, Any]: 
    return run_agent_if_intent_matches(state, ["discussion", "forum"], DiscussionHelperAgent, "DiscussionHelper")

def error_diagnosis_node(state: Dict[str, Any]) -> Dict[str, Any]: 
    return run_agent_if_intent_matches(state, ["error", "bug", "troubleshooting", "debug"], ErrorDiagnosisAgent, "ErrorDiagnosis")

# === Memory Update ===
def memory_update_node(state: Dict[str, Any]) -> Dict[str, Any]:
    memory = state.setdefault("memory", {})
    original_query = state.get("original_query", "")
    memory.setdefault("past_queries", []).append(original_query)
    memory.setdefault("agent_outputs_log", []).append(state.get("agent_outputs", []))
    memory.setdefault("reasoning_trace_log", []).append(state.get("reasoning_trace", []))
    memory.setdefault("intent_history", []).append(state.get("intent", "unknown"))
    state["memory"] = memory
    return state

# === Meta Monitoring ===
def meta_monitor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    memory = state.get("memory", {})
    past_queries = memory.get("past_queries", [])
    agent_outputs_log = memory.get("agent_outputs_log", [])
    intent_history = memory.get("intent_history", [])

    too_repetitive = len(past_queries) >= 3 and len(set(past_queries[-3:])) == 1
    no_output_recently = any(len(batch or []) == 0 for batch in agent_outputs_log[-2:])
    switching_intents = len(set(intent_history[-3:])) > 2

    needs_intervention = too_repetitive or no_output_recently or switching_intents
    state.setdefault("reasoning_trace", []).append(
        f"[MetaMonitor] Intervention needed? {needs_intervention} | Repetitive: {too_repetitive}, Output Missing: {no_output_recently}, Switching Intents: {switching_intents}"
    )
    state["meta_intervention_needed"] = needs_intervention
    return state

def meta_intervention_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent = ProgressMonitorAgent().to_crewai()
    task = Task(
        name="Meta-Intervention Analysis",
        description="Diagnose why recent runs have failed or stalled. Recommend a different approach, reasoning style, or agent mix.",
        agent=agent,
        context=[],  # CrewAI Task.context expects a list, not a dict
        expected_output="Actionable diagnosis and re-strategizing"
    )
    crew = Crew(agents=[agent], tasks=[task], process="sequential")
    try:
        output = crew.kickoff()
        state.setdefault("reasoning_trace", []).append(f"[MetaIntervention] {output}")
        state["agent_outputs"].append({"agent_name": "ProgressMonitor", "response": output})
    except Exception as e:
        state.setdefault("reasoning_trace", []).append(f"[MetaIntervention] Failed: {e}")
    return state

# === Aggregation ===

def aggregation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    responses = state.get("agent_outputs", [])
    if not responses:
        state["final_response"] = "No relevant agent responses to aggregate."
        return state
    final = orchestrator.aggregate_response(responses)
    state["final_response"] = final
    return state
