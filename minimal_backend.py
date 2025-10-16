#!/usr/bin/env python3
"""
Minimal Flask Backend for Session Management Only
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

# Import Multi-Agent System
try:
    from orchestrators.expert_orchestrator_langgraph import ExpertSystemOrchestratorLangGraph
    from orchestrators.component_orchestrator import ComponentOrchestrator
    MULTIAGENT_AVAILABLE = True
    print("[OK] Multi-agent system loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: Multi-agent system not available: {e}")
    MULTIAGENT_AVAILABLE = False

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
    print("[OK] Core scraping system loaded successfully (OverviewScraper, NotebookAPIFetcher, DiscussionScraper)")
except ImportError as e:
    print(f"[WARN] Warning: Core scraping system not available: {e}")
    SCRAPING_AVAILABLE = False

# Import Advanced Scraping Features (OPTIONAL - can fail without breaking core)
try:
    from hybrid_scraping_routing.agent_router import HybridScrapingAgent
    from query_processing.user_input_processor import UserInputProcessor
    print("[OK] Advanced scraping features loaded (HybridScrapingAgent, UserInputProcessor)")
except ImportError as e:
    print(f"[WARN] Advanced scraping features not available (optional): {e}")
    # Don't set SCRAPING_AVAILABLE to False - core scrapers still work!

# Import Agents and LLM for intelligent analysis
try:
    from agents import CompetitionSummaryAgent, NotebookExplainerAgent, DiscussionHelperAgent, CommunityEngagementAgent
    from agents.data_section_agent import DataSectionAgent
    from agents.code_feedback_agent import CodeFeedbackAgent
    from agents.error_diagnosis_agent import ErrorDiagnosisAgent
    from llms.llm_loader import get_llm_from_config
    AGENT_AVAILABLE = True
    print("[OK] Competition analysis agents loaded successfully")
    print("[OK] Code handling agents (CodeFeedbackAgent, ErrorDiagnosisAgent) loaded successfully")
    print("[OK] Community engagement agent (CommunityEngagementAgent) loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: Agent system not available: {e}")
    AGENT_AVAILABLE = False

# Import Data Fetcher for hybrid API + scraping
try:
    from Kaggle_Fetcher.data_fetcher import DataFetcher
    DATA_FETCHER_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Warning: Data Fetcher not available: {e}")
    DATA_FETCHER_AVAILABLE = False

# Import ChromaDB RAG Pipeline for persistent storage
try:
    from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
    CHROMADB_AVAILABLE = True
    print("[OK] ChromaDB RAG pipeline loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: ChromaDB not available: {e}")
    CHROMADB_AVAILABLE = False

# Import LangGraph Visualization for debugging
try:
    from workflows.graph_visual import get_graph_image
    from workflows.graph_workflow import compiled_graph
    LANGGRAPH_VIZ_AVAILABLE = True
    print("[OK] LangGraph visualization loaded successfully")
except ImportError as e:
    print(f"[WARN] Warning: LangGraph visualization not available: {e}")
    LANGGRAPH_VIZ_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# In-memory store for active sessions
user_sessions = {}

# 🔧 DEBUG: Store execution traces for LangGraph visualization
execution_traces = {}  # {query_id: {nodes: [], timestamp: "", response: "", agents_used: []}}
MAX_TRACES = 50  # Keep last 50 traces for debugging

# Initialize Multi-Agent System
multiagent_orchestrator = None
component_orchestrator = None
if MULTIAGENT_AVAILABLE:
    try:
        multiagent_orchestrator = ExpertSystemOrchestratorLangGraph()
        print("[OK] Multi-agent orchestrator (LangGraph) initialized successfully")
        
        # Initialize ComponentOrchestrator for CrewAI/AutoGen multi-agent interactions
        component_orchestrator = ComponentOrchestrator()
        print("[OK] Component orchestrator (CrewAI/AutoGen) initialized successfully")
    except Exception as e:
        print(f"[WARN] Failed to initialize multi-agent orchestrators: {e}")
        MULTIAGENT_AVAILABLE = False

# Initialize ChromaDB RAG Pipeline for persistent data storage
chromadb_pipeline = None
if CHROMADB_AVAILABLE:
    try:
        chromadb_pipeline = ChromaDBRAGPipeline(
            collection_name="kaggle_competition_data",
            embedding_model="BAAI/bge-base-en"
        )
        print("[OK] ChromaDB pipeline initialized successfully")
    except Exception as e:
        print(f"[WARN] Failed to initialize ChromaDB pipeline: {e}")
        CHROMADB_AVAILABLE = False

# Create session management blueprint
session_bp = Blueprint("session", __name__, url_prefix="/session")

def search_kaggle_competitions(query: str) -> list:
    """Search for Kaggle competitions using real API"""
    if not KAGGLE_API_AVAILABLE:
        # Fallback to mock data if Kaggle API is not available
        mock_competitions = [
            {
                "slug": "nfl-big-data-bowl-2026-prediction",
                "name": "NFL Big Data Bowl 2026",
                "description": "Predict NFL player performance",
                "category": "Sports",
                "url": "https://www.kaggle.com/competitions/nfl-big-data-bowl-2026-prediction"
            },
            {
                "slug": "titanic",
                "name": "Titanic - Machine Learning from Disaster",
                "description": "Predict survival on the Titanic",
                "category": "Getting Started",
                "url": "https://www.kaggle.com/competitions/titanic"
            }
        ]
        
        if not query:
            return mock_competitions[:5]
        
        query_lower = query.lower()
        filtered = [comp for comp in mock_competitions if 
                    query_lower in comp['name'].lower() or 
                    query_lower in comp['slug'].lower() or
                    query_lower in comp['description'].lower()]
        
        return filtered[:5]
    
    try:
        # Use real Kaggle API
        # Note: Removed category parameter - "all" causes 400 error
        # Valid categories: "getting-started", "playground", "research", etc.
        competitions = api_search_competitions(
            query=query,
            sort_by="latestDeadline",
            page=1,
            page_size=10
        )
        
        return competitions[:5]  # Return top 5 results
        
    except Exception as e:
        print(f"Error searching competitions with Kaggle API: {e}")
        # Fallback to empty list on error
        return []

def check_chromadb_for_competition(competition_slug: str, section: str = "evaluation") -> dict:
    """
    Check if competition data already exists in ChromaDB.
    
    Args:
        competition_slug: Competition identifier
        section: Section to retrieve (e.g., "evaluation", "data", "overview")
    
    Returns:
        dict with 'found' (bool), 'content' (str), and 'metadata' (dict)
    """
    if not CHROMADB_AVAILABLE or not chromadb_pipeline:
        return {'found': False, 'content': '', 'metadata': {}}
    
    try:
        print(f"[DEBUG] Checking ChromaDB for {competition_slug} - {section} section...")
        
        # Query ChromaDB with competition-specific query
        query = f"{section} metric for {competition_slug}"
        retrieved_docs = chromadb_pipeline.retriever.retrieve(query, top_k=5)
        
        print(f"[DEBUG] Retrieved {len(retrieved_docs)} documents from ChromaDB")
        
        # Filter for this specific competition
        for i, doc in enumerate(retrieved_docs):
            metadata = doc.get('metadata', {})
            content = doc.get('content', '')
            
            # Debug: Print metadata to see what's actually stored
            print(f"[DEBUG] Doc {i+1} metadata keys: {list(metadata.keys())}")
            print(f"[DEBUG] Doc {i+1} content preview: {content[:100]}...")
            
            # Try multiple ways to match the competition
            doc_competition = metadata.get('competition_slug', '')
            doc_section = metadata.get('section', '')
            doc_url = metadata.get('url', '')
            
            # Extract competition slug from URL if stored there
            if not doc_competition and doc_url.startswith('kaggle://competition/'):
                doc_competition = doc_url.replace('kaggle://competition/', '')
            
            # Match by competition slug in metadata OR URL
            slug_match = doc_competition == competition_slug
            section_match = section in doc_section.lower() if doc_section else False
            
            print(f"[DEBUG] Doc {i+1} - doc_competition: '{doc_competition}', slug_match: {slug_match}, section_match: {section_match}")
            
            if slug_match and section_match:
                if content and len(content) > 100:  # Ensure substantial content
                    print(f"[CACHE HIT] Found {section} data in ChromaDB ({len(content)} chars)")
                    return {
                        'found': True,
                        'content': content,
                        'metadata': metadata
                    }
        
        print(f"[CACHE MISS] No {section} data found in ChromaDB for {competition_slug}")
        return {'found': False, 'content': '', 'metadata': {}}
        
    except Exception as e:
        print(f"[WARN] ChromaDB check failed: {e}")
        import traceback
        traceback.print_exc()
        return {'found': False, 'content': '', 'metadata': {}}

def get_detailed_competition_info(competition_slug: str) -> dict:
    """Get detailed competition information using scraping system."""
    if not SCRAPING_AVAILABLE:
        print("[DEBUG] Scraping system not available")
        return {'scraped_successfully': False, 'error': 'Scraping system not available'}
    
    # OPTIMIZATION: Check ChromaDB first before scraping
    cached_eval = check_chromadb_for_competition(competition_slug, section="evaluation")
    if cached_eval['found']:
        print(f"[OPTIMIZATION] Using cached evaluation data from ChromaDB (skipping scrape)")
        evaluation_text = cached_eval['content']
        
        # Return cached data in the expected format
        return {
            'overview_data': {},
            'overview_sections': {},
            'evaluation_info': {
                'detailed_evaluation': evaluation_text,
                'markdown': evaluation_text
            },
            'scraped_successfully': True,
            'from_cache': True
        }
    
    try:
        print(f"[DEBUG] No cached data found. Starting to scrape overview for: {competition_slug}")
        # Use OverviewScraper to get detailed competition information
        overview_scraper = OverviewScraper(competition_slug)
        overview_result = overview_scraper.scrape()
        
        print(f"[DEBUG] Scrape result structure: {list(overview_result.keys()) if overview_result else 'None'}")
        
        # Extract the scraped sections from the new Playwright-based structure
        overview_sections = overview_result.get('overview_sections', {})
        section_titles = list(overview_sections.keys())
        
        print(f"[DEBUG] Found {len(overview_sections)} sections: {section_titles}")
        
        # Extract evaluation metric from scraped sections
        evaluation_info = {}
        evaluation_text = ""
        
        for section_title, section_data in overview_sections.items():
            if 'evaluation' in section_title.lower() or 'metric' in section_title.lower():
                # New structure has 'text' and 'markdown' fields
                evaluation_text = section_data.get('text', '')
                evaluation_info['detailed_evaluation'] = evaluation_text
                evaluation_info['markdown'] = section_data.get('markdown', '')
                print(f"[DEBUG] Found evaluation section: '{section_title}'")
                print(f"[DEBUG] Evaluation content length: {len(evaluation_text)} chars")
                print(f"[DEBUG] Evaluation content preview: {evaluation_text[:200]}...")
                break
        
        if not evaluation_text:
            print(f"[DEBUG] No evaluation section found. Available sections: {section_titles}")
        
        # Store scraped data in ChromaDB for future retrieval
        if CHROMADB_AVAILABLE and chromadb_pipeline and evaluation_text:
            try:
                print("[DEBUG] Storing evaluation data in ChromaDB...")
                # Prepare document for indexing
                # NOTE: Use 'url' field to store competition_slug since indexer preserves it
                documents_to_index = [{
                    "content": evaluation_text,
                    "section": "evaluation",
                    "title": "Evaluation Metric",
                    "deep_scraped": True,
                    "url": f"kaggle://competition/{competition_slug}",  # Store slug in URL
                    "competition_slug": competition_slug  # Try to store directly too
                }]
                
                # Index in ChromaDB
                result = chromadb_pipeline.index_scraped_data(
                    pydantic_results=[],
                    structured_results=documents_to_index
                )
                print(f"[DEBUG] ChromaDB indexing result: {result}")
                
            except Exception as e:
                print(f"[WARN] Failed to store in ChromaDB: {e}")
                # Don't fail the scraping if storage fails
        
        return {
            'overview_data': overview_result,
            'overview_sections': overview_sections,
            'evaluation_info': evaluation_info,
            'scraped_successfully': True
        }
        
    except Exception as e:
        print(f"[ERROR] Error scraping competition details: {e}")
        import traceback
        traceback.print_exc()
        return {'scraped_successfully': False, 'error': str(e)}

def check_chromadb_for_notebooks(competition_slug: str, notebook_path: str = None) -> dict:
    """
    Check if notebook data already exists in ChromaDB.
    
    Args:
        competition_slug: Competition identifier
        notebook_path: Specific notebook path (optional, if None checks for any notebooks)
    
    Returns:
        dict with 'found' (bool), 'content' (str), and 'metadata' (dict)
    """
    if not CHROMADB_AVAILABLE or not chromadb_pipeline:
        return {'found': False, 'content': '', 'metadata': {}}
    
    try:
        print(f"[DEBUG] Checking ChromaDB for notebooks in {competition_slug}...")
        
        # Query ChromaDB with competition-specific query
        query = f"notebooks code for {competition_slug}"
        retrieved_docs = chromadb_pipeline.retriever.retrieve(query, top_k=10)
        
        print(f"[DEBUG] Retrieved {len(retrieved_docs)} documents from ChromaDB")
        
        # Filter for this specific competition and notebook
        matching_docs = []
        for i, doc in enumerate(retrieved_docs):
            metadata = doc.get('metadata', {})
            content = doc.get('content', '')
            
            # Debug: Print metadata to see what's actually stored
            print(f"[DEBUG] Doc {i+1} metadata keys: {list(metadata.keys())}")
            
            # Try multiple ways to match the competition
            doc_competition = metadata.get('competition_slug', '')
            doc_section = metadata.get('section', '')
            doc_notebook_path = metadata.get('notebook_path', '')
            
            # Match by competition slug
            slug_match = doc_competition == competition_slug
            section_match = 'code' in doc_section.lower() if doc_section else False
            
            # If notebook_path specified, also match that
            if notebook_path:
                notebook_match = doc_notebook_path == notebook_path
                if slug_match and section_match and notebook_match:
                    matching_docs.append({'content': content, 'metadata': metadata})
            elif slug_match and section_match:
                matching_docs.append({'content': content, 'metadata': metadata})
        
        if matching_docs:
            # Return the first matching doc or aggregated content
            combined_content = "\n\n---\n\n".join([doc['content'] for doc in matching_docs])
            print(f"[CACHE HIT] Found {len(matching_docs)} notebook(s) in ChromaDB ({len(combined_content)} chars)")
            return {
                'found': True,
                'content': combined_content,
                'metadata': matching_docs[0]['metadata'],
                'count': len(matching_docs)
            }
        
        print(f"[CACHE MISS] No notebook data found in ChromaDB for {competition_slug}")
        return {'found': False, 'content': '', 'metadata': {}}
        
    except Exception as e:
        print(f"[WARN] ChromaDB notebook check failed: {e}")
        import traceback
        traceback.print_exc()
        return {'found': False, 'content': '', 'metadata': {}}

def check_cached_notebook_analysis(notebook_path: str, competition_slug: str = None) -> dict:
    """
    Check if we have a cached analysis for a specific notebook.
    
    Args:
        notebook_path: Notebook identifier (e.g., "username/notebook-name")
        competition_slug: Optional competition filter
    
    Returns:
        dict with 'found' (bool), 'analysis' (str), and 'metadata' (dict)
    """
    if not CHROMADB_AVAILABLE or not chromadb_pipeline:
        return {'found': False, 'analysis': '', 'metadata': {}}
    
    try:
        print(f"[DEBUG] Checking cache for notebook analysis: {notebook_path}")
        
        # Query ChromaDB for this specific notebook's analysis
        query = f"notebook analysis {notebook_path}"
        retrieved_docs = chromadb_pipeline.retriever.retrieve(query, top_k=5)
        
        for doc in retrieved_docs:
            metadata = doc.get('metadata', {})
            content = doc.get('content', '')
            
            # Match by notebook_path and section type
            doc_notebook = metadata.get('notebook_path', '')
            doc_section = metadata.get('section', '')
            
            if doc_notebook == notebook_path and doc_section == 'notebook_analysis':
                print(f"[CACHE HIT] Found cached analysis for {notebook_path}")
                return {
                    'found': True,
                    'analysis': content,
                    'metadata': metadata
                }
        
        print(f"[CACHE MISS] No cached analysis for {notebook_path}")
        return {'found': False, 'analysis': '', 'metadata': {}}
        
    except Exception as e:
        print(f"[WARN] Failed to check cached analysis: {e}")
        return {'found': False, 'analysis': '', 'metadata': {}}

def store_notebook_analysis(notebook_path: str, analysis: str, notebook_metadata: dict, competition_slug: str = None) -> bool:
    """
    Store individual notebook analysis in ChromaDB for future reuse.
    
    Args:
        notebook_path: Notebook identifier
        analysis: The agent's analysis text
        notebook_metadata: Metadata about the notebook (title, author, votes)
        competition_slug: Competition identifier
    
    Returns:
        bool: Success status
    """
    if not CHROMADB_AVAILABLE or not chromadb_pipeline:
        return False
    
    try:
        print(f"[DEBUG] Storing analysis for notebook: {notebook_path}")
        
        # Prepare document for ChromaDB
        from datetime import datetime, timezone
        documents_to_index = [{
            "content": analysis,
            "section": "notebook_analysis",  # New section type
            "title": notebook_metadata.get('title', 'Untitled'),
            "notebook_path": notebook_path,
            "competition_slug": competition_slug or "unknown",
            "author": notebook_metadata.get('author', ''),
            "votes": notebook_metadata.get('votes', 0),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "analysis_version": "v1"
        }]
        
        # Store in ChromaDB
        chromadb_pipeline.index_scraped_data(
            pydantic_results=[],
            structured_results=documents_to_index
        )
        
        print(f"[OK] Stored analysis for {notebook_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to store analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def fetch_and_store_notebooks(competition_slug: str, max_notebooks: int = 5, min_votes: int = 10) -> dict:
    """
    Fetch competition notebooks via Kaggle API and store in ChromaDB.
    
    Args:
        competition_slug: Competition identifier
        max_notebooks: Maximum number of notebooks to fetch
        min_votes: Minimum votes threshold
    
    Returns:
        dict with fetched notebook data and success status
    """
    if not SCRAPING_AVAILABLE:
        print("[DEBUG] Scraping system not available")
        return {'success': False, 'error': 'Scraping system not available'}
    
    # OPTIMIZATION: Check ChromaDB first before fetching
    cached_notebooks = check_chromadb_for_notebooks(competition_slug)
    if cached_notebooks['found']:
        print(f"[OPTIMIZATION] Using {cached_notebooks['count']} cached notebooks from ChromaDB")
        return {
            'notebooks_data': cached_notebooks,
            'success': True,
            'from_cache': True,
            'count': cached_notebooks['count']
        }
    
    try:
        print(f"[DEBUG] No cached data found. Fetching notebooks for: {competition_slug}")
        
        # Use NotebookAPIFetcher to get notebook content
        fetcher = NotebookAPIFetcher(competition_slug)
        result = fetcher.fetch(
            max_pinned=max_notebooks,
            max_top_voted=max_notebooks,
            min_votes=min_votes,
            download_content=True
        )
        
        print(f"[DEBUG] Fetch result: {len(result['notebook_categories']['pinned'])} notebooks")
        
        # Process and store notebooks in ChromaDB
        stored_count = 0
        for category, notebooks in result['notebook_categories'].items():
            for notebook_data in notebooks:
                if not notebook_data.get('content'):
                    continue  # Skip if no content downloaded
                
                metadata = notebook_data['metadata']
                content = notebook_data['content']
                
                # Combine cells for storage
                combined_content = []
                for cell in content.get('markdown_cells', []):
                    combined_content.append(f"MARKDOWN:\n{cell.get('content', '')}")
                for cell in content.get('code_cells', []):
                    combined_content.append(f"CODE ({cell.get('language', 'python')}):\n{cell.get('content', '')}")
                
                full_content = "\n\n---\n\n".join(combined_content)
                
                if not full_content.strip():
                    continue  # Skip empty notebooks
                
                print(f"[DEBUG] Storing notebook: {metadata['title']} ({len(full_content)} chars)")
                
                # Store in ChromaDB
                if CHROMADB_AVAILABLE and chromadb_pipeline:
                    try:
                        documents_to_index = [{
                            "content": full_content,
                            "section": "code",
                            "title": metadata['title'],
                            "deep_scraped": False,
                            "url": f"kaggle://competition/{competition_slug}/notebook/{metadata['ref']}",
                            "competition_slug": competition_slug,
                            "notebook_path": metadata['ref'],
                            "author": metadata['author'],
                            "votes": metadata['total_votes'],
                            "category": category
                        }]
                        
                        chromadb_pipeline.index_scraped_data(
                            pydantic_results=[],
                            structured_results=documents_to_index
                        )
                        stored_count += 1
                        
                    except Exception as e:
                        print(f"[WARN] Failed to store notebook in ChromaDB: {e}")
        
        print(f"[DEBUG] Stored {stored_count} notebooks in ChromaDB")
        
        return {
            'notebooks_data': result,
            'success': True,
            'count': stored_count
        }
        
    except Exception as e:
        print(f"[ERROR] Error fetching notebooks: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def fetch_and_store_discussions(competition_slug: str, max_discussions: int = 20) -> dict:
    """
    Fetch competition discussions via Playwright scraper and store in ChromaDB.
    
    Args:
        competition_slug: Competition identifier
        max_discussions: Maximum number of discussions to fetch
    
    Returns:
        dict with fetched discussion data and success status
    """
    if not SCRAPING_AVAILABLE:
        print("[DEBUG] Scraping system not available")
        return {'success': False, 'error': 'Scraping system not available'}
    
    # OPTIMIZATION: Check ChromaDB first before scraping
    cached_discussions = check_chromadb_for_discussions(competition_slug)
    if cached_discussions['found']:
        print(f"[OPTIMIZATION] Using {cached_discussions['count']} cached discussions from ChromaDB")
        return {
            'discussions_data': cached_discussions,
            'success': True,
            'from_cache': True,
            'count': cached_discussions['count'],
            'pinned_count': cached_discussions['pinned_count']
        }
    
    try:
        print(f"[DEBUG] No cached data found. Scraping discussions for: {competition_slug}")
        
        # Use DiscussionScraperPlaywright to get discussion metadata
        scraper = DiscussionScraperPlaywright(competition_slug=competition_slug)
        discussions = scraper.scrape(max_discussions=max_discussions)
        
        print(f"[DEBUG] Scrape result: {len(discussions)} discussions")
        
        # Process and store discussions in ChromaDB
        stored_count = 0
        pinned_count = 0
        for discussion in discussions:
            # Store in ChromaDB
            if CHROMADB_AVAILABLE and chromadb_pipeline:
                try:
                    # Build searchable content
                    searchable_content = f"{discussion['title']} {discussion.get('author', '')}"
                    
                    # Flatten structure for ChromaDB (all fields at top level)
                    doc = {
                        "title": discussion['title'],
                        "content": searchable_content,
                        "url": discussion['url'],
                        "section": "discussion",
                        # All metadata fields at top level for indexer
                        "discussion_id": discussion['discussion_id'],
                        "author": discussion['author'],
                        "author_rank": discussion.get('author_rank'),
                        "date": discussion['date'],
                        "is_pinned": discussion['is_pinned'],
                        "comment_count": discussion['comment_count'],
                        "upvotes": discussion.get('upvotes'),
                        "competition_slug": competition_slug,
                        "last_scraped": discussion['last_scraped'],
                        "post_hash": discussion['post_hash'],
                        "has_full_content": False,  # Flag: content not yet scraped (Phase 3)
                    }
                    
                    chromadb_pipeline.index_scraped_data(
                        pydantic_results=[],
                        structured_results=[doc]
                    )
                    stored_count += 1
                    if discussion['is_pinned']:
                        pinned_count += 1
                    
                except Exception as e:
                    print(f"[WARN] Failed to store discussion in ChromaDB: {e}")
        
        print(f"[DEBUG] Stored {stored_count} discussions in ChromaDB ({pinned_count} pinned)")
        
        return {
            'discussions_data': discussions,
            'success': True,
            'count': stored_count,
            'pinned_count': pinned_count,
            'from_cache': False
        }
        
    except Exception as e:
        print(f"[ERROR] Error fetching discussions: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def check_chromadb_for_discussions(competition_slug: str) -> dict:
    """
    Check if discussions for a competition are already cached in ChromaDB.
    
    Returns:
        dict with 'found' boolean and discussion count
    """
    if not CHROMADB_AVAILABLE or not chromadb_pipeline:
        return {'found': False, 'count': 0, 'pinned_count': 0}
    
    try:
        collection = chromadb_pipeline.retriever._get_collection()
        
        # Query for all discussions for this competition
        results = collection.query(
            query_embeddings=[chromadb_pipeline.retriever.embedding_model.encode("discussion").tolist()],
            where={"$and": [
                {"competition_slug": competition_slug},
                {"section": "discussion"}
            ]},
            n_results=100,  # Get all
            include=["metadatas"]
        )
        
        if results["metadatas"] and results["metadatas"][0]:
            count = len(results["metadatas"][0])
            pinned_count = sum(1 for meta in results["metadatas"][0] if meta.get('is_pinned', False))
            print(f"[CACHE CHECK] Found {count} discussions ({pinned_count} pinned) in ChromaDB for {competition_slug}")
            return {'found': True, 'count': count, 'pinned_count': pinned_count}
        
        print(f"[CACHE MISS] No discussions found in ChromaDB for {competition_slug}")
        return {'found': False, 'count': 0, 'pinned_count': 0}
        
    except Exception as e:
        print(f"[ERROR] Error checking ChromaDB for discussions: {e}")
        return {'found': False, 'count': 0, 'pinned_count': 0}


def fetch_and_store_data_info(competition_slug: str) -> dict:
    """
    Fetch competition data info (files + description) and store in ChromaDB.
    Uses hybrid approach: API for files, scraping for description.
    
    Args:
        competition_slug: Competition identifier
    
    Returns:
        dict with data files, description, and success status
    """
    if not DATA_FETCHER_AVAILABLE:
        print("[DEBUG] Data Fetcher not available")
        return {'success': False, 'error': 'Data Fetcher not available'}
    
    # OPTIMIZATION: Check ChromaDB first
    cached_data = check_chromadb_for_data(competition_slug)
    if cached_data['found']:
        print(f"[OPTIMIZATION] Using cached data info from ChromaDB")
        return {
            'data_info': cached_data['data'],
            'success': True,
            'from_cache': True
        }
    
    try:
        print(f"[DEBUG] Fetching data info for: {competition_slug}")
        
        # Use DataFetcher (hybrid API + scraping)
        fetcher = DataFetcher()
        data_info = fetcher.fetch_complete_data_info(
            competition_slug,
            include_description=True  # Will scrape if not cached
        )
        
        print(f"[DEBUG] Fetched {data_info['file_count']} files, description: {data_info['has_description']}")
        
        # Store in ChromaDB
        if CHROMADB_AVAILABLE and chromadb_pipeline:
            try:
                # Combine description and file info into searchable content
                searchable_content = f"{data_info['description'][:500]} Files: {', '.join([f['name'] for f in data_info['files']])}"
                
                doc = {
                    "title": f"Data Section: {competition_slug}",
                    "content": searchable_content,
                    "section": "data",
                    "competition_slug": competition_slug,
                    "file_count": data_info['file_count'],
                    "total_size": data_info['total_size'],
                    "files": str(data_info['files']),  # Serialize for storage
                    "description": data_info['description'],
                    "has_description": data_info['has_description'],
                    "column_count": len(data_info.get('column_info', [])),
                    "last_updated": datetime.now().isoformat()
                }
                
                chromadb_pipeline.index_scraped_data(
                    pydantic_results=[],
                    structured_results=[doc]
                )
                print("[DEBUG] Stored data info in ChromaDB")
                
            except Exception as e:
                print(f"[WARN] Failed to store data info in ChromaDB: {e}")
        
        return {
            'data_info': data_info,
            'success': True,
            'from_cache': False
        }
        
    except Exception as e:
        print(f"[ERROR] Error fetching data info: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def check_chromadb_for_data(competition_slug: str) -> dict:
    """
    Check if data info for a competition is already cached in ChromaDB.
    
    Returns:
        dict with 'found' boolean and data info
    """
    if not CHROMADB_AVAILABLE or not chromadb_pipeline:
        return {'found': False, 'data': None}
    
    try:
        collection = chromadb_pipeline.retriever._get_collection()
        
        # Query for data section
        results = collection.query(
            query_embeddings=[chromadb_pipeline.retriever.embedding_model.encode("data files").tolist()],
            where={"$and": [
                {"competition_slug": competition_slug},
                {"section": "data"}
            ]},
            n_results=1,
            include=["metadatas", "documents"]
        )
        
        if results["metadatas"] and results["metadatas"][0]:
            metadata = results["metadatas"][0][0]
            
            # Reconstruct data_info from stored metadata
            import ast
            data_info = {
                "competition": competition_slug,
                "files": ast.literal_eval(metadata.get('files', '[]')),
                "file_count": metadata.get('file_count', 0),
                "total_size": metadata.get('total_size', 0),
                "description": metadata.get('description', ''),
                "has_description": metadata.get('has_description', False),
                "column_info": []  # Could store this too if needed
            }
            
            print(f"[CACHE HIT] Found cached data info for {competition_slug}")
            return {'found': True, 'data': data_info}
        
        print(f"[CACHE MISS] No data info found in ChromaDB for {competition_slug}")
        return {'found': False, 'data': None}
        
    except Exception as e:
        print(f"[ERROR] Error checking ChromaDB for data: {e}")
        return {'found': False, 'data': None}


def fetch_competition_context(competition_slug: str) -> dict:
    """Fetch real competition context using Kaggle API"""
    if not KAGGLE_API_AVAILABLE:
        # Fallback to mock data
        return {
            "slug": competition_slug,
            "name": f"Competition: {competition_slug}",
            "total_notebooks": 150,
            "competition_accessible": True,
            "description": f"Mock description for {competition_slug}",
            "deadline": "2026-03-15",
            "evaluation_metric": "RMSE"
        }
    
    try:
        # Get competition details from Kaggle API (includes notebook count)
        competition_details = api_get_competition_details(competition_slug)
        
        if competition_details:
            return {
                "slug": competition_slug,
                "name": competition_details.get("name", f"Competition: {competition_slug}"),
                "total_notebooks": competition_details.get("notebook_count", 0),
                "competition_accessible": True,
                "description": competition_details.get("description", ""),
                "deadline": competition_details.get("deadline", ""),
                "evaluation_metric": competition_details.get("evaluation_metric", ""),
                "category": competition_details.get("category", ""),
                "prize": competition_details.get("prize", ""),
                "team_count": competition_details.get("team_count", 0),
                "max_team_size": competition_details.get("max_team_size", 1),
                "max_daily_submissions": competition_details.get("max_daily_submissions", 0),
                "url": competition_details.get("url", f"https://www.kaggle.com/competitions/{competition_slug}")
            }
        else:
            # Competition not found or not accessible
            return {
                "slug": competition_slug,
                "name": f"Competition: {competition_slug}",
                "total_notebooks": 0,
                "competition_accessible": False,
                "description": "Competition not accessible via API. This could mean: 1) Private/Invitation-only, 2) Not yet started, 3) Ended and archived, 4) API access restricted",
                "deadline": "",
                "evaluation_metric": "",
                "access_issue": "Competition exists but API access is limited"
            }
            
    except Exception as e:
        print(f"Error fetching competition context: {e}")
        # Fallback on error
        return {
            "slug": competition_slug,
            "name": f"Competition: {competition_slug}",
            "total_notebooks": 0,
            "competition_accessible": False,
            "description": f"Error fetching competition details: {str(e)}",
            "deadline": "",
            "evaluation_metric": ""
        }

def parse_community_feedback(query: str) -> dict:
    """
    Parse user's community feedback report using LLM.
    
    Extracts:
    - Discussion title/thread
    - Community members mentioned (@username)
    - Feedback/suggestions received
    - Action type (posted, asked, commented)
    
    Args:
        query: User's natural language feedback report
    
    Returns:
        Dict with structured feedback data
    """
    import re
    from datetime import datetime
    
    try:
        # Extract discussion title (common patterns)
        title_patterns = [
            r'in the ["\']?([^"\']+?)["\']? (thread|discussion|forum)',
            r'posted in ["\']?([^"\']+?)["\']?',
            r'asked about ["\']?([^"\']+?)["\']?',
            r'discussion about ["\']?([^"\']+?)["\']?'
        ]
        
        discussion_title = "Community Discussion"
        for pattern in title_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                discussion_title = match.group(1).strip()
                break
        
        # Extract mentions (@username)
        mentions = re.findall(r'@(\w+)', query)
        
        # Determine action type
        action_type = "engaged"
        if any(word in query.lower() for word in ['i posted', 'i commented']):
            action_type = "comment"
        elif 'i asked' in query.lower():
            action_type = "question"
        elif 'upvoted' in query.lower():
            action_type = "upvote"
        
        # Extract feedback content (everything after "suggested", "said", "recommended")
        feedback_patterns = [
            r'suggested (.+)',
            r'said (.+)',
            r'recommended (.+)',
            r'advised (.+)',
            r'mentioned (.+)'
        ]
        
        community_responses = []
        for mention in mentions:
            for pattern in feedback_patterns:
                # Look for feedback from this specific person
                person_pattern = f'@{mention}[\\s\\w]*{pattern}'
                match = re.search(person_pattern, query, re.IGNORECASE)
                if match:
                    feedback = match.group(1).strip()
                    # Clean up (remove trailing punctuation, etc.)
                    feedback = re.sub(r'[.!?,;]+$', '', feedback)
                    community_responses.append({
                        'author': f'@{mention}',
                        'response': feedback,
                        'timestamp': datetime.now().isoformat()
                    })
                    break
        
        # If no structured responses found, use LLM to extract
        if not community_responses and mentions:
            # Fallback: assume everything after first mention is feedback
            for mention in mentions:
                community_responses.append({
                    'author': f'@{mention}',
                    'response': f"Provided feedback (see full context)",
                    'timestamp': datetime.now().isoformat()
                })
        
        return {
            'discussion_title': discussion_title,
            'user_action': action_type,
            'community_responses': community_responses,
            'mentions': mentions,
            'timestamp': datetime.now().isoformat(),
            'engagement_type': action_type,
            'raw_query': query
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to parse community feedback: {e}")
        return {
            'discussion_title': "Community Discussion",
            'user_action': "engaged",
            'community_responses': [],
            'mentions': [],
            'timestamp': datetime.now().isoformat(),
            'engagement_type': "comment",
            'raw_query': query,
            'parse_error': str(e)
        }


@session_bp.route("/initialize", methods=["POST"])
def initialize_session():
    """Initialize a new user session with Kaggle username and competition."""
    try:
        data = request.get_json()
        kaggle_username = data.get("kaggle_username", "").strip()
        competition_slug = data.get("competition_slug", "").strip()
        
        if not kaggle_username or not competition_slug:
            return jsonify({
                "error": "Both kaggle_username and competition_slug are required"
            }), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Fetch competition context (minimal for now)
        competition_context = fetch_competition_context(competition_slug)
        
        # Store session
        user_sessions[session_id] = {
            "session_id": session_id,
            "kaggle_username": kaggle_username,
            "competition_slug": competition_slug,
            "competition_context": competition_context,
            "fetched_data": [],
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
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
        return jsonify({
            "error": f"Session initialization failed: {str(e)}"
        }), 500

@session_bp.route("/competitions/search", methods=["POST"])
def search_competitions_route():
    """Search for Kaggle competitions."""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        
        competitions = search_kaggle_competitions(query)
        
        return jsonify({
            "success": True,
            "query": query,
            "total_found": len(competitions),
            "competitions": competitions
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Competition search failed: {str(e)}"
        }), 500

@session_bp.route("/status/<session_id>", methods=["GET"])
def get_session_status(session_id: str):
    """Get current session status."""
    try:
        if session_id not in user_sessions:
            return jsonify({
                "error": f"Session {session_id} not found"
            }), 404
        
        session_data = user_sessions[session_id]
        session_data["last_activity"] = datetime.now().isoformat()
        
        return jsonify(session_data), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get session status: {str(e)}"
        }), 500

@session_bp.route("/context/<session_id>", methods=["GET"])
def get_competition_context(session_id: str):
    """Get session context (minimal data only)."""
    try:
        if session_id not in user_sessions:
            return jsonify({
                "error": f"Session {session_id} not found"
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
    """Fetch competition data on-demand based on user query."""
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
        
        # Mock data fetching - replace with real implementation later
        fetch_results = [
            {
                "section": "overview",
                "content": f"Mock overview data for query: {user_query}",
                "source": "kaggle_api",
                "timestamp": datetime.now().isoformat()
            },
            {
                "section": "notebooks",
                "content": f"Mock notebook data for query: {user_query}",
                "source": "kaggle_api", 
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Update session with fetched data
        user_sessions[session_id]["fetched_data"].extend(fetch_results)
        user_sessions[session_id]["last_activity"] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "query": user_query,
            "sections_processed": ["overview", "notebooks"],
            "results_count": len(fetch_results),
            "data": fetch_results
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Data fetching failed: {str(e)}"
        }), 500

# Component orchestrator endpoint (mock for now)
@app.route("/component-orchestrator/query", methods=["POST"])
def handle_component_query():
    """Handle multi-agent component queries."""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()
        # Handle both 'context' and 'user_context' for compatibility
        context = data.get("context", {}) or data.get("user_context", {})
        
        if not query:
            return jsonify({
                "error": "Query is required"
            }), 400
        
        # Extract common context early so both intelligent and fallback paths can use it
        print(f"[DEBUG] Received context: {context}")
        competition_name = context.get('competition_name', 'Unknown')
        kaggle_username = context.get('kaggle_username', 'Unknown')
        competition_slug = context.get('competition_slug', 'Unknown')
        print(f"[DEBUG] Extracted - Name: {competition_name}, User: {kaggle_username}, Slug: {competition_slug}")

        # Determine intent once so both paths can use it
        # PRIORITY ORDER: error_diagnosis > code_review > community_feedback > multi_agent > discussion > notebooks > evaluation > data > strategy > explanation > technical > greeting > general
        # Code handling has highest priority when code/errors are present
        # Community feedback comes before multi_agent for reporting back from discussions
        # Multi-agent queries require orchestration (progress, ideas, stagnation, breakthroughs)
        # If user mentions "discussion", they want to browse/search discussions - even if topic is "evaluation"
        # Examples:
        #   - "ValueError: Found array with 0 samples" → Error diagnosis
        #   - "Review my code: ```python ...```" → Code review
        #   - "I posted in the Title thread, @JohnDoe suggested..." → Community feedback
        #   - "Am I stagnating?" → Multi-agent orchestration (ProgressMonitor + TimelineCoach)
        #   - "Give me ideas" → Multi-agent orchestration (IdeaInitiator + MultiHopReasoning)
        #   - "What discussions are there involving evaluation?" → Discussion handler (semantic search)
        #   - "What is the evaluation metric?" → Evaluation handler
        query_lower = query.lower()
        
        # Check for error diagnosis intent FIRST (highest priority for code with errors)
        has_error_keywords = any(word in query_lower for word in ['error', 'exception', 'traceback', 'valueerror', 'keyerror', 'typeerror', 'failed', 'not working', 'bug', 'issue'])
        has_code_block = '```' in query or 'import ' in query or 'def ' in query
        
        if has_error_keywords:
            response_type = "error_diagnosis"
        elif any(word in query_lower for word in ['review my code', 'check my code', 'feedback on code', 'code review', 'improve my code', 'optimize', 'refactor']) or (has_code_block and any(word in query_lower for word in ['review', 'check', 'feedback', 'improve', 'better', 'wrong'])):
            response_type = "code_review"
        elif any(word in query_lower for word in ['i posted', 'i asked', 'i commented', 'they suggested', 'they said', 'community said', 'got feedback', 'received feedback', 'discussion feedback', '@']) and any(word in query_lower for word in ['thread', 'discussion', 'forum', 'suggested', 'recommended', 'said']):
            response_type = "community_feedback"
        elif any(word in query_lower for word in ['stagnating', 'stagnant', 'stuck', 'progress', 'how am i doing', 'am i doing well', 'ideas', 'suggest approaches', 'what should i try', 'breakthrough', 'need help', 'next step', 'give me ideas', 'generate ideas']):
            response_type = "multi_agent"
        elif any(word in query_lower for word in ['discussion', 'forum', 'pinned', 'community', 'what are people saying']):
            response_type = "community"
        elif any(word in query_lower for word in ['notebook', 'code', 'kernel', 'solution', 'example', 'implementation', 'top notebook', 'best notebook', 'winning solution', 'popular approach']):
            response_type = "notebooks"
        elif any(word in query_lower for word in ['evaluation', 'metric', 'scoring', 'score', 'how is it scored', 'judged', 'judging', 'submission format', 'submission file', 'submit', 'how to submit']):
            response_type = "evaluation"
        elif any(word in query_lower for word in ['data', 'dataset', 'features', 'columns', 'what data', 'file', 'files', 'csv', 'json', 'train.csv', 'test.csv', 'size', 'big', 'how big', 'download']):
            response_type = "data_analysis"
        elif any(word in query_lower for word in ['get started', 'getting started', 'how do i start', 'how should i start', 'where do i begin', 'where should i begin', 'first steps', 'starting out']):
            response_type = "getting_started"
        elif any(word in query_lower for word in ['approach', 'strategy', 'how to', 'recommend', 'advice', 'what should i do']):
            response_type = "strategy"
        elif any(word in query_lower for word in ['explain', 'what is', 'about', 'describe', 'overview']):
            response_type = "explanation"
        elif any(word in query_lower for word in ['model', 'algorithm', 'technique', 'ml model']):
            response_type = "technical"
        elif query_lower in ['hi', 'hello', 'hey', 'hi there']:
            response_type = "greeting"
        else:
            response_type = "general"
        
        # ⚡ SMART CACHE OPTIMIZATION: Check for cached detailed responses first
        # First query: Full analysis (25-30s) → Caches detailed agent response
        # Repeated queries: Return cached analysis (1-2s) → SAME quality, much faster!
        # Complex queries always use full orchestration for thorough analysis
        is_simple_query = response_type in ["evaluation", "data_analysis"] and not has_code_block
        
        if is_simple_query and CHROMADB_AVAILABLE and chromadb_pipeline:
            # Check if we have a cached AGENT-GENERATED response (not just raw data)
            try:
                # Create a cache key based on query type and competition
                cache_key = f"{competition_slug}_{response_type}_response"
                
                print(f"[SMART CACHE] Checking for cached response: {cache_key}")
                
                # Query ChromaDB for cached agent response
                # We look for metadata indicating this is a complete agent analysis
                results = chromadb_pipeline.query(
                    query_texts=[query],
                    n_results=3,
                    where={
                        "competition_slug": competition_slug,
                        "section": "evaluation" if response_type == "evaluation" else "data",
                        "source": "agent_analysis"  # Only get agent-generated responses
                    }
                )
                
                if results and results.get('documents') and results['documents'][0]:
                    cached_response = results['documents'][0][0]
                    print(f"[SMART CACHE HIT] Found cached agent response ({len(cached_response)} chars) - returning detailed analysis!")
                    
                    # 🔧 DEBUG: Record execution trace for cache hit
                    query_id = str(uuid.uuid4())
                    execution_trace = {
                        "query_id": query_id,
                        "query": query,
                        "timestamp": datetime.now().isoformat(),
                        "agents_used": ["cached_agent_response"],
                        "nodes": ["preprocessing", "cache_lookup", "aggregation"],
                        "response_time_ms": 0,
                        "cache_hit": True,
                        "response_type": response_type
                    }
                    execution_traces[query_id] = execution_trace
                    
                    # Limit trace storage
                    if len(execution_traces) > MAX_TRACES:
                        oldest_key = list(execution_traces.keys())[0]
                        del execution_traces[oldest_key]
                    
                    # Return the full detailed response from cache
                    return jsonify({
                        "final_response": cached_response,
                        "response_time_ms": 0,
                        "agents_used": ["cached_agent_response"],
                        "fast_path": True,
                        "cache_hit": True,
                        "query_id": query_id  # Include query_id for trace lookup
                    }), 200
                else:
                    print(f"[SMART CACHE MISS] No cached agent response found - will use full path to generate and cache")
                    # Fall through to full orchestration which will:
                    # 1. Scrape if needed
                    # 2. Run agent analysis  
                    # 3. Cache the detailed response for next time
                    
            except Exception as e:
                print(f"[SMART CACHE ERROR] Cache check failed: {e}")
                # Fall through to full orchestration
        
        # ⚡ END SMART CACHE CHECK
        
        # Use real multi-agent system if available
        if MULTIAGENT_AVAILABLE and multiagent_orchestrator:
            try:
                # For now, use a simplified approach that works with our current setup
                # TODO: Fix LLM model names and re-enable full multi-agent system
                
                # Create an intelligent response based on the query and context
                
                # Fetch real competition data from Kaggle API
                competition_details = {}
                if KAGGLE_API_AVAILABLE:
                    try:
                        print(f"[DEBUG] Fetching competition details for: {competition_slug}")
                        competition_details = api_get_competition_details(competition_slug)
                        print(f"[DEBUG] Competition details received: {competition_details}")
                        if not competition_details:
                            print("[DEBUG] WARNING: Competition details is empty!")
                    except Exception as e:
                        print(f"[ERROR] Error fetching competition details: {e}")
                        competition_details = {}
                else:
                    print("[DEBUG] Kaggle API not available, using empty competition details")
                
                # Get detailed information using scraping system
                scraped_details = {}
                if SCRAPING_AVAILABLE:
                    try:
                        print(f"[DEBUG] Attempting to scrape competition details for: {competition_slug}")
                        scraped_details = get_detailed_competition_info(competition_slug)
                        print(f"[DEBUG] Scraping result: success={scraped_details.get('scraped_successfully', False)}")
                    except Exception as e:
                        print(f"[ERROR] Error calling scraping function: {e}")
                        scraped_details = {'scraped_successfully': False, 'error': str(e)}
                else:
                    print("[DEBUG] Scraping not available")
                
                # Analyze the query intent and provide contextual response (uses response_type determined earlier)
                
                # Generate contextual response
                if response_type == "evaluation":
                    eval_metric = competition_details.get('evaluation_metric', competition_details.get('evaluationMetric', 'Not specified in API'))
                    deadline = competition_details.get('deadline', 'Not specified')
                    category = competition_details.get('category', 'Not specified')
                    description = competition_details.get('description', '')
                    
                    print(f"[DEBUG] Evaluation response - Metric from API: {eval_metric}")
                    
                    # Try to get detailed evaluation info from scraping
                    detailed_evaluation = ""
                    if scraped_details.get('scraped_successfully'):
                        print("[DEBUG] Scraping was successful, checking for evaluation info")
                        if scraped_details.get('evaluation_info'):
                            detailed_evaluation = scraped_details['evaluation_info'].get('detailed_evaluation', '')
                            print(f"[DEBUG] Found scraped evaluation text: {len(detailed_evaluation)} chars")
                        else:
                            print("[DEBUG] No evaluation_info in scraped_details")
                    else:
                        print(f"[DEBUG] Scraping failed or not available: {scraped_details.get('error', 'Unknown error')}")
                    
                    # Use CompetitionSummaryAgent for intelligent analysis
                    if AGENT_AVAILABLE and detailed_evaluation:
                        try:
                            print(f"[DEBUG] MULTI-AGENT PATH: Using CompetitionSummaryAgent for intelligent analysis")
                            print(f"[DEBUG] Input evaluation text length: {len(detailed_evaluation)} chars")
                            
                            # Load LLM and initialize agent
                            llm = get_llm_from_config("default")
                            
                            # Use ChromaDB retriever if available, otherwise fallback to mock
                            if CHROMADB_AVAILABLE and chromadb_pipeline:
                                print("[DEBUG] Using ChromaDB retriever for agent")
                                agent = CompetitionSummaryAgent(retriever=chromadb_pipeline, llm=llm)
                            else:
                                print("[DEBUG] ChromaDB not available, using mock retriever")
                                agent = CompetitionSummaryAgent(llm=llm)
                                # Fallback: Mock fetch_sections to return our scraped text
                                def mock_fetch(query_dict, top_k=5):
                                    return [{"content": detailed_evaluation}]
                                agent.fetch_sections = mock_fetch
                            
                            # Prepare query
                            query_dict = {
                                "cleaned_query": f"Explain the evaluation metric for {competition_name}",
                                "original_query": query,
                                "metadata": {
                                    "user_level": "intermediate",
                                    "tone": "helpful",
                                    "competition": competition_name,
                                    "metric": eval_metric
                                }
                            }
                            
                            # Run agent analysis
                            result = agent.run(query_dict)
                            agent_response = result.get('response', '')
                            
                            print(f"[DEBUG] Agent response length: {len(agent_response)} chars")
                            
                            # Format with competition context
                            response = f"""📊 **Evaluation Metric for {competition_name}**

