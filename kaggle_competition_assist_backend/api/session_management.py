"""Session management API for user initialization and competition data fetching."""

from flask import Blueprint, request, jsonify
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from Kaggle_Fetcher.kaggle_api_client import (
        get_notebooks_info,
        get_leaderboard_info,
        get_total_notebooks_count
    )
    from kaggle_competition_assist_backend.utils.logging_config import get_request_logger, log_request
except ImportError as e:
    print(f"Import error in session_management: {e}")
    # Fallback - create dummy functions
    def get_request_logger():
        import logging
        return logging.getLogger(__name__)
    def log_request(func):
        return func
    # Dummy functions for when Kaggle_Fetcher is not available
    def get_notebooks_info(*args, **kwargs):
        return []
    def get_leaderboard_info(*args, **kwargs):
        return []
    def get_total_notebooks_count(*args, **kwargs):
        return 0

session_bp = Blueprint("session_management", __name__, url_prefix="/session")

# In-memory session store (in production, use Redis or database)
user_sessions = {}

def validate_competition_slug(competition_slug: str) -> bool:
    """Validate if competition slug exists and is accessible."""
    try:
        # Try to fetch basic competition info
        total_notebooks = get_total_notebooks_count(competition_slug)
        return total_notebooks >= 0  # Even 0 is valid (no notebooks yet)
    except Exception as e:
        get_request_logger().error(f"Competition validation failed: {e}")
        return False

def fetch_competition_context(competition_slug: str) -> Dict:
    """Fetch minimal competition context for session initialization (no heavy data fetching)."""
    logger = get_request_logger()
    
    context = {
        "competition_slug": competition_slug,
        "fetched_at": datetime.now().isoformat(),
        "total_notebooks": 0,
        "competition_accessible": False,
        "error": None
    }
    
    try:
        # Only validate competition exists and get basic count - no heavy fetching
        total_notebooks = get_total_notebooks_count(competition_slug)
        context["total_notebooks"] = total_notebooks
        context["competition_accessible"] = True
        
        logger.info(f"Competition validation successful for: {competition_slug}")
        
    except Exception as e:
        error_msg = f"Error validating competition: {e}"
        logger.error(error_msg)
        context["error"] = error_msg
        context["competition_accessible"] = False
    
    return context

