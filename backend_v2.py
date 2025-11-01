#!/usr/bin/env python3
"""
Backend V2.0 - Flask Backend with MasterOrchestrator Integration
"""
from flask import Flask, Blueprint, jsonify, request, send_file
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import sys
import io

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Environment variables loaded from .env file")
except ImportError:
    print("[WARN] python-dotenv not installed, using system environment variables")

# Set Kaggle credentials from environment variables
os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME', '')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY', '')

# Import Kaggle API functions
try:
    from Kaggle_Fetcher.kaggle_api_client import (
        search_kaggle_competitions as api_search_competitions,
        get_competition_details as api_get_competition_details,
        get_total_notebooks_count as api_get_notebooks_count,
        get_competition_data_files as api_get_data_files,
        get_user_submissions as api_get_user_submissions,
        get_user_progress_summary as api_get_user_progress_summary
    )
    KAGGLE_API_AVAILABLE = True
    print("[OK] Kaggle API integration loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: Kaggle API not available: {e}")
    KAGGLE_API_AVAILABLE = False

# Import V2.0 Multi-Agent System Components
try:
    from orchestrators.component_orchestrator import ComponentOrchestrator
    from unified_intelligence_layer import UnifiedIntelligenceLayer
    from hybrid_agent_router import HybridAgentRouter
    V2_ORCHESTRATION_AVAILABLE = True
    print("[OK] V2.0 Orchestration components loaded successfully")
    print("[OK]   - ComponentOrchestrator (CrewAI, AutoGen, LangGraph, Dynamic modes)")
    print("[OK]   - UnifiedIntelligenceLayer")
    print("[OK]   - HybridAgentRouter")
except ImportError as e:
    print(f"[WARN] Warning: V2.0 Orchestration not available: {e}")
    import traceback
    traceback.print_exc()
    V2_ORCHESTRATION_AVAILABLE = False

# Import Guideline Evaluator for response validation
try:
    from evaluation.guideline_evaluator import enrich_response_with_guidelines, evaluate_response
    GUIDELINE_EVALUATION_AVAILABLE = True
    print("[OK] Guideline evaluator loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: Guideline evaluator not available: {e}")
    GUIDELINE_EVALUATION_AVAILABLE = False

# Import Scraping System (Core - REQUIRED)
try:
    from scraper.overview_scraper import OverviewScraper
    from scraper.notebook_api_fetcher import NotebookAPIFetcher
    from scraper.discussion_scraper_playwright import DiscussionScraperPlaywright
    SCRAPING_AVAILABLE = True
    print("[OK] Core scraping system loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: Core scraping system not available: {e}")
    SCRAPING_AVAILABLE = False

# Import V2.0 Hybrid Scraping Agent (Intelligent Routing)
try:
    from hybrid_scraping_routing.agent_router import HybridScrapingAgent
    from query_processing.user_input_processor import UserInputProcessor
    HYBRID_SCRAPING_AVAILABLE = True
    print("[OK] V2.0 Hybrid Scraping Agent loaded (intelligent routing)")
except ImportError as e:
    print(f"[WARN] V2.0 Hybrid Scraping Agent not available: {e}")
    HYBRID_SCRAPING_AVAILABLE = False

# Import Agents and LLM
try:
    from agents import (
        CompetitionSummaryAgent, NotebookExplainerAgent, DiscussionHelperAgent, 
        CommunityEngagementAgent, ProgressMonitorAgent, TimelineCoachAgent,
        MultiHopReasoningAgent, IdeaInitiatorAgent
    )
    from agents.data_section_agent import DataSectionAgent
    from agents.code_feedback_agent import CodeFeedbackAgent
    from agents.error_diagnosis_agent import ErrorDiagnosisAgent
    from llms.llm_loader import get_llm_from_config
    AGENT_AVAILABLE = True
    print("[OK] All 10 specialized agents loaded successfully")
    print("[OK] Code handling agents loaded successfully")
    print("[OK] Community engagement agent loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: Agent system not available: {e}")
    AGENT_AVAILABLE = False

# Import Data Fetcher
try:
    from Kaggle_Fetcher.data_fetcher import DataFetcher
    DATA_FETCHER_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Warning: Data Fetcher not available: {e}")
    DATA_FETCHER_AVAILABLE = False

# Import ChromaDB RAG Pipeline
try:
    from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
    CHROMADB_AVAILABLE = True
    print("[OK] ChromaDB RAG pipeline loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: ChromaDB not available: {e}")
    CHROMADB_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# In-memory store for active sessions