**Competition Details:**
- **Metric**: {eval_metric}
- **Category**: {category}
- **Deadline**: {deadline}
- **User**: {kaggle_username}

**🎯 How Scoring Works:**

{agent_response}

*Analysis powered by AI agent using competition data from Kaggle.*"""
                            
                            # ⚡ CACHE THE DETAILED AGENT RESPONSE for fast retrieval next time
                            if CHROMADB_AVAILABLE and chromadb_pipeline:
                                try:
                                    print("[SMART CACHE] Caching detailed agent response for future fast retrieval")
                                    chromadb_pipeline.add_documents(
                                        documents=[response],
                                        metadatas=[{
                                            "competition_slug": competition_slug,
                                            "section": "evaluation",
                                            "source": "agent_analysis",
                                            "query_type": "evaluation_metric",
                                            "timestamp": datetime.now().isoformat()
                                        }],
                                        ids=[f"{competition_slug}_evaluation_response_{int(datetime.now().timestamp())}"]
                                    )
                                    print("[SMART CACHE] ✅ Agent response cached successfully")
                                except Exception as cache_error:
                                    print(f"[SMART CACHE WARNING] Failed to cache response: {cache_error}")
                            
                        except Exception as e:
                            print(f"[ERROR] Agent failed, using fallback template: {e}")
                            import traceback
                            traceback.print_exc()
                            # Fallback to template
                            response = f"""📊 **Evaluation Metric for {competition_name}**

