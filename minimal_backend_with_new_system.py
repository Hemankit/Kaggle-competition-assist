#!/usr/bin/env python3
"""
Minimal Backend with New Multi-Agent System
Complete implementation with all endpoints
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add current directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Environment variables loaded from .env file")
except ImportError:
    print("[WARN] python-dotenv not available, using system environment variables")

# Import Kaggle API
try:
    from Kaggle_Fetcher.kaggle_api_client import KaggleAPIClient
    kaggle_client = KaggleAPIClient()
    KAGGLE_API_AVAILABLE = True
    print("[OK] Kaggle API loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: Kaggle API not available: {e}")
    KAGGLE_API_AVAILABLE = False
    kaggle_client = None

# Import NEW Multi-Agent System
try:
    print(f"[DEBUG] Current working directory: {os.getcwd()}")
    print(f"[DEBUG] Project root: {project_root}")
    print(f"[DEBUG] Python path: {sys.path[:3]}")
    from master_orchestrator import MasterOrchestrator
    NEW_SYSTEM_AVAILABLE = True
    print("[OK] New Multi-Agent System loaded successfully")
except ImportError as e:
    print(f"[WARN] New Multi-Agent System not available: {e}")
    print(f"[DEBUG] Available files in current directory: {os.listdir('.')}")
    NEW_SYSTEM_AVAILABLE = False

# Import OLD Multi-Agent System (for backward compatibility)
try:
    from orchestrators.expert_orchestrator_langgraph import ExpertSystemOrchestratorLangGraph
    from orchestrators.component_orchestrator import ComponentOrchestrator
    OLD_MULTIAGENT_AVAILABLE = True
    print("[OK] Old Multi-Agent System loaded successfully")
except ImportError as e:
    print(f"[WARN] Old Multi-Agent System not available: {e}")
    OLD_MULTIAGENT_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================================
# GLOBAL VARIABLES AND INITIALIZATION
# ===================================

# Initialize new multi-agent system
master_orchestrator = None
if NEW_SYSTEM_AVAILABLE:
    try:
        master_orchestrator = MasterOrchestrator()
        print("[OK] New Multi-Agent System initialized successfully")
    except Exception as e:
        print(f"[WARN] Failed to initialize new system: {e}")
        print(f"[DEBUG] Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        master_orchestrator = None

# Initialize old multi-agent system (for backward compatibility)
old_orchestrator = None
if OLD_MULTIAGENT_AVAILABLE:
    try:
        old_orchestrator = ComponentOrchestrator()
        print("[OK] Old Multi-Agent System initialized successfully")
    except Exception as e:
        print(f"[WARN] Failed to initialize old system: {e}")
        old_orchestrator = None

# Session storage (in-memory for simplicity)
sessions = {}

# ===================================
# HEALTH CHECK ENDPOINTS
# ===================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Test if new system is actually functional
    new_system_functional = False
    if NEW_SYSTEM_AVAILABLE and master_orchestrator is not None:
        try:
            # Test if the orchestrator can process a simple query
            test_result = master_orchestrator.run("test", {}, mode="auto")
            new_system_functional = test_result is not None
        except Exception as e:
            print(f"[DEBUG] New system test failed: {e}")
            new_system_functional = False
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "new_system_available": new_system_functional,
        "old_system_available": OLD_MULTIAGENT_AVAILABLE and old_orchestrator is not None,
        "kaggle_api_available": KAGGLE_API_AVAILABLE
    })

# ===================================
# NEW MULTI-AGENT SYSTEM ENDPOINTS
# ===================================

@app.route('/api/v2/query', methods=['POST'])
def process_query_v2():
    """Process query using the new multi-agent system."""
    try:
        if not NEW_SYSTEM_AVAILABLE or not master_orchestrator:
            return jsonify({"error": "New multi-agent system not available"}), 503
        
        data = request.get_json()
        query = data.get('query', '')
        context = data.get('context', {})
        mode = data.get('mode', 'auto')  # auto, crewai, autogen, langgraph, dynamic
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        logger.info(f"Processing query with new system: {query}")
        
        # Process with new system
        result = master_orchestrator.run(query, context, mode)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing query with new system: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/v2/status', methods=['GET'])
def get_system_status_v2():
    """Get new system status."""
    if not NEW_SYSTEM_AVAILABLE or not master_orchestrator:
        return jsonify({"error": "New multi-agent system not available"}), 503
    
    try:
        # Get system status from master orchestrator
        status = {
            "execution_history": {
                "recent_queries": master_orchestrator.execution_history[-5:] if hasattr(master_orchestrator, 'execution_history') else [],
                "total_queries": master_orchestrator.performance_metrics.get('total_queries', 0) if hasattr(master_orchestrator, 'performance_metrics') else 0
            },
            "hybrid_router": {
                "available": True,
                "status": "operational"
            },
            "orchestrators": {
                "available": list(master_orchestrator.orchestrators.keys()) if hasattr(master_orchestrator, 'orchestrators') else [],
                "status": "operational"
            },
            "external_search": {
                "available": True,
                "status": "operational"
            }
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": f"Error getting system status: {str(e)}"}), 500

@app.route('/api/v2/modes', methods=['GET'])
def get_available_modes_v2():
    """Get available orchestration modes."""
    if not NEW_SYSTEM_AVAILABLE or not master_orchestrator:
        return jsonify({"error": "New multi-agent system not available"}), 503
    
    try:
        modes = {
            "available_modes": list(master_orchestrator.orchestrators.keys()) if hasattr(master_orchestrator, 'orchestrators') else [],
            "default_mode": "auto",
            "mode_descriptions": {
                "auto": "Automatically select the best orchestrator",
                "crewai": "CrewAI-based multi-agent orchestration",
                "autogen": "AutoGen-based multi-agent orchestration", 
                "langgraph": "LangGraph-based multi-agent orchestration",
                "dynamic": "Dynamic multi-agent orchestration"
            }
        }
        return jsonify(modes)
    except Exception as e:
        return jsonify({"error": f"Error getting available modes: {str(e)}"}), 500

# ===================================
# LEGACY ENDPOINTS (for backward compatibility)
# ===================================

@app.route('/api/query', methods=['POST'])
def process_query_legacy():
    """Legacy query endpoint - uses old system or falls back to new system."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_context = data.get('user_context', {})
        mode = data.get('mode', 'langgraph')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        logger.info(f"Processing query with legacy system: {query}")
        
        # Try new system first if available
        if NEW_SYSTEM_AVAILABLE and master_orchestrator:
            try:
                result = master_orchestrator.run(query, user_context, mode)
                return jsonify(result)
            except Exception as e:
                logger.warning(f"New system failed, falling back to old system: {e}")
        
        # Fall back to old system
        if OLD_MULTIAGENT_AVAILABLE and old_orchestrator:
            result = old_orchestrator.process_query(query, user_context, mode)
            return jsonify(result)
        else:
            return jsonify({"error": "No multi-agent system available"}), 503
            
    except Exception as e:
        logger.error(f"Error processing query with legacy system: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# ===================================
# KAGGLE API ENDPOINTS
# ===================================

@app.route('/api/kaggle/competitions', methods=['GET'])
def search_competitions():
    """Search Kaggle competitions."""
    if not KAGGLE_API_AVAILABLE:
        return jsonify({"error": "Kaggle API not available"}), 503
    
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        competitions = kaggle_client.search_competitions(query)
        return jsonify({"competitions": competitions})
    except Exception as e:
        return jsonify({"error": f"Error searching competitions: {str(e)}"}), 500

@app.route('/api/kaggle/competitions/<competition_id>', methods=['GET'])
def get_competition_details(competition_id):
    """Get competition details."""
    if not KAGGLE_API_AVAILABLE:
        return jsonify({"error": "Kaggle API not available"}), 503
    
    try:
        details = kaggle_client.get_competition_details(competition_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": f"Error getting competition details: {str(e)}"}), 500

@app.route('/api/kaggle/competitions/<competition_id>/notebooks/count', methods=['GET'])
def get_notebooks_count(competition_id):
    """Get total notebooks count for a competition."""
    if not KAGGLE_API_AVAILABLE:
        return jsonify({"error": "Kaggle API not available"}), 503
    
    try:
        count = kaggle_client.get_notebooks_count(competition_id)
        return jsonify({"count": count})
    except Exception as e:
        return jsonify({"error": f"Error getting notebooks count: {str(e)}"}), 500

@app.route('/api/kaggle/competitions/<competition_id>/data', methods=['GET'])
def get_competition_data_files(competition_id):
    """Get competition data files."""
    if not KAGGLE_API_AVAILABLE:
        return jsonify({"error": "Kaggle API not available"}), 503
    
    try:
        files = kaggle_client.get_competition_data_files(competition_id)
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": f"Error getting competition data files: {str(e)}"}), 500

@app.route('/api/kaggle/users/<username>/submissions', methods=['GET'])
def get_user_submissions(username):
    """Get user submissions."""
    if not KAGGLE_API_AVAILABLE:
        return jsonify({"error": "Kaggle API not available"}), 503
    
    try:
        submissions = kaggle_client.get_user_submissions(username)
        return jsonify({"submissions": submissions})
    except Exception as e:
        return jsonify({"error": f"Error getting user submissions: {str(e)}"}), 500

@app.route('/api/kaggle/users/<username>/progress', methods=['GET'])
def get_user_progress(username):
    """Get user progress summary."""
    if not KAGGLE_API_AVAILABLE:
        return jsonify({"error": "Kaggle API not available"}), 503
    
    try:
        progress = kaggle_client.get_user_progress(username)
        return jsonify(progress)
    except Exception as e:
        return jsonify({"error": f"Error getting user progress: {str(e)}"}), 500

# ===================================
# SESSION MANAGEMENT ENDPOINTS
# ===================================

@app.route('/session/create', methods=['POST'])
def create_session():
    """Create a new session."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'id': session_id,
        'created_at': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat(),
        'queries': []
    }
    return jsonify({'session_id': session_id})

@app.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details."""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    
    session = sessions[session_id]
    session['last_activity'] = datetime.now().isoformat()
    return jsonify(session)

@app.route('/session/<session_id>/query', methods=['POST'])
def add_query_to_session(session_id):
    """Add a query to a session."""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Add query to session
    sessions[session_id]['queries'].append({
        'query': query,
        'timestamp': datetime.now().isoformat()
    })
    sessions[session_id]['last_activity'] = datetime.now().isoformat()
    
    return jsonify({"message": "Query added to session"})

@app.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session."""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404
    
    del sessions[session_id]
    return jsonify({"message": "Session deleted"})

@app.route('/session/competitions/search', methods=['POST'])
def search_competitions_session():
    """Search for competitions using the new multi-agent system"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Use the new system to search competitions
        context = {'search_type': 'competitions'}
        result = master_orchestrator.run(query, context)
        
        return jsonify({
            'competitions': result.get('result', []),
            'success': result.get('success', False),
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error searching competitions: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/session/initialize', methods=['POST'])
def initialize_session():
    """Initialize a session with user and competition info using new multi-agent system."""
    try:
        data = request.get_json()
        kaggle_username = data.get('kaggle_username')
        competition_slug = data.get('competition_slug')
        
        if not kaggle_username or not competition_slug:
            return jsonify({"error": "kaggle_username and competition_slug are required"}), 400
        
        # Use the new multi-agent system to initialize session
        if NEW_SYSTEM_AVAILABLE and master_orchestrator:
            try:
                # Create a query to initialize the session
                query = f"Initialize session for user {kaggle_username} with competition {competition_slug}"
                context = {
                    "section": "session_init",
                    "kaggle_username": kaggle_username,
                    "competition_slug": competition_slug
                }
                
                # Process the initialization query
                result = master_orchestrator.run(query, context, mode="dynamic")
                
                if result.get("success"):
                    session_id = str(uuid.uuid4())
                    sessions[session_id] = {
                        'id': session_id,
                        'created_at': datetime.now().isoformat(),
                        'last_activity': datetime.now().isoformat(),
                        'kaggle_username': kaggle_username,
                        'competition_slug': competition_slug,
                        'queries': [],
                        'initialized': True
                    }
                    
                    return jsonify({
                        "success": True,
                        "session_id": session_id,
                        "message": "Session initialized successfully with new multi-agent system",
                        "data": result.get("data", {})
                    })
                else:
                    return jsonify({"error": result.get("error", "Session initialization failed")}), 500
                    
            except Exception as e:
                return jsonify({"error": f"New system error: {str(e)}"}), 500
        else:
            return jsonify({"error": "New multi-agent system not available"}), 503
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ===================================
# DEBUG ENDPOINTS (SIMPLIFIED)
# ===================================

@app.route('/debug/status', methods=['GET'])
def debug_status():
    """Debug status endpoint."""
    return jsonify({
        "new_system_available": NEW_SYSTEM_AVAILABLE,
        "old_system_available": OLD_MULTIAGENT_AVAILABLE,
        "kaggle_api_available": KAGGLE_API_AVAILABLE,
        "master_orchestrator_initialized": master_orchestrator is not None,
        "old_orchestrator_initialized": old_orchestrator is not None,
        "active_sessions": len(sessions),
        "timestamp": datetime.now().isoformat()
    })

# ===================================
# MAIN APPLICATION
# ===================================

if __name__ == '__main__':
    print("[START] Starting Flask Backend with New Multi-Agent System...")
    print("[INFO] Health check: /health")
    print("[INFO] New system query: /api/v2/query")
    print("[INFO] Legacy query: /api/query")
    print("[INFO] System status: /api/v2/status")
    print("[INFO] Available modes: /api/v2/modes")
    print("[INFO] Debug status: /debug/status")
    print("[INFO] Backend will be available at: http://localhost:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=False)