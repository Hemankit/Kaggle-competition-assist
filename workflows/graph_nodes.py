
from typing import Any, Dict
import asyncio
from agents import (
    competition_summary_agent,
    notebook_explainer_agent,
    discussion_helper_agent,
    error_diagnosis_agent,
    ProgressMonitorAgent
)
from crewai import Crew, Task
from orchestrators import orchestrator, crewAI_orchestrator, autogen_conversational_orchestrator
from dispatching.dispatch import dispatch_query
from utils.preprocessing import preprocess_query

# === Preprocessing ===
def preprocessing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    original_query = state.get("original_query", "")
    processed = preprocess_query(original_query)

    state.update({
        "cleaned_query": processed["cleaned_query"],
        "tokens": processed.get("tokens", []),
        "metadata": processed.get("metadata", {})
    })

    memory = state.get("memory", {})
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
        state.setdefault("reasoning_trace", []).append(
            f"Loop detected: '{original_query}' appeared {past_queries.count(original_query)} times. Escalating to meta-intervention."
        )
        return state

    route_result = orchestrator.route_to_agents(original_query)

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
    state.setdefault("reasoning_trace", []).append(
        f"Structured query generated: {structured_query}"
    )

    dispatch_result = dispatch_query(structured_query, memory=memory)
    state["selected_agents"] = dispatch_result["selected_agents"]
    state["selected_backend"] = dispatch_result["selected_backend"]
    state.setdefault("reasoning_trace", []).extend([
        f"Dispatched to backend: {dispatch_result['selected_backend']} with agents: {dispatch_result['selected_agents']}",
        f"Dispatch reasoning: {dispatch_result['dispatch_reason']}"
    ])

    return state

# === Reasoning Nodes ===
async def run_concurrent_orchestrators(user_query: str, metadata: dict):
    crewai_task = asyncio.create_task(crewAI_orchestrator.run(user_query=user_query, metadata=metadata))
    autogen_task = asyncio.create_task(autogen_conversational_orchestrator.run(user_query=user_query, metadata=metadata))

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
        result = crewAI_orchestrator.run(user_query, metadata)
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
        result = autogen_conversational_orchestrator.run(user_query, metadata)
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

def competition_summary_node(state): 
    return run_agent_if_intent_matches(state, ["data", "overview"], competition_summary_agent, "CompetitionSummaryAgent")

def notebook_explainer_node(state): 
    return run_agent_if_intent_matches(state, ["code", "model"], notebook_explainer_agent, "NotebookExplainerAgent")

def discussion_helper_node(state): 
    return run_agent_if_intent_matches(state, ["discussion"], discussion_helper_agent, "DiscussionHelperAgent")

def error_diagnosis_node(state): 
    return run_agent_if_intent_matches(state, ["error", "bug", "troubleshooting"], error_diagnosis_agent, "ErrorDiagnosisAgent")

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
    no_output_recently = any(len(batch) == 0 for batch in agent_outputs_log[-2:])
    switching_intents = len(set(intent_history[-3:])) > 2

    needs_intervention = too_repetitive or no_output_recently or switching_intents
    state.setdefault("reasoning_trace", []).append(
        f"[MetaMonitor] Intervention needed? {needs_intervention} | Repetitive: {too_repetitive}, Output Missing: {no_output_recently}, Switching Intents: {switching_intents}"
    )
    state["meta_intervention_needed"] = needs_intervention
    return state

def meta_intervention_node(state: Dict[str, Any]) -> Dict[str, Any]:
    agent = ProgressMonitorAgent().get_crew_agent()
    task = Task(
        name="Meta-Intervention Analysis",
        description="Diagnose why recent runs have failed or stalled. Recommend a different approach, reasoning style, or agent mix.",
        agent=agent,
        context={"memory": state.get("memory", {})},
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

# === Scoring & Aggregation ===
def scoring_node(state: Dict[str, Any]) -> Dict[str, Any]:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.chat_models import ChatOpenAI

    scoring_prompt = PromptTemplate.from_template(
        """You are evaluating the quality of an assistant's response.

        Response:
        {response}

        Rate the response on a scale of 0 to 100 based on:
        - Relevance to the user's query
        - Specificity and usefulness
        - Clarity and structure

        Only return a number.
        """
    )

    scoring_chain = LLMChain(llm=ChatOpenAI(temperature=0.0), prompt=scoring_prompt)
    scored_outputs = []
    for output in state.get("agent_outputs", []):
        try:
            score_str = scoring_chain.run(response=output["response"])
            score = int(score_str.strip())
            output["score"] = score
            state.setdefault("reasoning_trace", []).append(
                f"Scored agent {output['agent_name']} with {score}/100"
            )
        except Exception as e:
            output["score"] = 50
            state.setdefault("reasoning_trace", []).append(
                f"Scoring failed for {output['agent_name']}: {e}"
            )
        scored_outputs.append(output)

    state["agent_outputs"] = scored_outputs
    return state

def aggregation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    responses = state.get("agent_outputs", [])
    if not responses:
        state["final_response"] = "No relevant agent responses to aggregate."
        return state
    final = orchestrator.aggregate_response(responses)
    state["final_response"] = final
    return state