**🎯 How Your Submission Will Be Scored:**
- **Metric**: {eval_metric if eval_metric != 'Not specified in API' else 'Check competition description'}
- **Competition**: {competition_name}
- **Category**: {category}
- **Deadline**: {deadline}

**📋 Evaluation Criteria:**
{detailed_evaluation}

*This information is based on actual competition data from Kaggle API.*"""
                    else:
                        # No agent or no detailed evaluation - use simple template
                        print(f"[DEBUG] Agent not available or no evaluation data, using template")
                        response = f"""📊 **Evaluation Metric for {competition_name}**

**🎯 How Your Submission Will Be Scored:**
- **Metric**: {eval_metric if eval_metric != 'Not specified in API' else 'Check competition description'}
- **Competition**: {competition_name}
- **Category**: {category}
- **Deadline**: {deadline}
- **User**: {kaggle_username}

**📋 Evaluation Details:**
{detailed_evaluation or 'Check the competition page for detailed evaluation criteria.'}

*This information is based on actual competition data from Kaggle API.*"""

                elif response_type == "notebooks":
                    # Handle notebook/code queries
                    print(f"[DEBUG] Handling notebooks query for: {competition_slug}")
                    
                    # Fetch and cache notebooks
                    notebooks_result = fetch_and_store_notebooks(competition_slug, max_notebooks=3, min_votes=10)
                    
                    if notebooks_result.get('success'):
                        print(f"[DEBUG] Successfully fetched {notebooks_result.get('count', 0)} notebooks")
                        
                        # Check if from cache
                        from_cache = notebooks_result.get('from_cache', False)
                        cache_status = "[CACHED]" if from_cache else "[FRESH]"
                        
                        # Retrieve from ChromaDB and use agent for intelligent analysis
                        if CHROMADB_AVAILABLE and chromadb_pipeline:
                            try:
                                query_text = f"top notebooks code for {competition_slug}"
                                retrieved_docs = chromadb_pipeline.retriever.retrieve(query_text, top_k=5)
                                
                                print(f"[DEBUG] Retrieved {len(retrieved_docs)} notebooks from ChromaDB")
                                
                                # ==========================================
                                # CACHED SEQUENTIAL ANALYSIS APPROACH
                                # ==========================================
                                import time
                                
                                cached_analyses = []
                                notebooks_to_analyze = []
                                notebook_metadata_list = []
                                
                                # Smart Progressive Loading: Extract requested number from query
                                import re
                                
                                # Check if user wants "more" notebooks
                                wants_more = any(phrase in query_lower for phrase in ['more notebook', 'additional notebook', 'show more', 'see more', 'all notebook'])
                                
                                # Extract specific number request (e.g., "top 5", "show 3 notebooks")
                                number_match = re.search(r'top\s+(\d+)|(\d+)\s+notebook|show\s+(\d+)', query_lower)
                                requested_count = None
                                if number_match:
                                    requested_count = int(number_match.group(1) or number_match.group(2) or number_match.group(3))
                                    print(f"[SMART LOADING] User requested {requested_count} notebooks")
                                
                                # Determine notebooks to process based on request
                                if requested_count:
                                    # User explicitly asked for N notebooks
                                    if wants_more:
                                        # "show more" after "top 5" -> show remaining (skip first shown)
                                        already_shown = 2  # We show 2 initially for counts > 2
                                        remaining = max(requested_count - already_shown, 0)
                                        notebooks_to_process = min(remaining, 3)  # Max 3 more (to stay under 120s)
                                        skip_first_n = already_shown
                                    else:
                                        # First request: show up to 2 for fast response
                                        notebooks_to_process = min(requested_count, 2)
                                        skip_first_n = 0
                                elif wants_more:
                                    # Generic "show more" without number
                                    notebooks_to_process = 2
                                    skip_first_n = 1
                                else:
                                    # Default: show 1 notebook
                                    notebooks_to_process = 1
                                    skip_first_n = 0
                                
                                print(f"[INFO] Processing {notebooks_to_process} notebook(s) (skipping first {skip_first_n})...", flush=True)
                                print(f"[INFO] User wants more: {wants_more}, Requested count: {requested_count}", flush=True)
                                
                                # Step 1: Check cache for each notebook (with deduplication)
                                seen_paths = set()
                                doc_count = 0
                                skipped_count = 0
                                
                                for doc in retrieved_docs:
                                    if doc_count >= notebooks_to_process:
                                        break
                                    
                                    metadata = doc.get('metadata', {})
                                    content = doc.get('content', '')
                                    
                                    title = metadata.get('title', f'Notebook {doc_count + 1}')
                                    author = metadata.get('author', 'Unknown')
                                    votes = metadata.get('votes', 0)
                                    notebook_path = metadata.get('notebook_path', '')
                                    
                                    # Skip duplicates
                                    if notebook_path in seen_paths:
                                        print(f"[SKIP] Duplicate notebook: {title}")
                                        continue
                                    
                                    seen_paths.add(notebook_path)
                                    
                                    # Skip first N notebooks if requested (for "show more")
                                    if skipped_count < skip_first_n:
                                        print(f"[SKIP] Already shown: {title}")
                                        skipped_count += 1
                                        continue
                                    
                                    doc_count += 1
                                    i = doc_count
                                    
                                    # Store metadata for display
                                    notebook_info = {
                                        'title': title,
                                        'author': author,
                                        'votes': votes,
                                        'path': notebook_path,
                                        'number': i,
                                        'content': content  # Keep original content
                                    }
                                    notebook_metadata_list.append(notebook_info)
                                    
                                    # Check if we have cached analysis
                                    cached = check_cached_notebook_analysis(notebook_path, competition_slug)
                                    
                                    if cached['found']:
                                        print(f"[CACHE HIT] Using cached analysis for: {title}")
                                        cached_analyses.append({
                                            'notebook': notebook_info,
                                            'analysis': cached['analysis'],
                                            'cached': True
                                        })
                                    else:
                                        print(f"[CACHE MISS] Need to analyze: {title}")
                                        notebooks_to_analyze.append(notebook_info)
                                
                                # Step 2: Analyze missing notebooks sequentially
                                if notebooks_to_analyze and AGENT_AVAILABLE:
                                    print(f"[INFO] Analyzing {len(notebooks_to_analyze)} uncached notebooks...")
                                    
                                    # Initialize agent once
                                    llm = get_llm_from_config("default")
                                    if CHROMADB_AVAILABLE and chromadb_pipeline:
                                        agent = NotebookExplainerAgent(retriever=chromadb_pipeline, llm=llm)
                                    else:
                                        agent = NotebookExplainerAgent(llm=llm)
                                    
                                    for notebook_info in notebooks_to_analyze:
                                        try:
                                            print(f"[ANALYZING] {notebook_info['title']}...")
                                            
                                            # Prepare single notebook for analysis
                                            # Progressive loading: 1200 chars for detailed, high-quality analysis
                                            notebook_content = f"""
