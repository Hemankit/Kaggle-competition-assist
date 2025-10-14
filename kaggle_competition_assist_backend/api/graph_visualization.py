from flask import Blueprint, jsonify, request, send_file
from orchestrators.component_orchestrator import ComponentOrchestrator
from workflows.graph_visual import get_graph_image
import io

graph_visualization_bp = Blueprint("graph_visualization", __name__, url_prefix="/graph-viz")

# Instantiate orchestrator (or inject from app context)
orchestrator = ComponentOrchestrator()

@graph_visualization_bp.route("/image", methods=["GET"])
def get_graph_image_route():
    trace_info = orchestrator.get_debug_trace()
    execution_trace = trace_info.get("trace", [])

    img_bytes = get_graph_image(execution_trace)

    if img_bytes is None:
        return jsonify({"error": "Graph could not be generated"}), 400

    return send_file(
        io.BytesIO(img_bytes),
        mimetype='image/png',
        as_attachment=False,
        download_name="execution_graph.png"
    )