user_sessions = {}

# Initialize V2.0 Orchestration Components
component_orchestrator = None
unified_intelligence = None
hybrid_router = None

if V2_ORCHESTRATION_AVAILABLE:
    try:
        print("[INITIALIZING] V2.0 Orchestration System...")
        
        # Initialize ComponentOrchestrator (has all 4 modes)
        component_orchestrator = ComponentOrchestrator()
        print("[OK] ComponentOrchestrator initialized (CrewAI, AutoGen, LangGraph, Dynamic)")
        
        # Initialize Hybrid Agent Router FIRST (it initializes all agents)
        perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        hybrid_router = HybridAgentRouter(
            perplexity_api_key=perplexity_key,
            google_api_key=google_key
        )
        print("[OK] Hybrid Agent Router initialized")
        
        # Initialize Unified Intelligence Layer WITH hybrid_router (for agent access)
        from llms.llm_loader import get_llm_from_config
        routing_llm = get_llm_from_config("routing")
        unified_intelligence = UnifiedIntelligenceLayer(llm=routing_llm, hybrid_router=hybrid_router)
        print("[OK] Unified Intelligence Layer initialized")
        if perplexity_key:
            print("[OK]   - ExternalSearchAgent (Perplexity) configured")
        else:
            print("[WARN]   - Perplexity API key not found (external search may be limited)")
        
        print("[SUCCESS] V2.0 Orchestration System ready!")
        print("[INFO] Modes available: CrewAI, AutoGen, LangGraph, Dynamic")
    except Exception as e:
        print(f"[ERROR] Failed to initialize V2.0 Orchestration: {e}")
        import traceback
        traceback.print_exc()
        V2_ORCHESTRATION_AVAILABLE = False

# Initialize ChromaDB RAG Pipeline
chromadb_pipeline = None
if CHROMADB_AVAILABLE:
    try:
        chromadb_pipeline = ChromaDBRAGPipeline(
            collection_name="kaggle_competition_data",
            embedding_model="all-mpnet-base-v2"
        )
        print("[OK] ChromaDB pipeline initialized successfully")
    except Exception as e:
        print(f"[WARN] Failed to initialize ChromaDB pipeline: {e}")
        CHROMADB_AVAILABLE = False

# Initialize V2.0 Hybrid Scraping Agent (Intelligent Scraping Routing)
hybrid_scraping_agent = None
if HYBRID_SCRAPING_AVAILABLE:
    try:
        from llms.llm_loader import get_llm_from_config
        scraping_llm = get_llm_from_config("scraper_decision")
        hybrid_scraping_agent = HybridScrapingAgent(llm=scraping_llm)
        print("[OK] V2.0 Hybrid Scraping Agent initialized (intelligent routing)")
    except Exception as e:
        print(f"[WARN] Failed to initialize Hybrid Scraping Agent: {e}")
        HYBRID_SCRAPING_AVAILABLE = False

# Create session management blueprint
session_bp = Blueprint("session", __name__, url_prefix="/session")

def search_kaggle_competitions(query: str) -> list:
    """Search for Kaggle competitions using real API"""
    if not KAGGLE_API_AVAILABLE:
        # Fallback to mock data
        mock_competitions = [
            {
                "slug": "titanic",
                "name": "Titanic - Machine Learning from Disaster",
                "description": "Predict survival on the Titanic",
                "category": "Getting Started",
                "url": "https://www.kaggle.com/competitions/titanic"
            }
        ]
        return mock_competitions[:5]
    
    try:
        competitions = api_search_competitions(
            query=query,
            sort_by="latestDeadline",
            page=1,
            page_size=10
        )
        return competitions[:5]
    except Exception as e:
        print(f"[ERROR] Kaggle API search failed: {e}")
        return []

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "orchestrator": "V2_LangGraph" if V2_ORCHESTRATION_AVAILABLE else "None",
        "unified_intelligence": "active" if unified_intelligence else "inactive",
        "hybrid_router": "active" if hybrid_router else "inactive",
        "scraping": "HybridScrapingAgent_V2" if HYBRID_SCRAPING_AVAILABLE else "None",
        "chromadb": "available" if CHROMADB_AVAILABLE else "unavailable",
        "kaggle_api": "available" if KAGGLE_API_AVAILABLE else "unavailable",
        "timestamp": datetime.now().isoformat()
    }), 200