=== {notebook_info['title']} ===
Author: {notebook_info['author']} | Votes: {notebook_info['votes']:,}

{notebook_info['content'][:1200]}...
"""
                                            
                                            # Prepare query for this specific notebook
                                            query_dict = {
                                                "cleaned_query": f"Analyze notebook: {notebook_info['title']}",
                                                "original_query": query,
                                                "metadata": {
                                                    "user_level": "intermediate",
                                                    "tone": "strategic and actionable",
                                                    "competition": competition_name
                                                }
                                            }
                                            
                                            # Run agent analysis (just for this notebook)
                                            # Override the agent's retrieval to use our content
                                            result = agent.explain_sections(
                                                sections=[notebook_content],
                                                metadata=query_dict['metadata']
                                            )
                                            
                                            print(f"[OK] Analysis complete ({len(result)} chars)")
                                            
                                            # Store in cache
                                            store_notebook_analysis(
                                                notebook_path=notebook_info['path'],
                                                analysis=result,
                                                notebook_metadata=notebook_info,
                                                competition_slug=competition_slug
                                            )
                                            
                                            # Add to our list
                                            cached_analyses.append({
                                                'notebook': notebook_info,
                                                'analysis': result,
                                                'cached': False
                                            })
                                            
                                            # No cooldown needed - Gemini has generous rate limits
                                            
                                        except Exception as e:
                                            print(f"[ERROR] Failed to analyze {notebook_info['title']}: {e}")
                                            # Add fallback analysis
                                            cached_analyses.append({
                                                'notebook': notebook_info,
                                                'analysis': f"Analysis unavailable for this notebook. Preview: {notebook_info['content'][:500]}...",
                                                'cached': False
                                            })
                                
                                # Step 3: Synthesize all analyses
                                if AGENT_AVAILABLE and cached_analyses:
                                    try:
                                        print(f"[SYNTHESIS] Combining {len(cached_analyses)} analyses...")
                                        
                                        # Combine all individual analyses
                                        combined_analysis = "\n\n---\n\n".join([
                                            f"**Notebook {i+1}: {item['notebook']['title']}**\n{item['analysis']}"
                                            for i, item in enumerate(cached_analyses)
                                        ])
                                        
                                        agent_response = combined_analysis
                                        print(f"[DEBUG] Final synthesis length: {len(agent_response)} chars")
                                        
                                        # Build notebook list for context
                                        notebooks_list = "\n".join([
                                            f"{nb['number']}. **{nb['title']}** by {nb['author']} ({nb['votes']:,} votes) - [View](https://www.kaggle.com/code/{nb['path']})"
                                            for nb in notebook_metadata_list
                                        ])
                                        
                                        # Smart "show more" prompt based on requested count
                                        show_more_prompt = ""
                                        if not wants_more and len(retrieved_docs) > notebooks_to_process:
                                            total_available = min(len(retrieved_docs), 5)  # Max 5 total notebooks
                                            
                                            if requested_count:
                                                # User asked for specific number (e.g., "top 5")
                                                remaining = min(requested_count - notebooks_to_process, total_available - notebooks_to_process)
                                                if remaining > 0:
                                                    show_more_prompt = f"""

