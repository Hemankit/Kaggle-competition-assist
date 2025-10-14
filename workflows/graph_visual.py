import io
from workflows.graph_workflow import compiled_graph


def get_graph_image(execution_trace=None):
    """
    Returns the graph visualization as PNG bytes showing the LangGraph workflow.
    If execution_trace is provided, can be used for highlighting (not yet supported).
    """
    if not compiled_graph:
        return None
    
    try:
        # Get the drawable graph object
        graph = compiled_graph.get_graph()
        
        # Draw the Mermaid PNG diagram
        img_bytes = io.BytesIO()
        graph.draw_mermaid_png(output_file_path=None)  # Returns bytes
        
        # Alternative: If the above doesn't work, try drawing to file
        try:
            png_data = graph.draw_mermaid_png()
            return png_data
        except:
            # Fallback: Use draw_ascii for text representation
            ascii_repr = graph.draw_ascii()
            # Convert ASCII to a simple image (or just return None)
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to generate graph visualization: {e}")
        return None