# ==================== SESSION MANAGEMENT ENDPOINTS ====================

@session_bp.route("/initialize", methods=["POST"])
def initialize_session():
    """Initialize a new user session with competition context"""
    try:
        data = request.get_json()
        kaggle_username = data.get("kaggle_username", "").strip()
        competition_slug = data.get("competition_slug", "").strip()
        
        if not kaggle_username or not competition_slug:
            return jsonify({
                "error": "Both kaggle_username and competition_slug are required"
            }), 400
        
        # Create session ID
        session_id = str(uuid.uuid4())
        
        # Fetch competition details
        competition_context = {}
        if KAGGLE_API_AVAILABLE:
            try:
                details = api_get_competition_details(competition_slug)
                total_notebooks = api_get_notebooks_count(competition_slug)
                
                competition_context = {
                    "competition_slug": competition_slug,
                    "competition_name": details.get('name', competition_slug),
                    "description": details.get('description', ''),
                    "total_notebooks": total_notebooks,
                    "competition_accessible": True
                }
            except Exception as e:
                print(f"[WARN] Failed to fetch competition details: {e}")
                competition_context = {
                    "competition_slug": competition_slug,
                    "competition_name": competition_slug,
                    "total_notebooks": 0,
                    "competition_accessible": False
                }
        
        # Store session
        user_sessions[session_id] = {
            "session_id": session_id,
            "kaggle_username": kaggle_username,
            "competition_slug": competition_slug,
            "competition_context": competition_context,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "fetched_data": []
        }
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "competition_context": competition_context
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to initialize session: {str(e)}"
        }), 500

@session_bp.route("/competitions/search", methods=["POST"])
def search_competitions():
    """Search for Kaggle competitions"""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        
        competitions = search_kaggle_competitions(query)
        
        return jsonify({
            "success": True,
            "competitions": competitions,
            "count": len(competitions)
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to search competitions: {str(e)}"
        }), 500