---

💡 **Want the full set?** Ask *"show more notebooks"* to see {remaining} more (total {requested_count} as requested)!"""
                                            else:
                                                # Generic query, suggest 2 more
                                                remaining = min(2, total_available - notebooks_to_process)
                                                if remaining > 0:
                                                    show_more_prompt = f"""

---

💡 **Want deeper insights?** Ask *"show more notebooks"* to see {remaining} additional top-voted notebook{"s" if remaining > 1 else ""}!"""
                                        
                                        # Format with agent analysis
                                        response = f"""📓 **Top Notebooks Analysis for {competition_name}** {cache_status}

**Competition**: {competition_name} ({competition_details.get('category', 'Unknown')})
**User**: {kaggle_username}

**📊 Analyzed Notebook{'s' if notebooks_to_process > 1 else ''}:**
{notebooks_list}

---

**🎯 Strategic Analysis:**

{agent_response}

---

*Analysis powered by AI agent using notebook data from Kaggle API.*{show_more_prompt}"""
                                    
                                    except Exception as e:
                                        print(f"[ERROR] Agent failed, using fallback template: {e}")
                                        import traceback
                                        traceback.print_exc()
                                        # Fallback to simple list
                                        notebooks_section = "\n".join([
                                            f"{nb['number']}. **{nb['title']}** by {nb['author']} ({nb['votes']:,} votes) - [View](https://www.kaggle.com/code/{nb['path']})"
                                            for nb in notebook_metadata_list
                                        ])
                                        
                                        response = f"""📓 **Top Notebooks for {competition_name}** {cache_status}

**Competition**: {competition_name}
**Category**: {competition_details.get('category', 'Unknown')}
**User**: {kaggle_username}

**🏆 Most Popular Notebooks:**

{notebooks_section}

💡 **Tips:**
- These notebooks are sorted by community votes
- Check the full notebooks for detailed explanations
- Look for common patterns across top solutions

*Data retrieved from Kaggle API and cached for fast access.*"""
                                else:
                                    # No agent - use simple list
                                    print("[DEBUG] Agent not available, using simple notebook list")
                                    notebooks_section = "\n".join([
                                        f"{nb['number']}. **{nb['title']}** by {nb['author']} ({nb['votes']:,} votes) - [View](https://www.kaggle.com/code/{nb['path']})"
                                        for nb in notebook_metadata_list
                                    ])
                                    
                                    response = f"""📓 **Top Notebooks for {competition_name}** {cache_status}

**Competition**: {competition_name}
**User**: {kaggle_username}

**🏆 Most Popular Notebooks:**

{notebooks_section}

*Data retrieved from Kaggle API and cached for fast access.*"""
                            
                            except Exception as e:
                                print(f"[ERROR] Failed to retrieve notebooks from ChromaDB: {e}")
                                import traceback
                                traceback.print_exc()
                                response = f"""📓 **Top Notebooks for {competition_name}**

**Status**: Notebooks are being fetched and cached. Please try again in a moment.

**Competition**: {competition_name}
**User**: {kaggle_username}

*Tip: Ask "Show me the top notebooks" to see popular solutions.*"""
                        else:
                            response = f"""📓 **Notebooks for {competition_name}**

**Status**: ChromaDB not available. Notebooks cannot be cached.

**Competition**: {competition_name}
**User**: {kaggle_username}"""
                    else:
                        error_msg = notebooks_result.get('error', 'Unknown error')
                        response = f"""📓 **Notebooks for {competition_name}**

**Status**: Failed to fetch notebooks.
**Error**: {error_msg}

**Competition**: {competition_name}
**User**: {kaggle_username}

*Please try again or check the competition page directly on Kaggle.*"""

                elif response_type == "data_analysis":
                    # Handle data section queries using DataSectionAgent
                    print(f"[DEBUG] Handling data_analysis query for {competition_slug}")
                    
                    # Fetch data info (cached or fresh)
                    data_result = fetch_and_store_data_info(competition_slug)
                    cache_status = "💾 [Cached]" if data_result.get('from_cache') else "🔄 [Fresh]"
                    
                    if data_result['success']:
                        data_info = data_result['data_info']
                        
                        # Use DataSectionAgent for intelligent summary
                        if AGENT_AVAILABLE:
                            try:
                                # Initialize agent with LLM
                                llm = get_llm_from_config(section="default")
                                data_agent = DataSectionAgent(llm=llm)
                                
                                # Get intelligent summary
                                agent_response = data_agent.run(
                                    competition=competition_slug,
                                    files=data_info['files'],
                                    description=data_info['description'],
                                    user_query=query
                                )
                                
                                response = f"""📊 **Data Section: {competition_name}**

{cache_status}

{agent_response['summary']}

---
**📁 Files:** {data_info['file_count']} | **Total Size:** {data_info['total_size'] / (1024*1024):.1f} MB

*Data information powered by Kaggle API + intelligent scraping + ChromaDB caching*"""
                                
                                # ⚡ CACHE THE DETAILED AGENT RESPONSE for fast retrieval next time
                                if CHROMADB_AVAILABLE and chromadb_pipeline:
                                    try:
                                        print("[SMART CACHE] Caching detailed data analysis response for future fast retrieval")
                                        chromadb_pipeline.add_documents(
                                            documents=[response],
                                            metadatas=[{
                                                "competition_slug": competition_slug,
                                                "section": "data",
                                                "source": "agent_analysis",
                                                "query_type": "data_analysis",
                                                "timestamp": datetime.now().isoformat()
                                            }],
                                            ids=[f"{competition_slug}_data_response_{int(datetime.now().timestamp())}"]
                                        )
                                        print("[SMART CACHE] ✅ Data analysis response cached successfully")
                                    except Exception as cache_error:
                                        print(f"[SMART CACHE WARNING] Failed to cache response: {cache_error}")
                                
                            except Exception as e:
                                print(f"[ERROR] DataSectionAgent failed: {e}")
                                import traceback
                                traceback.print_exc()
                                # Fallback to simple response without agent
                                files_list = "\n".join([
                                    f"- **{f['name']}** ({f['size'] / 1024:.1f} KB)" 
                                    for f in data_info['files']
                                ])
                                
                                response = f"""📊 **Data Files for {competition_name}**

{cache_status}

**Available Files:**
{files_list}

**Description:**
{data_info['description'][:500] if data_info['description'] else 'No description available'}...

*Data retrieved from Kaggle API*"""
                        else:
                            # No agent available - use simple summary
                            files_list = "\n".join([
                                f"- **{f['name']}** ({f['size'] / 1024:.1f} KB)" 
                                for f in data_info['files']
                            ])
                            
                            response = f"""📊 **Data Files for {competition_name}**

{cache_status}

**Available Files:**
{files_list}

**Description:**
{data_info['description'][:500]}...

*Use API or download from Kaggle to access the data*"""
                    
                    else:
                        # Failed to fetch data
                        response = f"""⚠️ **Data Information Currently Unavailable**

Unable to fetch data files for **{competition_name}**. This might be because:
- The competition hasn't released data yet
- Data requires accepting competition rules first
- Temporary API/scraping issue

Please visit the competition page directly: https://www.kaggle.com/competitions/{competition_slug}/data

*Error: {data_result.get('error', 'Unknown')}*"""

                elif response_type == "code_review":
                    # Handle code review requests using CodeFeedbackAgent
                    print(f"[DEBUG] Handling code_review query for {competition_slug}")
                    
                    if AGENT_AVAILABLE:
                        try:
                            # Initialize CodeFeedbackAgent with powerful Groq LLM for deep code analysis
                            llm = get_llm_from_config(section="code_handling")
                            code_agent = CodeFeedbackAgent(llm=llm)
                            
                            # Prepare competition context (optional enhancement)
                            agent_context = {
                                "competition": competition_slug,
                                "competition_name": competition_name
                            }
                            
                            # Add notebook insights if available
                            if CHROMADB_AVAILABLE and chromadb_pipeline:
                                try:
                                    # Get top notebooks for context
                                    notebooks = chromadb_pipeline.retriever.retrieve(
                                        f"code notebooks for {competition_slug}",
                                        top_k=3
                                    )
                                    if notebooks:
                                        agent_context['notebooks'] = [
                                            {
                                                "title": nb.get('metadata', {}).get('title', 'Unknown'),
                                                "approach": nb.get('content', '')[:200]
                                            }
                                            for nb in notebooks[:2]
                                        ]
                                except Exception as e:
                                    print(f"[DEBUG] Could not fetch notebook context: {e}")
                            
                            # Run code feedback agent
                            agent_result = code_agent.run(query=query, context=agent_context)
                            agent_response = agent_result.get('response', '')
                            
                            # Format response
                            response = f"""💻 **Code Review for {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}

---

{agent_response}

---

*Code analysis powered by AI agent with competition-specific insights.*"""
                            
                        except Exception as e:
                            print(f"[ERROR] CodeFeedbackAgent failed: {e}")
                            import traceback
                            traceback.print_exc()
                            # Fallback response
                            response = f"""💻 **Code Review Request**

I'd be happy to review your code for **{competition_name}**, but I encountered an issue processing your request.

**Please try:**
- Paste your code in a markdown code block (triple backticks)
- Be specific about what you want reviewed
- Include any error messages if applicable

**Example:**
```
Review my code:
\```python
# Your code here
\```
```

*Error: {str(e)}*"""
                    else:
                        # Agent not available
                        response = f"""💻 **Code Review**

Code review functionality requires the AI agent system. Please ensure all dependencies are installed.

**Competition**: {competition_name}
**User**: {kaggle_username}"""

                elif response_type == "error_diagnosis":
                    # Handle error diagnosis requests using ErrorDiagnosisAgent
                    print(f"[DEBUG] Handling error_diagnosis query for {competition_slug}")
                    
                    if AGENT_AVAILABLE:
                        try:
                            # Initialize ErrorDiagnosisAgent with powerful Groq LLM for deep error analysis
                            llm = get_llm_from_config(section="code_handling")
                            error_agent = ErrorDiagnosisAgent(llm=llm)
                            
                            # Prepare competition context (optional enhancement)
                            agent_context = {
                                "competition": competition_slug,
                                "competition_name": competition_name
                            }
                            
                            # Add discussion insights for common errors if available
                            if CHROMADB_AVAILABLE and chromadb_pipeline:
                                try:
                                    # Search for similar error discussions
                                    error_discussions = chromadb_pipeline.retriever.retrieve(
                                        f"error issue bug solution {query[:100]}",
                                        top_k=3
                                    )
                                    if error_discussions:
                                        agent_context['discussions'] = [
                                            {
                                                "title": disc.get('metadata', {}).get('title', 'Unknown'),
                                                "url": disc.get('metadata', {}).get('url', '')
                                            }
                                            for disc in error_discussions[:2]
                                        ]
                                except Exception as e:
                                    print(f"[DEBUG] Could not fetch error discussion context: {e}")
                            
                            # Run error diagnosis agent
                            agent_result = error_agent.run(query=query, context=agent_context)
                            agent_response = agent_result.get('response', '')
                            
                            # Format response
                            response = f"""🔧 **Error Diagnosis for {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}

---

{agent_response}

---

*Error diagnosis powered by AI agent with pattern matching and community insights.*"""
                            
                        except Exception as e:
                            print(f"[ERROR] ErrorDiagnosisAgent failed: {e}")
                            import traceback
                            traceback.print_exc()
                            # Fallback response
                            response = f"""🔧 **Error Diagnosis**

I'd be happy to help diagnose your error for **{competition_name}**, but I encountered an issue processing your request.

**Please try:**
- Include the full error message/traceback
- Add the code that's causing the error
- Mention what you were trying to do

**Example:**
```
I'm getting this error:
ValueError: Found array with 0 samples

My code:
\```python
# Your code here
\```
```

*Error: {str(e)}*"""
                    else:
                        # Agent not available
                        response = f"""🔧 **Error Diagnosis**

Error diagnosis functionality requires the AI agent system. Please ensure all dependencies are installed.

**Competition**: {competition_name}
**User**: {kaggle_username}"""

                elif response_type == "multi_agent":
                    # Handle multi-agent orchestration queries (progress, ideas, stagnation, breakthroughs)
                    print(f"[DEBUG] Handling multi_agent query for {competition_slug}")
                    
                    if component_orchestrator:
                        try:
                            # Prepare comprehensive context for orchestration
                            orchestration_context = {
                                "competition": competition_slug,
                                "competition_name": competition_name,
                                "user": kaggle_username,
                                "query": query
                            }
                            
                            # Fetch competition details for evaluation metric
                            if KAGGLE_API_AVAILABLE:
                                try:
                                    comp_details = api_get_competition_details(competition_slug)
                                    orchestration_context["evaluation_metric"] = comp_details.get('evaluation_metric', 'Unknown')
                                    orchestration_context["deadline"] = comp_details.get('deadline', 'Unknown')
                                except Exception as e:
                                    print(f"[DEBUG] Could not fetch competition details: {e}")
                            
                            # Fetch leaderboard info if query is about progress
                            if any(word in query_lower for word in ['progress', 'stagnating', 'stuck', 'how am i doing']):
                                if KAGGLE_API_AVAILABLE:
                                    try:
                                        print("[DEBUG] Fetching user progress from Kaggle API...")
                                        progress_data = api_get_user_progress_summary(competition_slug)
                                        
                                        if progress_data and 'error' not in progress_data:
                                            orchestration_context['user_progress'] = {
                                                'best_score': progress_data.get('best_score'),
                                                'latest_score': progress_data.get('latest_score'),
                                                'submission_count': progress_data.get('submission_count'),
                                                'is_improving': progress_data.get('is_improving'),
                                                'stagnation_count': progress_data.get('stagnation_count'),
                                                'score_trend': progress_data.get('score_trend', 'unknown')
                                            }
                                            print(f"[DEBUG] User progress: {progress_data.get('score_trend')} - {progress_data.get('submission_count')} submissions")
                                        else:
                                            orchestration_context['user_progress'] = {'error': 'No submission data available'}
                                            print("[DEBUG] No user submissions found for this competition")
                                    except Exception as e:
                                        print(f"[DEBUG] Could not fetch user progress: {e}")
                                        orchestration_context['user_progress'] = {'error': str(e)}
                            
                            # Fetch top notebooks/approaches if query is about ideas
                            if any(word in query_lower for word in ['ideas', 'suggest', 'try', 'breakthrough']):
                                if CHROMADB_AVAILABLE and chromadb_pipeline:
                                    try:
                                        notebooks = chromadb_pipeline.retriever.retrieve(
                                            f"top approaches for {competition_slug}",
                                            top_k=5
                                        )
                                        if notebooks:
                                            orchestration_context['top_approaches'] = [
                                                {
                                                    "title": nb.get('metadata', {}).get('title', 'Unknown'),
                                                    "approach": nb.get('content', '')[:300]
                                                }
                                                for nb in notebooks[:3]
                                            ]
                                    except Exception as e:
                                        print(f"[DEBUG] Could not fetch notebook context: {e}")
                            
                            # Run ComponentOrchestrator with CrewAI/AutoGen
                            print("[DEBUG] Running ComponentOrchestrator...")
                            orchestration_result = component_orchestrator.run({
                                "query": query,
                                "mode": "crewai",  # Use CrewAI for multi-agent collaboration
                                "context": orchestration_context
                            })
                            
                            agent_response = orchestration_result.get('response', '')
                            agents_used = orchestration_result.get('agents_used', [])
                            
                            # Enrich response with expert guidelines
                            if GUIDELINE_EVALUATION_AVAILABLE:
                                try:
                                    enriched_response = enrich_response_with_guidelines(agent_response, query)
                                    evaluation = evaluate_response(agent_response, query)
                                    
                                    print(f"[DEBUG] Response quality: {evaluation['quality_level']} (score: {evaluation['score']})")
                                    
                                    # Use enriched response
                                    agent_response = enriched_response
                                except Exception as e:
                                    print(f"[DEBUG] Guideline enrichment failed: {e}")
                            
                            # Format response
                            agents_list = ", ".join(agents_used) if agents_used else "Multi-Agent System"
                            response = f"""🤖 **Multi-Agent Analysis for {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}