@session_bp.route("/initialize", methods=["POST"])
@log_request
def initialize_session():
    """Initialize a new user session with Kaggle username and competition."""
    logger = get_request_logger()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        kaggle_username = data.get("kaggle_username", "").strip()
        competition_slug = data.get("competition_slug", "").strip()
        
        if not kaggle_username or not competition_slug:
            return jsonify({
                "error": "Both kaggle_username and competition_slug are required"
            }), 400
        
        # Validate competition exists
        if not validate_competition_slug(competition_slug):
            return jsonify({
                "error": f"Competition '{competition_slug}' not found or not accessible"
            }), 400
        
        # Generate session ID
        session_id = f"{kaggle_username}_{competition_slug}_{int(datetime.now().timestamp())}"
        
        # Validate competition and get minimal context
        logger.info(f"Validating competition: {competition_slug}")
        competition_context = fetch_competition_context(competition_slug)
        
        # Create session
        session_data = {
            "session_id": session_id,
            "kaggle_username": kaggle_username,
            "competition_slug": competition_slug,
            "created_at": datetime.now().isoformat(),
            "competition_context": competition_context,
            "query_history": [],
            "active": True
        }
        
        user_sessions[session_id] = session_data
        
        logger.info(f"Session initialized: {session_id}")
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": f"Session initialized for {kaggle_username} on competition {competition_slug}",
            "competition_summary": {
                "slug": competition_slug,
                "total_notebooks": competition_context["total_notebooks"],
                "accessible": competition_context["competition_accessible"]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Session initialization failed: {e}")
        return jsonify({
            "error": f"Session initialization failed: {str(e)}"
        }), 500

@session_bp.route("/status/<session_id>", methods=["GET"])
@log_request
def get_session_status(session_id: str):
    """Get current session status and context."""
    logger = get_request_logger()
    
    if session_id not in user_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session_data = user_sessions[session_id]
    
    return jsonify({
        "session_id": session_id,
        "kaggle_username": session_data["kaggle_username"],
        "competition_slug": session_data["competition_slug"],
        "created_at": session_data["created_at"],
        "active": session_data["active"],
        "query_count": len(session_data["query_history"]),
        "competition_summary": {
            "slug": session_data["competition_slug"],
            "total_notebooks": session_data["competition_context"]["total_notebooks"],
            "leaderboard_entries": len(session_data["competition_context"]["leaderboard"]),
            "notebooks_fetched": len(session_data["competition_context"]["notebooks"])
        }
    }), 200

@session_bp.route("/competitions/search", methods=["POST"])
@log_request
def search_competitions():
    """Search for competitions by name or slug."""
    logger = get_request_logger()
    
    try:
        data = request.get_json()
        query = data.get("query", "").strip().lower()
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        # This is a simplified search - in production, you'd want to implement
        # a proper search against Kaggle's competition list
        # For now, we'll return some common competition patterns
        
        common_competitions = [
            {"slug": "titanic", "name": "Titanic - Machine Learning from Disaster"},
            {"slug": "house-prices-advanced-regression-techniques", "name": "House Prices: Advanced Regression Techniques"},
            {"slug": "digit-recognizer", "name": "Digit Recognizer"},
            {"slug": "nlp-getting-started", "name": "Natural Language Processing with Disaster Tweets"},
            {"slug": "spaceship-titanic", "name": "Spaceship Titanic"},
            {"slug": "playground-series-s3e1", "name": "Playground Series - Season 3, Episode 1"},
            {"slug": "tabular-playground-series-jan-2022", "name": "Tabular Playground Series - Jan 2022"},
        ]
        
        # Filter competitions based on query
        matching_competitions = [
            comp for comp in common_competitions
            if query in comp["name"].lower() or query in comp["slug"].lower()
        ]
        
        return jsonify({
            "success": True,
            "query": query,
            "competitions": matching_competitions,
            "total_found": len(matching_competitions)
        }), 200
        
    except Exception as e:
        logger.error(f"Competition search failed: {e}")
        return jsonify({
            "error": f"Competition search failed: {str(e)}"
        }), 500

@session_bp.route("/fetch-data", methods=["POST"])
@log_request
def fetch_competition_data():
    """Fetch competition data on-demand based on user query (aligned with architecture)."""
    logger = get_request_logger()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        session_id = data.get("session_id")
        user_query = data.get("query", "").strip()
        sections = data.get("sections", [])  # Specific sections requested
        
        if not session_id or session_id not in user_sessions:
            return jsonify({"error": "Invalid or missing session ID"}), 404
        
        if not user_query:
            return jsonify({"error": "User query is required"}), 400
        
        session_data = user_sessions[session_id]
        competition_slug = session_data["competition_slug"]
        
        logger.info(f"Fetching data for query: '{user_query}' in sections: {sections}")
        
        # Use the existing hybrid scraping architecture
        try:
            from hybrid_scraping_routing.agent_router import HybridScrapingAgent
            from query_processing.user_input_processor import UserInputProcessor
            
            # Process the query to determine what data is needed
            processor = UserInputProcessor()
            structured_query = processor.structure_query(user_query)
            
            # Initialize hybrid scraping agent
            hybrid_agent = HybridScrapingAgent(llm=None)  # Will be injected by the multi-agent system
            
            # Fetch data based on query analysis
            fetch_results = []
            
            # If specific sections requested, fetch only those
            if sections:
                for section in sections:
                    result = hybrid_agent.run({
                        "query": user_query,
                        "section": section,
                        "predicted_section": section
                    })
                    fetch_results.extend(result)
            else:
                # Use the predicted section from query processing
                predicted_section = structured_query.get("section", "overview")
                result = hybrid_agent.run({
                    "query": user_query,
                    "section": predicted_section,
                    "predicted_section": predicted_section
                })
                fetch_results.extend(result)
            
            # Update session with fetched data
            if "fetched_data" not in session_data:
                session_data["fetched_data"] = []
            
            session_data["fetched_data"].append({
                "query": user_query,
                "sections": sections,
                "results": fetch_results,
                "timestamp": datetime.now().isoformat()
            })
            
            return jsonify({
                "success": True,
                "query": user_query,
                "sections_processed": sections or [structured_query.get("section", "overview")],
                "results_count": len(fetch_results),
                "data": fetch_results
            }), 200
            
        except ImportError as e:
            logger.warning(f"Hybrid scraping components not available: {e}")
            return jsonify({
                "success": False,
                "message": "On-demand data fetching not available - using session validation only",
                "query": user_query
            }), 200
            
    except Exception as e:
        logger.error(f"Data fetching failed: {e}")
        return jsonify({
            "error": f"Data fetching failed: {str(e)}"
        }), 500

@session_bp.route("/context/<session_id>", methods=["GET"])
@log_request
def get_competition_context(session_id: str):
    """Get session context (minimal data only)."""
    logger = get_request_logger()
    
    if session_id not in user_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session_data = user_sessions[session_id]
    
    return jsonify({
        "session_id": session_id,
        "competition_context": session_data["competition_context"],
        "fetched_data_count": len(session_data.get("fetched_data", []))
    }), 200
