from flask import Blueprint, jsonify, request
from workflows.graph_visual import get_graph_image
graph_visualization_bp = Blueprint("graph_visualization", __name__, url_prefix="/graph-viz")
@graph_visualization_bp.route("/image", methods=["POST"])
def get_graph_image_route():
    data = request.get_json()
    query = data.get("query", "")
    
    # Get the graph image bytes for the provided query
    img_bytes = get_graph_image(query)
    
    if img_bytes is None:
        return jsonify({"error": "Graph could not be generated"}), 400
    
    response = jsonify({"message": "Graph image generated successfully"})
    response.headers.set("Content-Type", "image/png")
    response.data = img_bytes
    return response, 200