**Agents**: {agents_list}

---

{agent_response}

---

*This response was generated by {len(agents_used) if agents_used else 'multiple'} AI agents working together, validated against Kaggle expert guidelines.*"""
                            
                        except Exception as e:
                            print(f"[ERROR] ComponentOrchestrator failed: {e}")
                            import traceback
                            traceback.print_exc()
                            # Fallback response
                            response = f"""🤖 **Multi-Agent System**

I'd love to help analyze your progress and suggest ideas for **{competition_name}**, but I encountered an issue with the orchestration system.

**Please try:**
- "Am I stagnating?" - Check your progress
- "Give me ideas" - Get competition-specific suggestions
- "What should I try next?" - Strategic recommendations

*Error: {str(e)}*"""
                    else:
                        # Orchestrator not available
                        response = f"""🤖 **Multi-Agent System**

The multi-agent orchestration system is not available. Please ensure all dependencies are installed.

**Competition**: {competition_name}
**User**: {kaggle_username}"""

                elif response_type == "community_feedback":
                    # Handle community feedback reporting (user reports back from discussions)
                    print(f"[DEBUG] Handling community_feedback query for {competition_slug}")
                    
                    if AGENT_AVAILABLE and CHROMADB_AVAILABLE and chromadb_pipeline:
                        try:
                            # Parse feedback from natural language
                            print("[DEBUG] Parsing community feedback...")
                            feedback_data = parse_community_feedback(query)
                            print(f"[DEBUG] Extracted: {feedback_data['discussion_title']} | Mentions: {feedback_data['mentions']}")
                            
                            # Initialize CommunityEngagementAgent
                            engagement_agent = CommunityEngagementAgent(
                                chromadb_pipeline=chromadb_pipeline
                            )
                            
                            # Store engagement in ChromaDB
                            engagement_id = engagement_agent.store_engagement(
                                user=kaggle_username,
                                competition=competition_slug,
                                engagement_data=feedback_data
                            )
                            print(f"[DEBUG] Stored engagement: {engagement_id}")
                            
                            # Get user progress for context
                            progress_status = "unknown"
                            if KAGGLE_API_AVAILABLE:
                                try:
                                    progress_data = api_get_user_progress_summary(competition_slug)
                                    if progress_data and 'error' not in progress_data:
                                        progress_status = f"{progress_data.get('score_trend', 'unknown')} - {progress_data.get('submission_count', 0)} submissions"
                                except Exception as e:
                                    print(f"[DEBUG] Could not fetch progress: {e}")
                            
                            # Analyze feedback with CommunityEngagementAgent
                            print("[DEBUG] Analyzing feedback with CommunityEngagementAgent...")
                            analysis_result = engagement_agent.run(
                                input_data=query,
                                context={
                                    'mode': 'analyze_feedback',
                                    'current_approach': 'XGBoost with basic features',  # TODO: Track actual approach
                                    'progress_status': progress_status
                                }
                            )
                            
                            agent_analysis = analysis_result.get('analysis', '')
                            
                            # Enrich with expert guidelines if available
                            if GUIDELINE_EVALUATION_AVAILABLE:
                                try:
                                    enriched_analysis = enrich_response_with_guidelines(agent_analysis, query)
                                    evaluation = evaluate_response(agent_analysis, query)
                                    print(f"[DEBUG] Response quality: {evaluation['quality_level']} (score: {evaluation['score']})")
                                    agent_analysis = enriched_analysis
                                except Exception as e:
                                    print(f"[DEBUG] Guideline enrichment failed: {e}")
                            
                            # Format response
                            mentions_text = ", ".join(feedback_data['mentions']) if feedback_data['mentions'] else "community members"
                            response = f"""🤝 **Community Feedback Analyzed for {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}
**Discussion**: {feedback_data['discussion_title']}
**Community Members**: {mentions_text}

---

{agent_analysis}

---

✅ **Engagement Tracked**: This feedback has been saved for future reference. When you ask "What should I try next?", I'll remember this community-validated advice!

*Analysis powered by CommunityEngagementAgent with crowd-validated insights.*"""
                            
                        except Exception as e:
                            print(f"[ERROR] Community feedback analysis failed: {e}")
                            import traceback
                            traceback.print_exc()
                            # Fallback response
                            response = f"""🤝 **Community Feedback**

I'd love to analyze the feedback you received for **{competition_name}**, but I encountered an issue processing your report.

**Please try:**
- Include the discussion title: "I posted in the 'Feature Engineering' thread"
- Mention who responded: "@JohnDoe suggested using regex"
- Describe what they suggested: "He recommended extracting titles from names"

**Example:**
"I posted in the 'Title Feature' thread and @JohnDoe suggested using regex to extract titles. @JaneSmith said Master/Miss/Mrs are highly predictive."

*Error: {str(e)}*"""
                    else:
                        # Agent or ChromaDB not available
                        response = f"""🤝 **Community Feedback**

I'd love to track your community interactions for **{competition_name}**, but the engagement tracking system is not fully initialized.

**Competition**: {competition_name}
**User**: {kaggle_username}

Please ensure all dependencies are installed."""

                elif response_type == "community":
                    # Handle discussion/community queries
                    print(f"[DEBUG] Handling discussion query for: {competition_slug}")
                    
                    # Fetch and cache discussion metadata
                    discussions_result = fetch_and_store_discussions(competition_slug, max_discussions=20)
                    
                    if discussions_result.get('success'):
                        print(f"[DEBUG] Successfully fetched {discussions_result.get('count', 0)} discussions")
                        
                        # Check if from cache
                        from_cache = discussions_result.get('from_cache', False)
                        cache_status = "[CACHED]" if from_cache else "[FRESH]"
                        
                        # Retrieve from ChromaDB and use agent for intelligent analysis
                        if CHROMADB_AVAILABLE and chromadb_pipeline and AGENT_AVAILABLE:
                            try:
                                collection = chromadb_pipeline.retriever._get_collection()
                                
                                # Determine query type based on keywords
                                if any(word in query_lower for word in ['pinned', 'important', 'official']):
                                    # Filter for pinned discussions
                                    print("[DEBUG] Filtering for pinned discussions")
                                    query_type = "list"
                                    results = collection.query(
                                        query_embeddings=[chromadb_pipeline.retriever.embedding_model.encode("pinned discussion").tolist()],
                                        where={"$and": [
                                            {"competition_slug": competition_slug},
                                            {"section": "discussion"},
                                            {"is_pinned": True}
                                        ]},
                                        n_results=10,
                                        include=["documents", "metadatas"]
                                    )
                                elif any(word in query_lower for word in ['recent', 'latest', 'new']):
                                    # Get recent discussions
                                    print("[DEBUG] Retrieving recent discussions")
                                    query_type = "list"
                                    results = collection.query(
                                        query_embeddings=[chromadb_pipeline.retriever.embedding_model.encode("recent discussion").tolist()],
                                        where={"$and": [
                                            {"competition_slug": competition_slug},
                                            {"section": "discussion"}
                                        ]},
                                        n_results=10,
                                        include=["documents", "metadatas"]
                                    )
                                else:
                                    # Detect if this is a specific discussion request (deep dive)
                                    specific_request_keywords = ['explain', 'summarize', 'analyze', 'titled', 'about', 'regarding']
                                    is_specific_request = any(word in query_lower for word in specific_request_keywords)
                                    
                                    # Semantic search for relevant discussions
                                    print(f"[DEBUG] Semantic search for: {query}")
                                    query_type = "analyze" if is_specific_request else "list"
                                    print(f"[DEBUG] Query type: {query_type}")
                                    
                                    query_embedding = chromadb_pipeline.retriever.embedding_model.encode(query).tolist()
                                    results = collection.query(
                                        query_embeddings=[query_embedding],
                                        where={"$and": [
                                            {"competition_slug": competition_slug},
                                            {"section": "discussion"}
                                        ]},
                                        n_results=5,
                                        include=["documents", "metadatas", "distances"]
                                    )
                                
                                # Format results
                                retrieved_discussions = []
                                if results["documents"] and results["documents"][0]:
                                    for i, doc_content in enumerate(results["documents"][0]):
                                        metadata = results["metadatas"][0][i] if results["metadatas"] and results["metadatas"][0] else {}
                                        retrieved_discussions.append({
                                            "content": doc_content,
                                            "metadata": metadata
                                        })
                                
                                print(f"[DEBUG] Retrieved {len(retrieved_discussions)} discussions from ChromaDB")
                                
                                if retrieved_discussions:
                                    print(f"[DEBUG] ===== DISCUSSION HANDLING START =====")
                                    print(f"[DEBUG] Query type: {query_type}")
                                    print(f"[DEBUG] Number of discussions: {len(retrieved_discussions)}")
                                    
                                    # Check if deep scraping is needed (for analyze queries)
                                    if query_type == "analyze" and retrieved_discussions:
                                        print(f"[DEBUG] Analyze query detected - checking for deep scraping need")
                                        # Focus on the most relevant discussion (first result)
                                        top_discussion = retrieved_discussions[0]
                                        metadata = top_discussion.get("metadata", {})
                                        has_full_content = metadata.get("has_full_content", False)
                                        discussion_url = metadata.get("url", "")
                                        
                                        print(f"[DEBUG] Top discussion: {metadata.get('title', 'Unknown')}")
                                        print(f"[DEBUG] Has full content: {has_full_content}")
                                        print(f"[DEBUG] URL: {discussion_url}")
                                        print(f"[DEBUG] Deep scraping needed: {not has_full_content and bool(discussion_url)}")
                                        
                                        # Trigger deep scraping if needed
                                        if not has_full_content and discussion_url:
                                            print("[DEEP SCRAPE] Full content not available, triggering deep scrape...")
                                            try:
                                                from scraper.discussion_scraper_playwright import DiscussionScraperPlaywright
                                                scraper = DiscussionScraperPlaywright(competition_slug=competition_slug)
                                                
                                                # Scrape full discussion
                                                full_discussion_data = scraper.scrape_full_discussion(discussion_url)
                                                
                                                if full_discussion_data:
                                                    print(f"[DEEP SCRAPE] Success! Found {len(full_discussion_data.get('comments', []))} comments")
                                                    
                                                    # Process OCR if screenshots present
                                                    ocr_text = ""
                                                    screenshot_urls = full_discussion_data.get('screenshot_urls', [])
                                                    if screenshot_urls:
                                                        print(f"[OCR] Processing {len(screenshot_urls)} screenshot(s)...")
                                                        try:
                                                            from scraper.screenshots_handler import extract_text_from_screenshots
                                                            
                                                            # Prepare post for OCR handler
                                                            ocr_post = {
                                                                'title': full_discussion_data.get('title', ''),
                                                                'content': full_discussion_data.get('content', ''),
                                                                'has_screenshot': True,
                                                                'screenshot_urls': screenshot_urls
                                                            }
                                                            
                                                            # Extract text from screenshots
                                                            ocr_result = extract_text_from_screenshots(ocr_post)
                                                            raw_ocr_text = ocr_result.get('ocr_text', '')
                                                            
                                                            if raw_ocr_text:
                                                                # Limit to ~2 sentences or 200 chars
                                                                sentences = raw_ocr_text.replace('\n', ' ').split('. ')
                                                                if len(sentences) >= 2:
                                                                    ocr_text = '. '.join(sentences[:2]) + '.'
                                                                else:
                                                                    ocr_text = raw_ocr_text[:200] + ('...' if len(raw_ocr_text) > 200 else '')
                                                                print(f"[OCR] Extracted {len(raw_ocr_text)} chars, limited to {len(ocr_text)} chars")
                                                            else:
                                                                print(f"[OCR] No text extracted from screenshots")
                                                        except Exception as e:
                                                            print(f"[OCR] Failed: {e}")
                                                    
                                                    # Build full content with OCR text if available
                                                    ocr_section = ""
                                                    if ocr_text:
                                                        ocr_section = f"""

**Screenshot Content (OCR):**
{ocr_text}
"""
                                                    
                                                    # Update ChromaDB with full content
                                                    full_content = f"""**{full_discussion_data.get('title', metadata.get('title', 'Unknown'))}**
Author: {metadata.get('author', 'Unknown')}
Date: {metadata.get('date', 'Unknown')}

**Post Content:**
{full_discussion_data.get('content', 'No content available')}{ocr_section}

**Comments ({len(full_discussion_data.get('comments', []))}):**
{chr(10).join([f"- **{c.get('author', 'Unknown')}**: {c.get('content', '')[:200]}..." for c in full_discussion_data.get('comments', [])[:5]])}"""
                                                    
                                                    # Update the top discussion with full content
                                                    top_discussion['content'] = full_content
                                                    top_discussion['metadata']['has_full_content'] = True
                                                    top_discussion['metadata']['deep_scraped'] = True
                                                    top_discussion['metadata']['has_screenshot'] = full_discussion_data.get('has_screenshot', False)
                                                    
                                                    # Update ChromaDB
                                                    try:
                                                        # Use existing ChromaDB pipeline indexer
                                                        indexer = chromadb_pipeline.indexer
                                                        
                                                        # Create document for indexing
                                                        doc = {
                                                            'content': full_content,
                                                            'metadata': top_discussion['metadata'],
                                                            'section': 'discussion'
                                                        }
                                                        
                                                        indexer.index_documents(
                                                            documents=[doc],
                                                            competition_slug=competition_slug
                                                        )
                                                        print("[DEEP SCRAPE] ChromaDB updated with full content")
                                                    except Exception as e:
                                                        print(f"[DEEP SCRAPE] Failed to update ChromaDB: {e}")
                                                else:
                                                    print("[DEEP SCRAPE] No content returned from scraper")
                                            except Exception as e:
                                                print(f"[DEEP SCRAPE] Failed: {e}")
                                                import traceback
                                                traceback.print_exc()
                                    
                                    # Initialize Discussion Helper Agent
                                    llm = get_llm_from_config("default")
                                    discussion_agent = DiscussionHelperAgent(
                                        retriever=chromadb_pipeline.retriever,
                                        llm=llm
                                    )
                                    
                                    # For analyze queries, only pass the top discussion
                                    discussions_to_analyze = retrieved_discussions
                                    if query_type == "analyze":
                                        discussions_to_analyze = [retrieved_discussions[0]]
                                        print(f"[DEBUG] Analyze mode: passing only top discussion to agent")
                                    
                                    # Run agent
                                    agent_result = discussion_agent.run(
                                        discussions=discussions_to_analyze,
                                        user_query=query,
                                        competition=competition_slug,
                                        query_type=query_type
                                    )
                                    
                                    response = f"""💬 **Community Discussions for {competition_name}**

