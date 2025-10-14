from flask import Blueprint, request, jsonify
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from orchestrators.component_orchestrator import ComponentOrchestrator
    from kaggle_competition_assist_backend.utils.logging_config import get_request_logger, log_request
except ImportError as e:
    print(f"Import error in component_orchestration: {e}")
    # Fallback - create dummy functions
    def get_request_logger():
        import logging
        return logging.getLogger(__name__)
    def log_request(func):
        return func
    from orchestrators.component_orchestrator import ComponentOrchestrator

component_orch = ComponentOrchestrator()
component_bp = Blueprint("component_orchestrator", __name__, url_prefix="/component-orchestrator")

@component_bp.route("/query", methods=["POST"])
@log_request
def handle_query():
    data = request.get_json()
    query = data.get("query", "")
    debug = data.get("debug", False)  # Optional for dev use

    logger = get_request_logger()
    
    if not query:
        logger.warning("Query endpoint called without query parameter")
        return jsonify({"error": "No query provided."}), 400

    try:
        logger.info(f"Processing query: {query[:100]}...")  # Log first 100 chars
        
        if debug:
            logger.info("Debug mode enabled")
            result = component_orch.run_with_debug(query)
            logger.info("Debug query completed successfully")
            return jsonify(result)
        else:
            final_response = component_orch.run(query)
            logger.info("Query processed successfully")
            return jsonify({"final_response": final_response})
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return jsonify({"error": str(e)}), 500