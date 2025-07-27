from flask import Blueprint, jsonify, request
from query_processing.user_input_processor import UserInputProcessor
from hybrid_scraping_routing.agent_router import HybridScrapingAgent
# creating blueprint for user input processing and scraping
input_processsing_bp = Blueprint("input_processing", __name__, url_prefix="/process")
scraping_or_fetching_bp = Blueprint("scraping_fetching", __name__, url_prefix="/scrape-or-fetch")
@input_processsing_bp.route("/", methods=["POST"])
def process_input():
  data = request.get_json()
  query = data.get("query", "")
  processor = UserInputProcessor()
  structured_query = processor.structure_query(query)
  return jsonify(structured_query), 200

   # using 
@scraping_or_fetching_bp.route("/", methods=["POST"])
def scrape_or_fetch_data():
  data = request.get_json()
  query = data.get("query", "")
  routing_and_retrieval = HybridScrapingAgent(llm=None)  # Assuming llm is initialized elsewhere, Which is fine as a placeholder.

# But eventually, you’ll either:

# Load an actual model (e.g., from LangChain or your config)

# Or inject it at the top level (app.config or DI-style init)

# Just mark this mentally as something to return to.
  structured_query = routing_and_retrieval.route_to_retrieval_method(query)
  return jsonify(structured_query), 200