@session_bp.route("/status/<session_id>", methods=["GET"])
def get_session_status(session_id: str):
    """Get session status"""
    try:
        if session_id not in user_sessions:
            return jsonify({
                "error": "Session not found"
            }), 404
        
        session_data = user_sessions[session_id]
        return jsonify({
            "session_id": session_id,
            "kaggle_username": session_data["kaggle_username"],
            "competition_slug": session_data["competition_slug"],
            "created_at": session_data["created_at"],
            "last_activity": session_data["last_activity"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get session status: {str(e)}"
        }), 500

@session_bp.route("/context/<session_id>", methods=["GET"])
def get_competition_context(session_id: str):
    """Get competition context for session"""
    try:
        if session_id not in user_sessions:
            return jsonify({
                "error": "Session not found"
            }), 404
        
        session_data = user_sessions[session_id]
        return jsonify({
            "session_id": session_id,
            "competition_context": session_data["competition_context"],
            "fetched_data_count": len(session_data.get("fetched_data", []))
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get competition context: {str(e)}"
        }), 500

@session_bp.route("/fetch-data", methods=["POST"])
def fetch_competition_data():
    """
    V2.0 Fetch competition data using intelligent scraping routing
    Uses HybridScrapingAgent to decide optimal scraping strategy
    """
    try:
        data = request.get_json()
        session_id = data.get("session_id", "").strip()
        user_query = data.get("query", "").strip()
        
        if not session_id or session_id not in user_sessions:
            return jsonify({
                "error": "Invalid or missing session_id"
            }), 400
        
        if not user_query:
            return jsonify({
                "error": "Query is required"
            }), 400
        
        # Get competition context from session
        session_data = user_sessions[session_id]
        competition_slug = session_data.get("competition_slug", "")
        
        fetch_results = []
        
        # Use V2.0 Hybrid Scraping Agent if available
        if HYBRID_SCRAPING_AVAILABLE and hybrid_scraping_agent and competition_slug:
            try:
                print(f"[V2.0 SCRAPING] Using HybridScrapingAgent for: {user_query}")
                
                # Run intelligent scraping routing
                scraping_result = hybrid_scraping_agent.run(
                    query=user_query,
                    competition_slug=competition_slug
                )
                
                # Extract data from scraping result
                if scraping_result and isinstance(scraping_result, dict):
                    sections = scraping_result.get('sections', [])
                    for section in sections:
                        fetch_results.append({
                            "section": section.get('section_name', 'unknown'),
                            "content": section.get('content', ''),
                            "source": "hybrid_scraping_v2",
                            "scraping_method": section.get('method', 'intelligent'),
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    print(f"[V2.0 SCRAPING] Fetched {len(fetch_results)} sections")
                else:
                    print("[V2.0 SCRAPING] No data returned from HybridScrapingAgent")
                    
            except Exception as e:
                print(f"[WARN] Hybrid scraping failed, using fallback: {e}")
        
        # Fallback: Mock data if scraping unavailable or failed
        if not fetch_results:
            fetch_results = [
                {
                    "section": "overview",
                    "content": f"Data for query: {user_query} (scraping unavailable)",
                    "source": "fallback",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        
        # Update session
        user_sessions[session_id]["fetched_data"].extend(fetch_results)
        user_sessions[session_id]["last_activity"] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "query": user_query,
            "results_count": len(fetch_results),
            "data": fetch_results,
            "scraping_method": "v2_intelligent" if HYBRID_SCRAPING_AVAILABLE else "fallback"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch data: {str(e)}"
        }), 500

# Register session blueprint
app.register_blueprint(session_bp)

# ==================== V2.0 QUERY ENDPOINT ====================

@app.route("/component-orchestrator/query", methods=["POST"])
def handle_v2_query():
    """
    V2.0 Query Handler with Intelligent Multi-Mode Orchestration
    
    Flow:
    1. Unified Intelligence Layer analyzes query (complexity + category)
    2. Hybrid Agent Router selects optimal agents
    3. Decide orchestration mode based on complexity:
       - Simple (low complexity, 1 agent) → LangGraph (fast, 3-5s)
       - Complex (high complexity, 2-3 agents) → CrewAI/AutoGen (powerful)
       - Very complex → Dynamic mode (auto-select best framework)
    """
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        user_context = data.get("user_context", {})
        
        if not query:
            return jsonify({
                "error": "Query is required"
            }), 400
        
        # Extract context
        kaggle_username = user_context.get("kaggle_username", "unknown")
        competition_slug = user_context.get("competition_slug", "")
        session_id = user_context.get("session_id", "")
        
        print(f"\n[V2.0 QUERY] User: {kaggle_username}")
        print(f"[V2.0 QUERY] Competition: {competition_slug}")
        print(f"[V2.0 QUERY] Query: {query}")
        
        # Check if V2.0 Orchestration is available
        if not V2_ORCHESTRATION_AVAILABLE or not component_orchestrator:
            return jsonify({
                "error": "V2.0 Orchestration not available",
                "response": "I'm currently unavailable. Please try again later."
            }), 503
        
        # Build orchestrator context
        orchestrator_context = {
            "competition_slug": competition_slug,
            "competition_name": competition_slug,
            "kaggle_username": kaggle_username,
            "session_id": session_id,
            "user_level": user_context.get("user_level", "intermediate")
        }
        
        # Step 1: Use Unified Intelligence Layer to analyze query
        print("[V2.0 STEP 1] Analyzing query with Unified Intelligence Layer...")
        if unified_intelligence:
            query_analysis = unified_intelligence.analyze_query(query, orchestrator_context)
            complexity = query_analysis.get('complexity', 'medium')
            category = query_analysis.get('category', 'GENERAL')
            print(f"[V2.0] Complexity: {complexity}, Category: {category}")
        else:
            complexity = "medium"
            category = "GENERAL"
        
        # Step 2: Use Hybrid Router to select agents
        print("[V2.0 STEP 2] Selecting agents with Hybrid Router...")
        if hybrid_router:
            agent_routing = hybrid_router.route_agents(query, orchestrator_context)
            agents_to_use = agent_routing.get('selected_agents', [])
            num_agents = len(agents_to_use)
            print(f"[V2.0] HybridRouter selected {num_agents} agents: {agents_to_use}")
            
            # CRITICAL: CATEGORY-BASED ROUTING (handles 95% of queries correctly!)
            # 
            # Category determines agent selection strategy:
            # - RAG queries (overview, data, discussions, notebooks) → TOP 1 agent → Fast (3-5s)
            # - CODE queries (debug, review, feedback) → TOP 1 agent → Fast
            # - STRATEGY queries (planning, approach) → TOP 1-2 agents → Powerful
            # - HYBRID queries (RAG + reasoning) → Sequential RAG → Reasoning
            # 
            # Multi-agent ONLY for:
            # - Explicit "comprehensive analysis" requests
            # - Multi-part queries ("analyze X AND review Y")
            
            if agents_to_use and len(agents_to_use) > 1:
                # Sort by score (highest first)
                agents_to_use_sorted = sorted(agents_to_use, key=lambda x: x.get('score', 0), reverse=True)
                top_agent = agents_to_use_sorted[0]
                
                # Check for multi-part or comprehensive requests
                multi_part_keywords = ['and', 'also', 'plus', 'comprehensive', 'detailed', 'thorough', 'everything']
                is_multi_part = sum(1 for kw in multi_part_keywords if kw in query.lower()) >= 2
                
                # CATEGORY-BASED DECISION:
                if category in ['RAG', 'GENERAL', 'INFORMATIONAL']:
                    # RAG queries: Always use TOP 1 agent (unless explicitly multi-part)
                    if not is_multi_part:
                        agents_to_use = [top_agent]
                        print(f"[V2.0] RAG query → Using TOP agent: {top_agent['agent_name']} (score: {top_agent.get('score', 0)})")
                    else:
                        print(f"[V2.0] Multi-part RAG query → Using {len(agents_to_use)} agents")
                
                elif category in ['CODE', 'DEBUG', 'REVIEW']:
                    # Code queries: Always TOP 1 agent
                    agents_to_use = [top_agent]
                    print(f"[V2.0] Code query → Using TOP agent: {top_agent['agent_name']}")
                
                elif category in ['STRATEGY', 'PLANNING', 'REASONING']:
                    # Strategy: Use top 2 if scores are close (within 30%)
                    second_agent = agents_to_use_sorted[1] if len(agents_to_use_sorted) > 1 else None
                    if second_agent and (second_agent.get('score', 0) >= top_agent.get('score', 1) * 0.7):
                        agents_to_use = agents_to_use_sorted[:2]
                        print(f"[V2.0] Strategy query → Using top 2 agents for comprehensive planning")
                    else:
                        agents_to_use = [top_agent]
                        print(f"[V2.0] Strategy query → Using TOP agent: {top_agent['agent_name']}")
                
                else:
                    # Unknown category: Default to top agent
                    agents_to_use = [top_agent]
                    print(f"[V2.0] Unknown category '{category}' → Using TOP agent: {top_agent['agent_name']}")
                    
            elif agents_to_use:
                print(f"[V2.0] Single agent selected: {agents_to_use[0].get('agent_name')}")
                
            num_agents = len(agents_to_use)
        else:
            agents_to_use = []
            num_agents = 0
        
        # Step 3: Create Dynamic Orchestration Plan
        print("[V2.0 STEP 3] Creating dynamic orchestration plan...")
        
        # IMPORTANT: Pass the agents selected by HybridRouter to the orchestration plan
        # This ensures we use the BEST agents (not randomly selected ones!)
        orchestrator_context['selected_agents'] = agents_to_use
        
        # GAME CHANGER: Let UnifiedIntelligenceLayer create a cross-framework plan
        # This allows RAG agents (LangGraph) to fetch Kaggle data,
        # then Reasoning agents (CrewAI/AutoGen) to analyze it!
        orchestration_plan = unified_intelligence.create_orchestration_plan(
            query, orchestrator_context
        )
        
        interaction_pattern = orchestration_plan.get('interaction_pattern', 'sequential')
        planned_agents = orchestration_plan.get('agents', [])
        expected_duration = orchestration_plan.get('expected_duration', 'unknown')
        
        print(f"[V2.0] Orchestration Plan:")
        print(f"  - Pattern: {interaction_pattern}")
        print(f"  - Agents: {len(planned_agents)}")
        print(f"  - Expected Duration: {expected_duration}")
        
        for i, agent in enumerate(planned_agents):
            print(f"  - Agent {i+1}: {agent['name']} ({agent['framework']}) - {agent['confidence']:.2f}")
        
        # Step 4: Execute dynamic orchestration plan
        print(f"[V2.0 STEP 4] Executing dynamic orchestration plan...")
        start_time = datetime.now()
        
        # Execute the plan using UnifiedIntelligenceLayer's dynamic orchestrator
        result = unified_intelligence.execute_orchestration_plan(query, orchestrator_context)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        print(f"[V2.0] Query processed in {execution_time:.2f}s")
        
        # Extract response from dynamic orchestrator result
        execution_summary = result.get('execution_summary', {})
        agent_results = result.get('results', [])
        
        # Combine all agent responses into final response
        final_response = ""
        successful_agents = []
        failed_agents = []
        
        if agent_results:
            # Synthesize responses from all agents
            for agent_result in agent_results:
                agent_name = agent_result.get('agent_name', 'unknown')
                
                # DEBUG: Print the actual structure returned by the agent
                print(f"[DEBUG] Agent {agent_name} result structure: {list(agent_result.keys())}")
                
                # Check if agent succeeded or failed
                if 'error' in agent_result:
                    failed_agents.append(agent_name)
                    print(f"[V2.0] Agent {agent_name} failed: {agent_result.get('error')}")
                    continue
                
                # Extract response (try multiple possible locations)
                agent_response = agent_result.get('result', {}).get('response', '')
                if not agent_response:
                    agent_response = agent_result.get('response', '')
                if not agent_response:
                    # Try nested result
                    result_obj = agent_result.get('result', {})
                    if isinstance(result_obj, dict):
                        agent_response = result_obj.get('result', '')
                
                print(f"[DEBUG] Agent {agent_name} extracted response length: {len(agent_response) if agent_response else 0}")
                
                if agent_response:
                    successful_agents.append(agent_name)
                    final_response += f"\n\n{agent_response}"  # Don't label agents, cleaner output
                else:
                    print(f"[WARN] Agent {agent_name} succeeded but returned empty response. Full result: {agent_result}")
        
        print(f"[V2.0] Successful agents: {successful_agents}, Failed agents: {failed_agents}")
        print(f"[DEBUG] final_response length: {len(final_response)}")
        print(f"[DEBUG] final_response preview: {final_response[:200] if final_response else 'EMPTY'}")
        
        if not final_response:
            final_response = "I processed your query but couldn't generate a response. ChromaDB may be empty."
        
        # Extract metadata from execution summary
        frameworks_used = execution_summary.get('frameworks_used', [])
        agents_used_names = execution_summary.get('agents_used', [])
        
        print(f"[V2.0 SUMMARY] Complexity: {complexity} | Category: {category} | Pattern: {interaction_pattern} | Agents: {agents_used_names} | Frameworks: {frameworks_used}")
        
        # Build response
        response_data = {
            "response": final_response.strip(),
            "final_response": final_response.strip(),  # Frontend expects this key
            "metadata": {
                "execution_time": execution_time,
                "complexity": complexity,
                "category": category,
                "interaction_pattern": interaction_pattern,
                "agents_used": agents_used_names,
                "frameworks_used": frameworks_used,
                "num_agents": len(agents_used_names),
                "expected_duration": expected_duration,
                "orchestrator_mode": "dynamic",
                "orchestrator_version": "2.0",
                "unified_intelligence": "active",
                "dynamic_orchestration": "active",
                "modes_available": ["crewai", "autogen", "langgraph", "dynamic"],
                "timestamp": datetime.now().isoformat()
            },
            "competition_context": {
                "competition_slug": competition_slug,
                "kaggle_username": kaggle_username
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[ERROR] V2.0 Query failed: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "error": f"Query processing failed: {str(e)}",
            "response": "I encountered an error processing your request. Please try again."
        }), 500

# ==================== HEALTH & INFO ENDPOINTS ====================

@app.route("/", methods=["GET"])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Kaggle Copilot Backend V2.0",
        "version": "2.0",
        "orchestrator": "MasterOrchestrator",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "query": "/component-orchestrator/query",
            "session_init": "/session/initialize",
            "session_search": "/session/competitions/search"
        }
    }), 200

if __name__ == "__main__":
    print("\n" + "="*80)
    print("KAGGLE COPILOT ASSISTANT - BACKEND V2.0")
    print("="*80)
    print(f"[INFO] Health check: http://localhost:5000/health")
    print(f"[INFO] Query endpoint: http://localhost:5000/component-orchestrator/query")
    print(f"[INFO] V2.0 Orchestration: {'ACTIVE' if V2_ORCHESTRATION_AVAILABLE else 'NOT AVAILABLE'}")
    print(f"[INFO] Unified Intelligence: {'ACTIVE' if unified_intelligence else 'INACTIVE'}")
    print(f"[INFO] Hybrid Router: {'ACTIVE' if hybrid_router else 'INACTIVE'}")
    print(f"[INFO] Hybrid Scraping: {'ACTIVE' if hybrid_scraping_agent else 'INACTIVE'}")
    print("="*80 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False)

