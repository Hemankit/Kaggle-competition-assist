#!/usr/bin/env python3
"""
Simple test backend for the new multi-agent system.
This bypasses the old orchestrator and tests our new system directly.
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our new system
from master_orchestrator import MasterOrchestrator

app = Flask(__name__)
CORS(app)

# Initialize our new system
print("Initializing new multi-agent system...")
try:
    master_orchestrator = MasterOrchestrator()
    print("✅ New system initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing new system: {e}")
    master_orchestrator = None

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "new_system_available": master_orchestrator is not None
    })

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a query using the new multi-agent system."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        context = data.get('context', {})
        mode = data.get('mode', 'auto')  # auto, crewai, autogen, langgraph, dynamic
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        if not master_orchestrator:
            return jsonify({"error": "New system not available"}), 500
        
        print(f"\n=== Processing Query ===")
        print(f"Query: {query}")
        print(f"Context: {context}")
        print(f"Mode: {mode}")
        
        # Process with new system
        result = master_orchestrator.process_query(query, context, mode)
        
        print(f"Result keys: {list(result.keys())}")
        print(f"Success: {result.get('success', False)}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    if not master_orchestrator:
        return jsonify({"error": "New system not available"}), 500
    
    status = master_orchestrator.get_system_status()
    return jsonify(status)

@app.route('/api/modes', methods=['GET'])
def get_modes():
    """Get available orchestration modes."""
    if not master_orchestrator:
        return jsonify({"error": "New system not available"}), 500
    
    return jsonify({
        "available_modes": master_orchestrator.get_available_modes(),
        "default_mode": "auto"
    })

if __name__ == '__main__':
    print("\n=== Starting New System Test Backend ===")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /api/query - Process query")
    print("  GET  /api/status - System status")
    print("  GET  /api/modes - Available modes")
    print("\nStarting server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)









