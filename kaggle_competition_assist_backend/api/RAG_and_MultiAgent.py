from flask import Blueprint, jsonify, request
from RAG_pipeline.rag_pipeline import HaystackRAGPipeline
from orchestrators.expert_orchestrator_langgraph import ExpertOrchestratorLangGraph
from orchestrators.orchestrator_base import BaseOrchestratorUtils 
from orchestrators.reasoning_orchestrator import ReasoningOrchestrator
from time import time
from evaluation.guideline_evaluator import evaluate_response

RAG_pipe_bp = Blueprint("rag_pipeline", __name__, url_prefix="/rag")
multiAgent_bp = Blueprint("multi_agent", __name__, url_prefix="/multi-agent")
@RAG_pipe_bp.route("/", methods=["POST"])
def run_rag_pipeline():
    data = request.get_json()
    query = data.get("query", "")
    
    # Initialize the RAG pipeline
    rag_pipeline = HaystackRAGPipeline()
    
    # Run the RAG pipeline with the provided query
    response = rag_pipeline.run(query)
    
    return jsonify(response), 200

@multiAgent_bp.route("/", methods=["POST"])
def run_multi_agent():
    data = request.get_json()
    query = data.get("query", "")
    query_type = data.get("query_type", "")  # Optional flag or intent classifier output

    start_time = time()

    # Route to the appropriate orchestrator
    if query_type == "reasoning":
        orchestrator = ReasoningOrchestrator()
    elif query_type == "expert":
        orchestrator = ExpertOrchestratorLangGraph()
    else:
        orchestrator = BaseOrchestratorUtils()

    response = orchestrator.run(query)

    end_time = time()
    duration = end_time - start_time

    # Determine if reasoning orchestrator was used
    used_reasoning = isinstance(orchestrator, ReasoningOrchestrator)

    # Evaluate the response (optional: pass more context if needed)
    score, matched_guideline = evaluate_response(response, query_type)

    # Final response packaging
    final_output = {
        "query": query,
        "response": response if isinstance(response, dict) else {"text": response},
        "used_reasoning": used_reasoning,
        "duration_seconds": round(duration, 2),
        "evaluation_score": score,
        "matched_guideline": matched_guideline
    }

    return jsonify(final_output), 200