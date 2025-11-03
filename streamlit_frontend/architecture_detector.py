"""
Architecture Detection for Streamlit Frontend
This module helps identify which backend architecture is running.
"""

import requests
import streamlit as st
from typing import Dict, Any, Optional

class ArchitectureDetector:
    """Detects which backend architecture is running."""
    
    def __init__(self, backend_url: str = "http://localhost:5000"):
        self.backend_url = backend_url
    
    def detect_architecture(self) -> Dict[str, Any]:
        """
        Detect the backend architecture.
        
        Returns:
            Dict containing architecture information
        """
        try:
            # Check health endpoint
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Determine architecture type
                if data.get('new_system_available'):
                    architecture_type = "NEW Multi-Agent System"
                    endpoint = "/api/v2/query"
                    features = [
                        "4 Orchestration Modes (CrewAI, AutoGen, LangGraph, Dynamic)",
                        "External Search with Perplexity API",
                        "Hybrid Agent Router",
                        "ChromaDB RAG Pipeline",
                        "Conversation State Management"
                    ]
                elif data.get('old_system_available'):
                    architecture_type = "OLD Multi-Agent System"
                    endpoint = "/api/query"
                    features = [
                        "Legacy Multi-Agent System",
                        "Basic Orchestration",
                        "Limited External Search",
                        "Basic RAG Pipeline"
                    ]
                else:
                    architecture_type = "No Multi-Agent System"
                    endpoint = None
                    features = ["Basic Backend Only"]
                
                return {
                    "status": "detected",
                    "architecture_type": architecture_type,
                    "endpoint": endpoint,
                    "features": features,
                    "backend_status": data.get('status', 'unknown'),
                    "new_system_available": data.get('new_system_available', False),
                    "old_system_available": data.get('old_system_available', False),
                    "kaggle_api_available": data.get('kaggle_api_available', False)
                }
            else:
                return {
                    "status": "error",
                    "error": f"Backend not responding: {response.status_code}",
                    "architecture_type": "Unknown"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"Connection failed: {str(e)}",
                "architecture_type": "Unknown"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Detection failed: {str(e)}",
                "architecture_type": "Unknown"
            }
    
    def display_architecture_info(self):
        """Display architecture information in Streamlit."""
        arch_info = self.detect_architecture()
        
        if arch_info["status"] == "detected":
            # Create columns for better layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🏗️ Backend Architecture")
                st.info(f"**{arch_info['architecture_type']}**")
                
                if arch_info['endpoint']:
                    st.code(f"API Endpoint: {arch_info['endpoint']}")
            
            with col2:
                # Status indicators
                if arch_info['new_system_available']:
                    st.success("✅ New System")
                elif arch_info['old_system_available']:
                    st.warning("⚠️ Old System")
                else:
                    st.error("❌ No System")
            
            # Features
            st.subheader("🚀 Available Features")
            for feature in arch_info['features']:
                st.write(f"• {feature}")
            
            # Backend status
            st.subheader("🔧 Backend Status")
            status_cols = st.columns(3)
            with status_cols[0]:
                st.metric("Backend", arch_info['backend_status'])
            with status_cols[1]:
                st.metric("Kaggle API", "✅" if arch_info['kaggle_api_available'] else "❌")
            with status_cols[2]:
                st.metric("Multi-Agent", "✅" if arch_info['old_system_available'] or arch_info['new_system_available'] else "❌")
                
        else:
            st.error(f"❌ Architecture Detection Failed: {arch_info['error']}")
    
    def get_recommended_endpoint(self) -> Optional[str]:
        """Get the recommended API endpoint based on detected architecture."""
        arch_info = self.detect_architecture()
        
        if arch_info["status"] == "detected":
            return arch_info.get("endpoint")
        return None
    
    def is_new_architecture(self) -> bool:
        """Check if the new architecture is available."""
        arch_info = self.detect_architecture()
        return arch_info.get("new_system_available", False)
    
    def is_old_architecture(self) -> bool:
        """Check if the old architecture is available."""
        arch_info = self.detect_architecture()
        return arch_info.get("old_system_available", False)

# Example usage in Streamlit
def show_architecture_detector():
    """Show architecture detector in Streamlit sidebar."""
    with st.sidebar:
        st.header("🔍 Architecture Detection")
        
        detector = ArchitectureDetector()
        arch_info = detector.detect_architecture()
        
        if arch_info["status"] == "detected":
            st.success(f"**{arch_info['architecture_type']}**")
            
            if arch_info['new_system_available']:
                st.info("🚀 Using latest multi-agent features!")
            elif arch_info['old_system_available']:
                st.warning("⚠️ Using legacy system")
            else:
                st.error("❌ No multi-agent system available")
        else:
            st.error("❌ Backend not available")

if __name__ == "__main__":
    # Test the detector
    detector = ArchitectureDetector()
    result = detector.detect_architecture()
    print("Architecture Detection Result:")
    print(result)









