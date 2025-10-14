import streamlit as st
import requests
import json
import time
from datetime import datetime
import os
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="🧠 Kaggle Copilot Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme UI
st.markdown("""
<style>
    /* Main container styling - Dark theme */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
        background-color: #1a1a1a;
    }
    
    /* Overall app background */
    .stApp {
        background-color: #0d1117;
    }
    
    /* Chat message styling - Dark gradients */
    .user-message {
        background: linear-gradient(135deg, #1e3a8a 0%, #581c87 100%);
        color: #e5e7eb;
        padding: 1rem;
        border-radius: 18px 18px 5px 18px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        max-width: 80%;
        margin-left: auto;
        margin-right: 0;
        border: 1px solid #374151;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        color: #e5e7eb;
        padding: 1rem;
        border-radius: 18px 18px 18px 5px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        max-width: 80%;
        margin-left: 0;
        margin-right: auto;
        border: 1px solid #4b5563;
    }
    
    .system-message {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        color: #d1fae5;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: center;
        font-style: italic;
        box-shadow: 0 2px 8px rgba(0,0,0,0.5);
        border: 1px solid #10b981;
    }
    
    /* Text input and textarea styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #374151;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        background-color: #1f2937;
        color: #e5e7eb;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
        background-color: #111827;
    }
    
    /* Button styling - Dark theme */
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #6b21a8 100%);
        color: #e5e7eb;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid #4b5563;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.6);
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
    
    /* Sidebar styling - Dark */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #e5e7eb !important;
    }
    
    /* Status indicators */
    .status-connected {
        color: #10b981;
        font-weight: bold;
    }
    
    .status-processing {
        color: #f59e0b;
        font-weight: bold;
    }
    
    .status-error {
        color: #ef4444;
        font-weight: bold;
    }
    
    /* Competition card styling */
    .competition-card {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 0.75rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #4b5563;
        color: #e5e7eb;
    }
    
    .competition-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Backend configuration
BACKEND_URL = "http://localhost:5000"

# Chat storage directory
CHAT_STORAGE_DIR = "data/chat_history"

def load_chat_history() -> List[Dict]:
    """Load all saved chats from disk"""
    os.makedirs(CHAT_STORAGE_DIR, exist_ok=True)
    chats = []
    
    try:
        for filename in os.listdir(CHAT_STORAGE_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CHAT_STORAGE_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    chat = json.load(f)
                    chats.append(chat)
        
        # Sort by timestamp (most recent first)
        chats.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    except Exception as e:
        print(f"Error loading chat history: {e}")
    
    return chats

def save_current_chat():
    """Save current chat to disk"""
    if not st.session_state.messages:
        return
    
    try:
        # Generate chat ID if not exists
        if not st.session_state.current_chat_id:
            st.session_state.current_chat_id = f"chat_{int(time.time())}_{hash(str(st.session_state.messages[0]))}"
        
        # Create chat title from first user message
        title = "New Chat"
        for msg in st.session_state.messages:
            if msg.get('role') == 'user':
                title = msg.get('content', '')[:50] + ("..." if len(msg.get('content', '')) > 50 else "")
                break
        
        chat_data = {
            'id': st.session_state.current_chat_id,
            'title': title,
            'messages': st.session_state.messages,
            'timestamp': datetime.now().isoformat(),
            'user_info': st.session_state.user_info,
            'session_id': st.session_state.session_id
        }
        
        # Save to file
        filepath = os.path.join(CHAT_STORAGE_DIR, f"{st.session_state.current_chat_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
        
        # Update session state chat history
        # Remove old version if exists
        st.session_state.chat_history = [c for c in st.session_state.chat_history if c.get('id') != st.session_state.current_chat_id]
        # Add updated version at the top
        st.session_state.chat_history.insert(0, chat_data)
        
    except Exception as e:
        print(f"Error saving chat: {e}")

def load_chat(chat_id: str):
    """Load a specific chat by ID"""
    try:
        filepath = os.path.join(CHAT_STORAGE_DIR, f"{chat_id}.json")
        with open(filepath, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
            st.session_state.messages = chat_data.get('messages', [])
            st.session_state.current_chat_id = chat_id
            # Restore user info if available
            if 'user_info' in chat_data:
                st.session_state.user_info = chat_data['user_info']
                st.session_state.session_initialized = True
                st.session_state.session_id = chat_data.get('session_id')
    except Exception as e:
        print(f"Error loading chat {chat_id}: {e}")

def create_new_chat():
    """Create a new chat (clear current messages)"""
    st.session_state.messages = []
    st.session_state.current_chat_id = None

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_initialized' not in st.session_state:
    st.session_state.session_initialized = False
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = {
        'kaggle_username': '',
        'competition_slug': '',
        'competition_name': ''
    }
if 'competition_context' not in st.session_state:
    st.session_state.competition_context = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = load_chat_history()
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'competition_suggestions' not in st.session_state:
    st.session_state.competition_suggestions = []

def check_backend_connection() -> bool:
    """Check if backend is running and accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def search_competitions(query: str) -> List[Dict]:
    """Search for competitions using backend API"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/session/competitions/search",
            json={"query": query},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("competitions", [])
    except Exception as e:
        st.error(f"Error searching competitions: {e}")
    return []

def initialize_session(kaggle_username: str, competition_slug: str) -> Dict:
    """Initialize a new session with the backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/session/initialize",
            json={
                "kaggle_username": kaggle_username,
                "competition_slug": competition_slug
            },
            timeout=30  # Longer timeout for competition data fetching
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {"error": error_data.get("error", "Session initialization failed")}
    except Exception as e:
        return {"error": f"Connection error: {e}"}

def get_session_status(session_id: str) -> Dict:
    """Get current session status"""
    try:
        response = requests.get(f"{BACKEND_URL}/session/status/{session_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Session not found"}
    except Exception as e:
        return {"error": f"Connection error: {e}"}

def get_competition_context(session_id: str) -> Dict:
    """Get detailed competition context"""
    try:
        response = requests.get(f"{BACKEND_URL}/session/context/{session_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Context not found"}
    except Exception as e:
        return {"error": f"Connection error: {e}"}

def fetch_competition_data_on_demand(session_id: str, query: str, sections: List[str] = None) -> Dict:
    """Fetch competition data on-demand based on user query (aligned with architecture)"""
    try:
        payload = {
            "session_id": session_id,
            "query": query,
            "sections": sections or []
        }
        
        response = requests.post(
            f"{BACKEND_URL}/session/fetch-data",
            json=payload,
            timeout=60  # Longer timeout for data fetching
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            return {"error": error_data.get("error", "Data fetching failed")}
    except Exception as e:
        return {"error": f"Connection error: {e}"}

def submit_query_to_backend(query: str, user_context: Dict) -> Dict:
    """Submit query to backend multi-agent system"""
    try:
        payload = {
            "query": query,
            "user_context": user_context,
            "mode": "langgraph"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json=payload,
            timeout=120  # Extended timeout for detailed analysis (1200 chars per notebook)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Backend error: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The multi-agent system is processing your query..."}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Please ensure the Flask server is running."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def display_message(message: Dict):
    """Display a chat message with appropriate styling"""
    role = message.get('role', 'assistant')
    content = message.get('content', '')
    timestamp = message.get('timestamp', datetime.now().strftime("%H:%M"))
    
    if role == 'user':
        st.markdown(f"""
        <div class="user-message">
            <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.5rem;">👤 You • {timestamp}</div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    elif role == 'system':
        st.markdown(f"""
        <div class="system-message">
            <div>🤖 {content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:  # assistant
        st.markdown(f"""
        <div class="assistant-message">
            <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.5rem;">🧠 Kaggle Copilot • {timestamp}</div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #e5e7eb; margin-bottom: 0.5rem;">🧠 Kaggle Copilot Assistant</h1>
        <p style="color: #9ca3af; font-size: 1.1rem;">Your AI-powered competition companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Session Status
        if st.session_state.session_initialized:
            st.markdown("### ✅ Session Active")
            st.markdown(f"**User:** {st.session_state.user_info['kaggle_username']}")
            st.markdown(f"**Competition:** {st.session_state.user_info['competition_name']}")
            
            # Session info
            if st.session_state.competition_context:
                context = st.session_state.competition_context
                st.markdown(f"**Total Notebooks:** {context.get('total_notebooks', 0)}")
                st.markdown(f"**Status:** {'✅ Accessible' if context.get('competition_accessible') else '❌ Not accessible'}")
                st.markdown(f"**Data Fetches:** {context.get('fetched_data_count', 0)}")
            
            if st.button("🔄 Refresh Session", use_container_width=True):
                if st.session_state.session_id:
                    status = get_session_status(st.session_state.session_id)
                    if "error" not in status:
                        st.success("Session refreshed!")
                        st.rerun()
                    else:
                        st.error(f"Refresh failed: {status['error']}")
        else:
            st.markdown("### 🎯 Initialize Session")
            
            # Session initialization form
            st.markdown("**Start a new session**")
            
            kaggle_username = st.text_input(
                "Kaggle Username", 
                value=st.session_state.user_info['kaggle_username'],
                placeholder="your_kaggle_username",
                help="Your Kaggle username (without @)"
            )
            
            # Competition input with search suggestions
            competition_input = st.text_input(
                "Competition Slug", 
                value=st.session_state.user_info['competition_slug'],
                placeholder="Start typing... (e.g., titanic, house-prices)",
                help="Enter the competition slug - we support ALL Kaggle competitions!"
            )
            
            # Auto-search as user types (only if 3+ characters)
            if competition_input and len(competition_input) >= 3 and competition_input != st.session_state.user_info['competition_slug']:
                with st.spinner("Searching..."):
                    found_comps = search_competitions(competition_input)
                    if found_comps:
                        st.markdown("**Suggestions:**")
                        for comp in found_comps[:3]:  # Show top 3
                            if st.button(f"✅ {comp['name'][:40]}...", key=f"sugg_{comp['slug']}", use_container_width=True):
                                st.session_state.user_info['competition_slug'] = comp['slug']
                                st.session_state.user_info['competition_name'] = comp['name']
                                st.rerun()
            
            competition_slug = competition_input
            
            # Initialize session button
            if st.button("🚀 Initialize Session", use_container_width=True, type="primary"):
                if not kaggle_username or not competition_slug:
                    st.error("Please provide both Kaggle username and competition slug")
                else:
                    with st.spinner("Initializing session and fetching competition data..."):
                        result = initialize_session(kaggle_username, competition_slug)
                        
                        if "error" in result:
                            st.error(f"Session initialization failed: {result['error']}")
                        else:
                            # Update session state
                            st.session_state.session_initialized = True
                            st.session_state.session_id = result['session_id']
                            st.session_state.user_info = {
                                'kaggle_username': kaggle_username,
                                'competition_slug': competition_slug,
                                'competition_name': result.get('competition_summary', {}).get('name', competition_slug)
                            }
                            
                            # Fetch detailed context
                            context_result = get_competition_context(result['session_id'])
                            if "error" not in context_result:
                                st.session_state.competition_context = context_result.get('competition_context', {})
                            
                            st.success(f"Session initialized successfully!")
                            st.balloons()
                            st.rerun()
        
        st.markdown("---")
        
        # Backend status
        st.markdown("### 🔗 System Status")
        if check_backend_connection():
            st.markdown('<p class="status-connected">✅ Backend Connected</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Backend Disconnected</p>', unsafe_allow_html=True)
            st.markdown("**To start the backend:**")
            st.code("python -m kaggle_competition_assist_backend.app")
        
        st.markdown("---")
        
        # Chat management
        st.markdown("### 💬 Conversations")
        
        # New Chat button
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            create_new_chat()
            st.rerun()
        
        # Chat history
        if st.session_state.chat_history:
            st.markdown("**Saved Chats:**")
            for chat in st.session_state.chat_history[:10]:  # Show last 10
                # Highlight current chat
                is_current = chat.get('id') == st.session_state.current_chat_id
                button_label = f"{'🟢 ' if is_current else '💬 '}{chat.get('title', 'Untitled')[:30]}"
                if len(chat.get('title', '')) > 30:
                    button_label += "..."
                
                if st.button(button_label, key=f"chat_{chat.get('id')}", use_container_width=True):
                    load_chat(chat.get('id'))
                    st.rerun()
        else:
            st.markdown("*No saved conversations*")
        
        # Clear current chat button
        if st.session_state.messages:
            if st.button("🗑️ Clear Current Chat", use_container_width=True):
                create_new_chat()
                st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Chat messages
        if st.session_state.messages:
            for message in st.session_state.messages:
                display_message(message)
        else:
            if not st.session_state.session_initialized:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; color: #9ca3af;">
                    <h3 style="color: #e5e7eb;">👋 Welcome to Kaggle Copilot!</h3>
                    <p style="color: #d1d5db;">I'm your AI assistant for Kaggle competitions. I can help you with:</p>
                    <ul style="text-align: left; max-width: 400px; margin: 0 auto; color: #d1d5db;">
                        <li>📊 Competition analysis and strategy</li>
                        <li>💻 Code review and optimization</li>
                        <li>🔍 Feature engineering suggestions</li>
                        <li>📈 Model performance improvement</li>
                        <li>🐛 Debugging and error resolution</li>
                    </ul>
                    <p style="margin-top: 2rem; color: #d1d5db;"><strong>🚀 Initialize your session in the sidebar to get started!</strong></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; color: #9ca3af;">
                    <h3 style="color: #e5e7eb;">💬 Start chatting with your AI assistant!</h3>
                    <p style="color: #d1d5db;">Ask me anything about the <strong style="color: #60a5fa;">{}</strong> competition.</p>
                    <p style="color: #d1d5db;">I'll fetch relevant data on-demand based on your questions!</p>
                    <p style="color: #9ca3af;"><em>📊 Total notebooks available: {}</em></p>
                </div>
                """.format(
                    st.session_state.user_info['competition_name'],
                    st.session_state.competition_context.get('total_notebooks', 0)
                ), unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    # Query input - Using text_area for multi-line support
    if st.session_state.session_initialized:
        user_query = st.text_area(
            f"💬 Ask me anything about the {st.session_state.user_info['competition_name']} competition:",
            placeholder="e.g., How should I approach this competition?\n\nOr paste your code here:\nimport pandas as pd\ndf = pd.read_csv('train.csv')",
            height=150,
            key="user_input",
            help="Paste code or ask questions - the box will expand automatically!"
        )
    else:
        user_query = st.text_area(
            "💬 Initialize your session first to start chatting:",
            placeholder="Session required to start chatting",
            height=150,
            disabled=True,
            key="user_input_disabled"
        )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        send_button = st.button("🚀 Send Query", use_container_width=True)
    
    # Process query
    if send_button and user_query.strip() and st.session_state.session_initialized:
        # Add user message to chat
        user_message = {
            'role': 'user',
            'content': user_query,
            'timestamp': datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(user_message)
        
        # Show processing indicator
        with st.spinner("🧠 Multi-agent system is thinking..."):
            # First, fetch relevant data on-demand based on the query
            data_fetch_result = fetch_competition_data_on_demand(
                st.session_state.session_id, 
                user_query
            )
            
            # Prepare enhanced user context with session info and fetched data
            enhanced_context = {
                **st.session_state.user_info,
                'session_id': st.session_state.session_id,
                'competition_context': st.session_state.competition_context,
                'fetched_data': data_fetch_result if "error" not in data_fetch_result else None
            }
            
            # Submit to backend
            result = submit_query_to_backend(user_query, enhanced_context)
            
            if 'error' in result:
                assistant_message = {
                    'role': 'system',
                    'content': f"⚠️ {result['error']}",
                    'timestamp': datetime.now().strftime("%H:%M")
                }
            else:
                assistant_message = {
                    'role': 'assistant',
                    'content': result.get('final_response', 'No response received.'),
                    'timestamp': datetime.now().strftime("%H:%M")
                }
            
            st.session_state.messages.append(assistant_message)
        
        # Auto-save chat after each message
        save_current_chat()
        
        st.rerun()

if __name__ == "__main__":
    main()
