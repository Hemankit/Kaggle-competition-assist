from flask import Blueprint, jsonify, request
from RAG_pipeline.rag_pipeline import HaystackRAGPipeline
from orchestrators.expert_orchestrator_langgraph import ExpertOrchestratorLangGraph
from orchestrators.orchestrator_base import BaseOrchestratorUtils 
from orchestrators.reasoning_orchestrator import ReasoningOrchestrator

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
    query_type = data.get("query_type", "")  # You could use an intent classifier here

    # Example routing logic
    if query_type == "reasoning":
        orchestrator = ReasoningOrchestrator()
        response = orchestrator.run(query)
    elif query_type == "expert":
        orchestrator = ExpertOrchestratorLangGraph()
        response = orchestrator.run(query)
    else:  # Default to base orchestrator or retrieval
        orchestrator = BaseOrchestratorUtils()
        response = orchestrator.run(query)

    return jsonify(response), 200

