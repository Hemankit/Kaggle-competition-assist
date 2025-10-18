from agents import (
    CompetitionSummaryAgent,
    TimelineCoachAgent,
    NotebookExplainerAgent,
    DiscussionHelperAgent,
    MultiHopReasoningAgent,
    ErrorDiagnosisAgent,
    CodeFeedbackAgent,
    ProgressMonitorAgent,
    IdeaInitiatorAgent,
    CommunityEngagementAgent,
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
        "capabilities": ["planning", "milestones", "deadline_tracking", "structuring_information"],
        "reasoning_styles": ["timeline", "project_management"],
        "tags": ["calendar", "schedule", "planning"],
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
        "capabilities": ["track_progress", "benchmarking", "suggest_next_steps", "progress", "performance", "status"],
        "reasoning_styles": ["progressive", "timeline_based"],
        "tags": ["planning", "feedback", "monitoring", "progress", "performance"],
    },
    "multi_hop_reasoning": {
        "agent_class": MultiHopReasoningAgent,
        "capabilities": ["multihop_reasoning", "graph_reasoning", "complex_logic", "metrics", "ranking"],
        "reasoning_styles": ["stepwise", "chained", "contrastive"],
        "tags": ["graph", "advanced", "multiagent", "reasoning"],
    },
    "error_diagnosis": {
        "agent_class": ErrorDiagnosisAgent,
        "capabilities": ["error_detection", "bug_explanation", "log_analysis"],
        "reasoning_styles": ["diagnostic", "stepwise"],
        "tags": ["debugging", "errors"],
    },
    "idea_initiator": {
        "agent_class": IdeaInitiatorAgent,
        "capabilities": ["idea_generation", "strategy_recommendation", "approach_suggestion", "project_ideas", "recommendations", "beginner_friendly", "getting_started", "performance_tuning", "strategy_guidance"],
        "reasoning_styles": ["strategic", "creative", "analytical"],
        "tags": ["brainstorming", "starter", "ideas", "strategy", "recommendations"],
    },
    "community_engagement": {
        "agent_class": CommunityEngagementAgent,
        "capabilities": ["track_engagement", "analyze_feedback", "extract_insights", "prioritize_suggestions", "update_strategy"],
        "reasoning_styles": ["analytical", "strategic", "synthesis"],
        "tags": ["community", "discussions", "feedback", "crowd_wisdom", "engagement"],
    },
}

# === Registry for CrewAI (Autogen-style multi-agent reasoning orchestration) === #
AUTOGEN_AGENT_REGISTRY = {
    # ✅ FIX: Only include agents designed for reasoning/interaction orchestration
    # RAG agents (discussion_helper, notebook_explainer) are single-agent handlers, not orchestrated
    "progress_monitor": AGENT_CAPABILITY_REGISTRY["progress_monitor"],
    "multi_hop_reasoning": AGENT_CAPABILITY_REGISTRY["multi_hop_reasoning"],
    "error_diagnosis": AGENT_CAPABILITY_REGISTRY["error_diagnosis"],
    "code_feedback": AGENT_CAPABILITY_REGISTRY["code_feedback"],
    "idea_initiator": AGENT_CAPABILITY_REGISTRY["idea_initiator"],
    "community_engagement": AGENT_CAPABILITY_REGISTRY["community_engagement"],
    "timeline_coach": AGENT_CAPABILITY_REGISTRY["timeline_coach"],
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