{agent_result['response']}

---
*{cache_status} Retrieved {agent_result['discussions_count']} discussions, showing most relevant.*"""
                                    
                                else:
                                    response = f"""💬 **Community Discussions for {competition_name}**

No discussions found matching your query. The community might not have discussed this topic yet, or discussions are still being indexed.

**Suggestions:**
- Try a broader search term
- Check pinned discussions for important updates
- Visit the competition page directly for the latest discussions

*Competition*: {competition_name}  
*User*: {kaggle_username}"""
                                
                            except Exception as e:
                                print(f"[ERROR] Discussion agent failed: {e}")
                                import traceback
                                traceback.print_exc()
                                response = f"""💬 **Community Discussions for {competition_name}**

Retrieved {discussions_result.get('count', 0)} discussions, but analysis failed.

**Available Discussions:** {discussions_result.get('count', 0)}
- Pinned: {discussions_result.get('pinned_count', 0)}
- Total: {discussions_result.get('count', 0)}

Please visit the competition page to view discussions directly.

*Error*: {str(e)}"""
                        else:
                            # ChromaDB or agent not available - show basic info
                            response = f"""💬 **Community Discussions for {competition_name}**

**Discussion Status:**
- Total discussions: {discussions_result.get('count', 0)}
- Pinned discussions: {discussions_result.get('pinned_count', 0)}
- Cache status: {cache_status}

**Next Steps:**
- Visit the competition discussion page
- Check pinned posts for important updates
- Engage with the community

*Competition*: {competition_name}  
*User*: {kaggle_username}"""
                    else:
                        # Failed to fetch discussions
                        error_msg = discussions_result.get('error', 'Unknown error')
                        response = f"""💬 **Community Discussions for {competition_name}**

Unable to fetch discussions at this time.

**Error:** {error_msg}

**Suggestions:**
- Visit the competition page directly
- Check your internet connection
- Try again in a moment

*Competition*: {competition_name}  
*User*: {kaggle_username}"""

                elif response_type == "greeting":
                    response = f"""👋 **Welcome to Kaggle Competition Assistant!**

**🎯 Ready to help with {competition_name}**
- **User**: {kaggle_username}
- **Competition**: {competition_name}

**🚀 What can I help you with today?**
- 🤖 **Multi-Agent Analysis**: "Am I stagnating?" or "Give me ideas"
- 🤝 **Community Feedback**: "I posted in the Title thread, @JohnDoe suggested..."
- 📊 **Data Analysis**: "What data files are available?"
- 🎯 **Strategy**: "How should I approach this competition?"
- 💻 **Code Review**: "Review my code: ```python ...```"
- 🔧 **Error Diagnosis**: "I'm getting ValueError: ..."
- 📈 **Evaluation**: "What is the evaluation metric?"
- 📓 **Notebooks**: "Show me top notebooks"
- 💬 **Community**: "What are people discussing?"

**💡 Quick Start:**
1. Ask about the competition overview
2. Understand the evaluation metric
3. Explore the dataset
4. Get code feedback and error help
5. Review top notebooks
6. Check community discussions
7. Get multi-agent progress analysis and ideas
8. Report back community feedback for personalized guidance

**🎊 Let's make this competition a success!** Ask me anything about your approach, code, or strategy."""
                
                elif response_type == "getting_started":
                    # Handle "how to get started" queries intelligently
                    print(f"[DEBUG] Handling getting_started query for {competition_slug}")
                    if AGENT_AVAILABLE and CHROMADB_AVAILABLE and chromadb_pipeline:
                        try:
                            # Get overview and notebook context
                            overview_results = chromadb_pipeline.retriever._get_collection().query(
                                query_texts=[f"getting started with {competition_slug}"],
                                n_results=5,
                                where={
                                    "$and": [
                                        {"competition_slug": competition_slug},
                                        {"section": "overview"}
                                    ]
                                }
                            )
                            
                            notebook_context = chromadb_pipeline.retriever.retrieve(
                                f"beginner friendly starter approaches for {competition_slug}",
                                top_k=3
                            )
                            
                            context_str = ""
                            if overview_results and overview_results['documents'] and overview_results['documents'][0]:
                                context_str = "Competition Overview:\n" + "\n".join([
                                    doc for doc in overview_results['documents'][0][:2]
                                    if doc and len(doc) > 50
                                ])
                            
                            if notebook_context:
                                context_str += "\n\nCommon Starting Approaches:\n" + "\n".join([
                                    f"- {doc.get('content', '')[:200]}"
                                    for doc in notebook_context[:2]
                                ])
                            
                            llm = get_llm_from_config(section="retrieval_agents")
                            agent = CompetitionSummaryAgent(llm=llm)
                            
                            analysis_prompt = f"""User Query: {query}
Competition: {competition_name}

Context:
{context_str if context_str else 'No cached data yet'}

Provide practical, actionable advice for getting started that:
1. Recommends specific first steps (e.g., "Load train.csv and check for missing values in Age, Cabin")
2. References actual competition details (files, metrics, deadlines)
3. Suggests 2-3 concrete starter approaches from successful notebooks
4. Prioritizes quick wins to build momentum
5. Is encouraging and beginner-friendly

Be specific to THIS competition, not generic advice."""
                            
                            result = agent.summarize_sections(
                                sections=[{"content": analysis_prompt, "title": "Getting Started"}],
                                metadata={"competition": competition_slug}
                            )
                            
                            response = f"""🚀 **Getting Started with {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}

---

{result}

---

*Personalized getting started guide powered by AI agent with competition-specific insights.*"""
                        
                        except Exception as e:
                            print(f"[ERROR] Getting started agent failed: {e}")
                            import traceback
                            traceback.print_exc()
                            response = None
                    else:
                        response = None
                    
                    if not response:
                        response = f"""🚀 **Getting Started with {competition_name}**

I'd love to give you personalized advice for getting started with **{competition_name}**, but the intelligent analysis system isn't available right now.

**Your question**: {query}

**To get started**, try:
- "What data files are available?"
- "What is the evaluation metric?"
- "Show me top notebooks for beginners"

*Requires agent system to be fully available.*"""
                
                elif response_type == "strategy":
                    # Handle strategy/approach questions intelligently
                    print(f"[DEBUG] Handling strategy query for {competition_slug}")
                    
                    if AGENT_AVAILABLE and CHROMADB_AVAILABLE and chromadb_pipeline:
                        try:
                            # Retrieve relevant notebook insights for context
                            notebook_context = chromadb_pipeline.retriever.retrieve(
                                f"best approaches and strategies for {competition_slug}",
                                top_k=5
                            )
                            
                            # Build context from notebooks
                            context_str = ""
                            if notebook_context:
                                context_str = "\n\n".join([
                                    f"**Approach {i+1}**: {doc.get('content', '')[:300]}"
                                    for i, doc in enumerate(notebook_context[:3])
                                ])
                            
                            # Use CompetitionSummaryAgent for intelligent analysis
                            llm = get_llm_from_config(section="retrieval_agents")
                            agent = CompetitionSummaryAgent(llm=llm)
                            
                            # Create prompt that respects user's input
                            analysis_prompt = f"""User Query: {query}

Competition: {competition_name}

Relevant approaches from top notebooks:
{context_str if context_str else 'No cached notebooks yet'}

Provide intelligent, contextual advice that:
1. Directly addresses the user's specific question
2. Acknowledges any approaches they mentioned
3. Builds on their ideas rather than ignoring them
4. Provides actionable, competition-specific recommendations
5. References concrete strategies from successful notebooks when relevant

Be collaborative, not prescriptive. If the user mentioned an approach, evaluate it thoughtfully."""
                            
                            result = agent.summarize_sections(
                                sections=[{"content": analysis_prompt, "title": "Strategy Analysis"}],
                                metadata={"competition": competition_slug}
                            )
                            
                            response = f"""🎯 **Strategic Advice for {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}

---

{result}

---

*Analysis powered by AI agent with insights from top-performing notebooks.*"""
                            
                        except Exception as e:
                            print(f"[ERROR] Strategy agent failed: {e}")
                            import traceback
                            traceback.print_exc()
                            # Fallback to general intelligent handler below
                            response = None
                    else:
                        response = None
                    
                    # If agent not available or failed, use fallback
                    if not response:
                        response = f"""🎯 **Strategy Advice for {competition_name}**

I'd love to help with your strategy for **{competition_name}**, but the intelligent analysis system isn't available right now.

**Your question**: {query}

**To get better help**, try:
- "What notebooks work best for this competition?"
- "How should I approach feature engineering?"
- "What models perform well here?"

*Requires agent system to be fully available.*"""
                
                elif response_type == "explanation":
                    # Handle overview/explanation questions intelligently
                    print(f"[DEBUG] Handling explanation/overview query for {competition_slug}")
                    
                    # Try to get Kaggle API details first for fallback
                    competition_details = {}
                    try:
                        competition_details = api_get_competition_details(competition_slug)
                    except Exception as e:
                        print(f"[DEBUG] Could not get API details: {e}")
                    
                    if AGENT_AVAILABLE and CHROMADB_AVAILABLE and chromadb_pipeline:
                        try:
                            # Query ChromaDB for overview content
                            overview_results = chromadb_pipeline.retriever._get_collection().query(
                                query_texts=[query],
                                n_results=10,
                                where={
                                    "$and": [
                                        {"competition_slug": competition_slug},
                                        {"section": "overview"}
                                    ]
                                }
                            )
                            
                            # Build context from overview sections
                            context_str = ""
                            if overview_results and overview_results['documents'] and overview_results['documents'][0]:
                                cached_docs = [
                                    doc for doc in overview_results['documents'][0][:5]
                                    if doc and len(doc) > 50  # Filter out tiny/useless sections
                                ]
                                if cached_docs:
                                    context_str = "\n\n".join(cached_docs)
                            
                            # If no cached overview, use API details
                            if not context_str and competition_details:
                                context_str = f"""Competition: {competition_details.get('name', competition_name)}
Description: {competition_details.get('description', 'N/A')}
Category: {competition_details.get('category', 'N/A')}
Deadline: {competition_details.get('deadline', 'N/A')}
Evaluation: {competition_details.get('evaluation_metric', 'N/A')}
Reward: {competition_details.get('reward', 'N/A')}"""
                            
                            # Use CompetitionSummaryAgent for intelligent synthesis
                            llm = get_llm_from_config(section="retrieval_agents")
                            agent = CompetitionSummaryAgent(llm=llm)
                            
                            # Create prompt
                            analysis_prompt = f"""User Query: {query}

Competition: {competition_name}

Competition Information:
{context_str if context_str else 'Limited information available'}

Provide a clear, informative explanation that:
1. Directly answers the user's question
2. Provides competition-specific details from the available information
3. Explains the competition's objectives and goals
4. Is helpful and encouraging

Be conversational and informative. If limited data is available, be honest but still helpful."""
                            
                            result = agent.summarize_sections(
                                sections=[{"content": analysis_prompt, "title": "Overview"}],
                                metadata={"competition": competition_slug}
                            )
                            
                            response = f"""📚 **Competition Overview: {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}

---

{result}

---

*Overview powered by AI agent with competition data.*"""
                            
                        except Exception as e:
                            print(f"[ERROR] Explanation agent failed: {e}")
                            import traceback
                            traceback.print_exc()
                            response = None
                    else:
                        response = None
                    
                    # If agent not available or failed, build intelligent fallback from API
                    if not response and competition_details:
                        desc = competition_details.get('description', '')
                        category = competition_details.get('category', 'Data Science')
                        deadline = competition_details.get('deadline', 'No deadline specified')
                        metric = competition_details.get('evaluation_metric', 'See competition page')
                        
                        response = f"""📚 **Competition Overview: {competition_name}**

**Competition**: {competition_name}
**Category**: {category}
**Deadline**: {deadline}
**User**: {kaggle_username}

---

**📖 About This Competition:**

{desc if desc else f"The {competition_name} is a {category} competition on Kaggle."}

**🎯 Evaluation:**
This competition uses **{metric}** to evaluate submissions.

**🚀 Getting Started:**
1. Download the competition data
2. Explore the dataset and understand the features
3. Review top notebooks for approaches
4. Build a baseline model and iterate

**💡 Next Steps:**
- Ask: "What data files are available?"
- Ask: "Show me top notebooks"
- Ask: "What approaches work well?"

---

*Information from Kaggle API. For detailed analysis, the AI agent system needs to be available.*"""
                    
                    # Ultimate fallback if no data at all
                    if not response:
                        response = f"""📚 **Competition Overview: {competition_name}**

I'd love to explain **{competition_name}** in detail, but I couldn't retrieve competition information right now.

**Your question**: {query}

**To get better information**, try:
- "What is the evaluation metric?"
- "Show me the top notebooks"
- "What data files are available?"

*Requires agent system and competition data to be available.*"""
                
                elif response_type == "technical":
                    # Handle technical/model questions intelligently
                    print(f"[DEBUG] Handling technical query for {competition_slug}")
                    
                    if AGENT_AVAILABLE and CHROMADB_AVAILABLE and chromadb_pipeline:
                        try:
                            # Retrieve relevant technical approaches from notebooks
                            notebook_context = chromadb_pipeline.retriever.retrieve(
                                f"models algorithms and techniques for {competition_slug}",
                                top_k=5
                            )
                            
                            # Build context from notebooks
                            context_str = ""
                            if notebook_context:
                                context_str = "\n\n".join([
                                    f"**Technical approach {i+1}**: {doc.get('content', '')[:300]}"
                                    for i, doc in enumerate(notebook_context[:3])
                                ])
                            
                            # Use CompetitionSummaryAgent for intelligent analysis
                            llm = get_llm_from_config(section="retrieval_agents")
                            agent = CompetitionSummaryAgent(llm=llm)
                            
                            # Create prompt that respects user's input
                            analysis_prompt = f"""User Query: {query}

Competition: {competition_name}

Technical approaches from successful notebooks:
{context_str if context_str else 'No cached notebooks yet'}

Provide intelligent technical advice that:
1. Directly addresses the user's specific question
2. Acknowledges any techniques or models they mentioned
3. Evaluates their approach thoughtfully
4. Provides competition-specific model/algorithm recommendations
5. References what actually works well in this competition based on notebooks

Be collaborative and respectful of their technical choices. Build on their ideas."""
                            
                            result = agent.summarize_sections(
                                sections=[{"content": analysis_prompt, "title": "Technical Analysis"}],
                                metadata={"competition": competition_slug}
                            )
                            
                            response = f"""⚙️ **Technical Advice for {competition_name}**

**Competition**: {competition_name}
**User**: {kaggle_username}

---

{result}

---

*Technical analysis powered by AI agent with insights from top-performing notebooks.*"""
                            
                        except Exception as e:
                            print(f"[ERROR] Technical agent failed: {e}")
                            import traceback
                            traceback.print_exc()
                            # Fallback to general intelligent handler below
                            response = None
                    else:
                        response = None
                    
                    # If agent not available or failed, use fallback
                    if not response:
                        response = f"""⚙️ **Technical Advice for {competition_name}**

I'd love to help with technical recommendations for **{competition_name}**, but the intelligent analysis system isn't available right now.

**Your question**: {query}

**To get better help**, try:
- "Show me top notebooks for this competition"
- "What models work well here?"
- "How do successful solutions handle feature engineering?"

*Requires agent system to be fully available.*"""
                
                else:  # general
                    response = f"""🤖 **AI Assistant Response for {competition_name}**

**📋 Competition Context:**
- Competition: {competition_name}
- User: {kaggle_username}
- Slug: {competition_slug}

**💬 Your Query:** "{query}"

**🎯 Intelligent Analysis:**
Based on your question about "{query}", here's my comprehensive response:

**🔍 Understanding Your Request:**
Your query suggests you're looking for guidance on this Kaggle competition. This is a great starting point for your data science journey!

**📚 Recommended Actions:**
1. **Explore the Data**: Download and examine the competition datasets
2. **Read Documentation**: Study the competition description and evaluation criteria
3. **Learn from Others**: Review successful kernels and discussions
4. **Start Simple**: Begin with a basic approach and iterate
5. **Join Community**: Engage with other participants for insights

**🚀 Next Steps:**
- Familiarize yourself with the competition structure
- Set up your development environment
- Create your first submission
- Iterate and improve based on feedback

**💡 Pro Tips:**
- Start with exploratory data analysis
- Build a robust baseline model
- Focus on feature engineering
- Use cross-validation for model selection
- Learn from leaderboard analysis

*This response is generated by the intelligent multi-agent reasoning system, designed to provide comprehensive guidance for Kaggle competitions.*"""

                return jsonify({
                    "success": True,
                    "query": query,
                    "final_response": response,
                    "timestamp": datetime.now().isoformat(),
                    "agents_used": ["intelligent_reasoning_agent"],
                    "confidence": 0.85,
                    "system": "intelligent_multiagent"
                }), 200
                
            except Exception as e:
                print(f"Multi-agent system error: {e}")
                import traceback
                traceback.print_exc()
                # Fall back to mock response if multi-agent fails
                pass
        
        # Fallback response when multi-agent is unavailable or fails
        # For evaluation queries, build a real answer using Kaggle API + scraper
        if response_type == "evaluation":
            # Fetch details from Kaggle API
            competition_details = {}
            if KAGGLE_API_AVAILABLE:
                try:
                    competition_details = api_get_competition_details(competition_slug)
                except Exception as e:
                    print(f"[ERROR] Fallback: error fetching competition details: {e}")
                    competition_details = {}

            # Scrape evaluation details
            scraped_details = {}
            if SCRAPING_AVAILABLE:
                try:
                    print(f"[DEBUG] Fallback path: scraping evaluation for {competition_slug}")
                    scraped_details = get_detailed_competition_info(competition_slug)
                except Exception as e:
                    print(f"[ERROR] Fallback: scraping failed: {e}")
                    scraped_details = {'scraped_successfully': False, 'error': str(e)}

            eval_metric = (competition_details or {}).get('evaluation_metric', (competition_details or {}).get('evaluationMetric', 'Not specified in API'))
            deadline = (competition_details or {}).get('deadline', 'Not specified')
            category = (competition_details or {}).get('category', 'Not specified')

            detailed_evaluation = ""
            if scraped_details.get('scraped_successfully') and scraped_details.get('evaluation_info'):
                detailed_evaluation = scraped_details['evaluation_info'].get('detailed_evaluation', '')

            # Use CompetitionSummaryAgent for intelligent analysis
            if AGENT_AVAILABLE and detailed_evaluation:
                try:
                    print(f"[DEBUG] Using CompetitionSummaryAgent for intelligent analysis")
                    print(f"[DEBUG] Input evaluation text length: {len(detailed_evaluation)} chars")
                    
                    # Load LLM and initialize agent
                    llm = get_llm_from_config("default")
                    agent = CompetitionSummaryAgent(llm=llm)
                    
                    # Mock fetch_sections to return our scraped text
                    def mock_fetch(query_dict, top_k=5):
                        return [{"content": detailed_evaluation}]
                    agent.fetch_sections = mock_fetch
                    
                    # Prepare query
                    query_dict = {
                        "cleaned_query": f"Explain the evaluation metric for {competition_name}",
                        "original_query": query,
                        "metadata": {
                            "user_level": "intermediate",
                            "tone": "helpful",
                            "competition": competition_name,
                            "metric": eval_metric
                        }
                    }
                    
                    # Run agent analysis
                    result = agent.run(query_dict)
                    agent_response = result.get('response', '')
                    
                    print(f"[DEBUG] Agent response length: {len(agent_response)} chars")
                    
                    # Format with competition context
                    response = f"""📊 **Evaluation Metric for {competition_name}**

**Competition Details:**
- **Metric**: {eval_metric}
- **Category**: {category}
- **Deadline**: {deadline}
- **User**: {kaggle_username}

**🎯 How Scoring Works:**

{agent_response}

*Analysis powered by AI agent using competition data from Kaggle.*"""
                    
                except Exception as e:
                    print(f"[ERROR] Agent failed, using fallback: {e}")
                    import traceback
                    traceback.print_exc()
                    # Fallback to simple template
                    response = f"""📊 **Evaluation Metric for {competition_name}**

**🎯 How Your Submission Will Be Scored:**
- **Metric**: {eval_metric if eval_metric != 'Not specified in API' else 'Check competition description'}
- **Competition**: {competition_name}
- **Category**: {category}
- **Deadline**: {deadline}

**📋 Evaluation Criteria:**
{detailed_evaluation}
"""
            else:
                # No agent or no scraped data - use simple template
                print(f"[DEBUG] Agent not available or no evaluation data scraped")
                response = f"""📊 **Evaluation Metric for {competition_name}**

**🎯 How Your Submission Will Be Scored:**
- **Metric**: {eval_metric if eval_metric != 'Not specified in API' else 'Check competition description'}
- **Competition**: {competition_name}
- **Category**: {category}
- **Deadline**: {deadline}

**📋 Evaluation Details:**
{detailed_evaluation or 'Check the competition page for detailed evaluation criteria.'}
"""
        else:
            response = (
                f"🎯 Multi-agent analysis for: '{query}'\n\n"
                f"📊 Competition Context: {competition_name}\n"
                f"👤 User: {kaggle_username}\n\n"
                f"🤖 **AI Analysis:**\n"
                f"Based on your query about '{query}', here's what I recommend:\n\n"
                f"1. **Data Exploration**: Start by understanding the competition dataset\n"
                f"2. **Notebook Analysis**: Review top-performing notebooks for insights\n"
                f"3. **Feature Engineering**: Focus on creating meaningful features\n"
                f"4. **Model Selection**: Try different algorithms and ensemble methods\n\n"
                f"💡 **Next Steps:**\n"
                f"- Explore the competition data\n"
                f"- Study successful approaches\n"
                f"- Build and iterate on your model\n"
            )

        # 🔧 DEBUG: Record execution trace for LangGraph visualization
        query_id = str(uuid.uuid4())
        execution_trace = {
            "query_id": query_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "agents_used": ["fallback_agent"],
            "nodes": ["preprocessing", "router", response_type, "aggregation"],
            "response_time_ms": 0,  # Fallback is instant
            "cache_hit": False,
            "response_type": response_type
        }
        execution_traces[query_id] = execution_trace
        
        # Limit trace storage
        if len(execution_traces) > MAX_TRACES:
            oldest_key = list(execution_traces.keys())[0]
            del execution_traces[oldest_key]
        
        return jsonify({
            "success": True,
            "query": query,
            "final_response": response,
            "timestamp": datetime.now().isoformat(),
            "agents_used": ["fallback_agent"],
            "confidence": 0.6 if response_type == "evaluation" else 0.5,
            "system": "fallback",
            "query_id": query_id  # Include query_id for trace lookup
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Query processing failed: {str(e)}"
        }), 500

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Minimal backend is running",
        "active_sessions": len(user_sessions),
        "timestamp": datetime.now().isoformat()
    }), 200

