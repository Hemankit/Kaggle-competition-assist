from workflows.graph_workflow import compiled_graph
import io

def get_graph_image(execution_trace=None):
    """
    Returns the graph visualization as PNG bytes.
    If execution_trace is provided, highlights/overlays activated nodes.
    """
    if not compiled_graph or not hasattr(compiled_graph, "draw_mermaid_png"):
        return None
    img_bytes = io.BytesIO()
    # If execution_trace is provided, pass it to the visualization method (if supported)
    # This assumes draw_mermaid_png supports a 'highlight_nodes' argument
    if execution_trace:
        try:
            compiled_graph.draw_mermaid_png(output=img_bytes, highlight_nodes=execution_trace)
        except TypeError:
            # Fallback: draw without highlights if not supported
            compiled_graph.draw_mermaid_png(output=img_bytes)
    else:
        compiled_graph.draw_mermaid_png(output=img_bytes)
    img_bytes.seek(0)
    return img_bytes.read()

