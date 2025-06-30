from agents import (
    CompetitionSummaryAgent,
    TimelineCoachAgent,
    NotebookExplainerAgent,
    DiscussionHelperAgent,
    MultiHopReasoningAgent,
    ErrorDiagnosisAgent,
    CodeFeedbackAgent,
    ProgressMonitorAgent,
)
from typing import Optional

# === Registry for LangGraph / LangChain-based orchestration === #
AGENT_CAPABILITY_REGISTRY = {
    "competition_summary": {
        "agent_class": CompetitionSummaryAgent,
        "capabilities": ["competition_overview", "rules", "description"],
        "reasoning_styles": ["default", "summary"],
        "tags": ["overview", "summary", "competition"],
    },
    "timeline_coach": {
        "agent_class": TimelineCoachAgent,
        "capabilities": ["planning", "milestones", "deadline_tracking"],
        "reasoning_styles": ["timeline", "project_management"],
        "tags": ["calendar", "schedule"],
    },
    "notebook_explainer": {
        "agent_class": NotebookExplainerAgent,
        "capabilities": ["explain_code", "walkthrough_notebook", "interpret_models"],
        "reasoning_styles": ["stepwise", "didactic"],
        "tags": ["notebook", "education", "learning"],
    },
    "discussion_helper": {
        "agent_class": DiscussionHelperAgent,
        "capabilities": ["summarize_replies", "generate_questions", "clarify_forum_posts"],
        "reasoning_styles": ["conversational", "contextual"],
        "tags": ["forum", "kaggle", "help"],
    },
    "code_feedback": {
        "agent_class": CodeFeedbackAgent,
        "capabilities": ["refactor_code", "style_feedback", "improve_code"],
        "reasoning_styles": ["constructive", "style-based"],
        "tags": ["coding", "feedback"],
    },
    "progress_monitor": {
        "agent_class": ProgressMonitorAgent,
        "capabilities": ["track_progress", "benchmarking", "suggest_next_steps"],
        "reasoning_styles": ["progressive", "timeline_based"],
        "tags": ["planning", "feedback", "monitoring"],
    },
    "multi_hop_reasoning": {
        "agent_class": MultiHopReasoningAgent,
        "capabilities": ["multihop_reasoning", "graph_reasoning", "complex_logic"],
        "reasoning_styles": ["stepwise", "chained", "contrastive"],
        "tags": ["graph", "advanced", "multiagent"],
    },
    "error_diagnosis": {
        "agent_class": ErrorDiagnosisAgent,
        "capabilities": ["error_detection", "bug_explanation", "log_analysis"],
        "reasoning_styles": ["diagnostic", "stepwise"],
        "tags": ["debugging", "errors"],
    },
}

# === Registry for CrewAI (Autogen-style multi-agent reasoning orchestration) === #
AUTOGEN_AGENT_REGISTRY = {
    "multi_hop_reasoning": AGENT_CAPABILITY_REGISTRY["multi_hop_reasoning"],
    "error_diagnosis": AGENT_CAPABILITY_REGISTRY["error_diagnosis"],
    "code_feedback": AGENT_CAPABILITY_REGISTRY["code_feedback"],
    "progress_monitor": AGENT_CAPABILITY_REGISTRY["progress_monitor"],
}

def get_agent(name: str, mode: str = "default", llm_config: Optional[dict] = None):
    """
    Dynamically load the agent class based on name and execution mode.
    Mode can be:
      - "default": returns the base agent class instance
      - "crewai": returns CrewAI-compatible agent
      - "autogen": returns AutoGen-compatible agent (requires llm_config)
    """
    registry = AGENT_CAPABILITY_REGISTRY
    if name not in registry:
        raise ValueError(f"Agent '{name}' not found in registry.")

    agent_class = registry[name]["agent_class"]
    agent_instance = agent_class()

    if mode == "default":
        return agent_instance
    elif mode == "crewai":
        return agent_instance.to_crewai()
    elif mode == "autogen":
        return agent_instance.to_autogen(llm_config=llm_config)

    raise ValueError(f"Unsupported agent mode: {mode}")