# Register the session blueprint
app.register_blueprint(session_bp)

# ===================================
# 🔧 DEBUG ENDPOINTS (Hidden from users)
# ===================================

@app.route("/debug/langgraph", methods=["GET"])
def debug_langgraph():
    """
    DEBUG ONLY: Show LangGraph visualization as PNG image.
    Access: http://localhost:5000/debug/langgraph
    """
    if not LANGGRAPH_VIZ_AVAILABLE:
        return jsonify({"error": "LangGraph visualization not available"}), 500
    
    try:
        # Get graph image as PNG bytes
        img_bytes = get_graph_image()
        
        if img_bytes is None:
            return jsonify({"error": "Failed to generate graph image"}), 500
        
        # Return as PNG image
        return send_file(
            io.BytesIO(img_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='langgraph.png'
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate visualization: {str(e)}"}), 500

@app.route("/debug/traces", methods=["GET"])
def debug_traces():
    """
    DEBUG ONLY: Show recent execution traces with agent activations.
    Access: http://localhost:5000/debug/traces
    Returns: JSON list of recent query executions
    """
    try:
        # Get last 10 traces
        recent_traces = list(execution_traces.values())[-10:]
        
        # Format for display
        formatted_traces = []
        for trace in recent_traces:
            formatted_traces.append({
                "query_id": trace.get("query_id"),
                "query": trace.get("query", "")[:100] + ("..." if len(trace.get("query", "")) > 100 else ""),
                "timestamp": trace.get("timestamp"),
                "agents_used": trace.get("agents_used", []),
                "nodes_activated": trace.get("nodes", []),
                "response_time_ms": trace.get("response_time_ms", 0),
                "cache_hit": trace.get("cache_hit", False)
            })
        
        return jsonify({
            "total_traces": len(execution_traces),
            "recent_traces": formatted_traces
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch traces: {str(e)}"}), 500

@app.route("/debug/langgraph/trace/<query_id>", methods=["GET"])
def debug_langgraph_trace(query_id):
    """
    DEBUG ONLY: Show LangGraph visualization with highlighted nodes for specific query.
    Access: http://localhost:5000/debug/langgraph/trace/<query_id>
    """
    if not LANGGRAPH_VIZ_AVAILABLE:
        return jsonify({"error": "LangGraph visualization not available"}), 500
    
    try:
        # Get trace for this query
        trace = execution_traces.get(query_id)
        
        if trace is None:
            return jsonify({"error": f"No trace found for query_id: {query_id}"}), 404
        
        # Get graph image with highlighted nodes
        nodes_activated = trace.get("nodes", [])
        img_bytes = get_graph_image(execution_trace=nodes_activated)
        
        if img_bytes is None:
            return jsonify({"error": "Failed to generate graph image"}), 500
        
        # Return as PNG image
        return send_file(
            io.BytesIO(img_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name=f'langgraph_trace_{query_id}.png'
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate visualization: {str(e)}"}), 500

@app.route("/debug/dashboard", methods=["GET"])
def debug_dashboard():
    """
    DEBUG ONLY: Show HTML dashboard with graph and traces.
    Access: http://localhost:5000/debug/dashboard
    """
    try:
        # Get recent traces
        recent_traces = list(execution_traces.values())[-10:]
        
        # Build HTML dashboard
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LangGraph Debug Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #0d1117;
                    color: #e5e7eb;
                }
                h1 { color: #60a5fa; }
                h2 { color: #34d399; margin-top: 30px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .graph-container {
                    background: #1f2937;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }
                .graph-container img {
                    max-width: 100%;
                    border: 2px solid #374151;
                    border-radius: 4px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background: #1f2937;
                    border-radius: 8px;
                    overflow: hidden;
                }
                th {
                    background: #374151;
                    padding: 12px;
                    text-align: left;
                    color: #60a5fa;
                }
                td {
                    padding: 10px;
                    border-top: 1px solid #374151;
                }
                tr:hover { background: #2d3748; }
                .cache-hit { color: #34d399; font-weight: bold; }
                .cache-miss { color: #f87171; font-weight: bold; }
                .agents { color: #fbbf24; }
                .refresh-btn {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-bottom: 20px;
                }
                .refresh-btn:hover { background: #2563eb; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 LangGraph Debug Dashboard</h1>
                <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
                
                <div class="graph-container">
                    <h2>📊 LangGraph Visualization</h2>
                    <img src="/debug/langgraph" alt="LangGraph">
                </div>
                
                <h2>📋 Recent Query Executions</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Query</th>
                            <th>Agents</th>
                            <th>Response Time</th>
                            <th>Cache</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for trace in reversed(recent_traces):  # Most recent first
            query = trace.get("query", "")[:60] + ("..." if len(trace.get("query", "")) > 60 else "")
            agents = ", ".join(trace.get("agents_used", []))
            cache_status = '<span class="cache-hit">✅ HIT</span>' if trace.get("cache_hit") else '<span class="cache-miss">❌ MISS</span>'
            
            html += f"""
                        <tr>
                            <td>{trace.get("timestamp", "")[:19]}</td>
                            <td>{query}</td>
                            <td class="agents">{agents or "None"}</td>
                            <td>{trace.get("response_time_ms", 0)} ms</td>
                            <td>{cache_status}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
                
                <p style="margin-top: 30px; color: #9ca3af; font-size: 0.9em;">
                    <strong>Note:</strong> This dashboard is for debugging purposes only and is hidden from end users.
                    Access other endpoints: 
                    <a href="/debug/traces" style="color: #60a5fa;">/debug/traces</a> | 
                    <a href="/debug/langgraph" style="color: #60a5fa;">/debug/langgraph</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        from flask import Response
        return Response(html, mimetype='text/html')
    except Exception as e:
        return jsonify({"error": f"Failed to generate dashboard: {str(e)}"}), 500

# ===================================
# END DEBUG ENDPOINTS
# ===================================

if __name__ == "__main__":
    print("[START] Starting Minimal Flask Backend...")
    print("[INFO] Session management endpoints available at /session/*")
    print("[INFO] Health check available at /health")
    print("[INFO] 🔧 DEBUG: LangGraph visualization at /debug/dashboard")
    print("[INFO] Backend will be available at: http://localhost:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
