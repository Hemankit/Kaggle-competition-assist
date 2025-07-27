# routing/intent_router.py

from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.language_models.chat_models import BaseChatModel

from routing.capability_scoring import find_agents_by_subintent
from llms.llm_loader import get_llm_from_config # Optional: central LLM fetch

# === Prompt ===
ROUTER_PROMPT = PromptTemplate.from_template("""
You are a routing engine for an AI system that processes user queries about Kaggle competitions.

Given the query: "{query}", identify the following:
- Main intent: (e.g. "overview", "model", "discussion", "error", "meta", etc.)
- Sub-intents: list of finer-grained tags (e.g. "metrics", "training", "stacktrace", etc.)
- Reasoning style: "fast", "accurate", or "conversational"
- Input references: any keywords that signal what section or file is referenced
- Preferred agents: list of agents (if clear from query)
- Metadata flags: extra notes (e.g. urgency, ambiguity)

Respond in JSON with keys: intent, sub_intents, input_references, reasoning_style, preferred_agents, metadata_flags.
""")

parser = JsonOutputParser()

# === Chain Builder ===
def build_router_chain(llm: BaseChatModel) -> Runnable:
    return ROUTER_PROMPT | llm | parser

# === Standalone Parse Method ===
def parse_user_intent(query: str, llm: BaseChatModel = None) -> Dict[str, Any]:
    """
    Core utility used by all orchestrators. Parses query into structured intent.
    If no LLM is passed, fallback to default router model.
    Adds recommended_mode based on reasoning style and sub-intents.
    """
    llm = llm or get_llm_from_config()
    chain = build_router_chain(llm)
    parsed = chain.invoke({"query": query})

    # --- Auto-mode selection logic ---
    reasoning_style = parsed.get("reasoning_style", "").lower()
    subintents = parsed.get("sub_intents", [])

    if reasoning_style == "multi-hop":
        parsed["recommended_mode"] = "autogen"
    elif any(s in ["timeline_planning", "code_feedback", "eda_summary"] for s in subintents):
        parsed["recommended_mode"] = "crewai"
    elif "strategic_monitoring" in subintents:
        parsed["recommended_mode"] = "hybrid"
    else:
        parsed["recommended_mode"] = "crewai"  # default fallback

    return parsed

# === Optional Utility That Selects Agents Too ===
def route_to_agents(query: str, llm: BaseChatModel = None) -> Dict[str, Any]:
    """
    (Optional) Wrapper that parses query and also selects matching agents.
    Can be deprecated in favor of orchestration logic that handles capability filtering separately.
    """
    parsed = parse_user_intent(query, llm)
    subintents = parsed.get("sub_intents", [])
    auto_mode = parsed.get("reasoning_style", "") == "conversational"

    selected_agents = find_agents_by_subintent(subintents, autogen=auto_mode)
    parsed["preferred_agents"] = selected_agents
    return parsed

