"""
SueBot - Legal Document Review Assistant
Minimalistic Streamlit UI - Blue & White Design

Author: Legal Tech Team
Version: 2.0.0
Python: 3.9+
"""

import streamlit as st
from chatbot.chatbot import LegalChatbot
from config import Config, logger
import os
import tempfile
from pathlib import Path
from datetime import datetime

# ==================== Configuration ====================

st.set_page_config(
    page_title="SueBot - Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Minimal Blue & White Styling ====================

st.markdown("""
    <style>
    /* Blue & White color scheme */
    :root {
        --primary-blue: #2563eb;
        --dark-blue: #1e40af;
        --light-blue: #eff6ff;
        --border-gray: #e5e7eb;
    }
    
    /* Main background */
    .main { background-color: white; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid var(--border-gray);
    }
    
    /* Headers */
    h1, h2, h3 { color: var(--dark-blue); }
    
    /* Buttons */
    .stButton > button {
        background: white;
        color: var(--primary-blue);
        border: 1px solid var(--border-gray);
        border-radius: 6px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: var(--light-blue);
        border-color: var(--primary-blue);
    }
    
    .stButton > button[kind="primary"] {
        background: var(--primary-blue);
        color: white;
        border: none;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--dark-blue);
    }
    
    /* Input fields */
    .stTextInput input {
        border: 1px solid var(--border-gray);
        border-radius: 6px;
    }
    
    .stTextInput input:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 1px var(--primary-blue);
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: white;
        border: 1px solid var(--border-gray);
        border-radius: 8px;
    }
    
    [data-testid="stChatMessage"][data-testid-type="user"] {
        background: var(--light-blue);
        border-left: 3px solid var(--primary-blue);
    }
    
    [data-testid="stChatMessage"][data-testid-type="assistant"] {
        border-left: 3px solid var(--dark-blue);
    }
    
    /* Info boxes */
    .stAlert { border-radius: 6px; }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid var(--border-gray);
    }
    
    [data-testid="stMetricValue"] { color: var(--primary-blue); }
    </style>
""", unsafe_allow_html=True)

# ==================== Session State ====================

def init_session():
    """Initialize session state variables"""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = LegalChatbot()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'doc_loaded' not in st.session_state:
        st.session_state.doc_loaded = False
    if 'doc_info' not in st.session_state:
        st.session_state.doc_info = None
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.now()

# ==================== Document Processing ====================

def process_document(file):
    """Process uploaded document"""
    try:
        # Validate file
        if file.size > Config.MAX_DOCUMENT_SIZE_MB * 1024 * 1024:
            return False, f"File exceeds {Config.MAX_DOCUMENT_SIZE_MB}MB limit"
        
        # Save to temp file
        suffix = Path(file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.getbuffer())
            tmp_path = tmp.name
        
        # Process with chatbot
        result = st.session_state.chatbot.load_document(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        # Update state
        st.session_state.doc_loaded = True
        st.session_state.doc_info = st.session_state.chatbot.state["document_metadata"]
        
        return True, result
        
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        return False, str(e)

# ==================== Query Processing ====================

def process_query(query):
    """Process user query"""
    try:
        response = st.session_state.chatbot.process_query(query)
        st.session_state.query_count += 1
        
        # Get metadata
        metadata = {
            'query_type': st.session_state.chatbot.state.get('query_type'),
            'routing': st.session_state.chatbot.state.get('routing_decision')
        }
        
        return True, response, metadata
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return False, str(e), None

# ==================== Sidebar ====================

def render_sidebar():
    """Render sidebar with document management"""
    with st.sidebar:
        st.title("⚖️ SueBot")
        st.caption("Legal Document Review Assistant")
        
        st.divider()
        
        # Document upload
        st.subheader("Document Upload")
        uploaded = st.file_uploader(
            "Upload legal document",
            type=['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'],
            help="PDF, PNG, JPG, TIFF, BMP supported"
        )
        
        if uploaded:
            if st.button("📤 Process Document", use_container_width=True, type="primary"):
                with st.spinner("Processing..."):
                    success, msg = process_document(uploaded)
                    if success:
                        st.success("Document loaded!")
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")
        
        st.divider()
        
        # Document info
        if st.session_state.doc_loaded and st.session_state.doc_info:
            st.subheader("Current Document")
            info = st.session_state.doc_info
            
            st.text(f"📄 {info['filename']}")
            st.text(f"📊 {info['size_mb']} MB")
            st.text(f"📝 {info['word_count']:,} words")
            
            if st.button("🗑️ Clear Document", use_container_width=True):
                st.session_state.chatbot.clear_document()
                st.session_state.doc_loaded = False
                st.session_state.doc_info = None
                st.rerun()
        else:
            st.info("No document loaded")
        
        st.divider()
        
        # Statistics
        st.subheader("Session Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", st.session_state.query_count)
        with col2:
            duration = datetime.now() - st.session_state.start_time
            st.metric("Duration", f"{int(duration.total_seconds()/60)}m")
        
        st.divider()
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.query_count = 0
                st.rerun()
        with col2:
            if st.button("🔁 Reset All", use_container_width=True):
                st.session_state.messages = []
                st.session_state.query_count = 0
                if st.session_state.doc_loaded:
                    st.session_state.chatbot.clear_document()
                    st.session_state.doc_loaded = False
                    st.session_state.doc_info = None
                st.rerun()
        
        st.divider()
        st.caption("v2.0.0 | Legal Tech Team")

# ==================== Main App ====================

def main():
    """Main application"""
    
    # Initialize
    init_session()
    
    # Render sidebar
    render_sidebar()
    
    # Header
    st.title("Legal Consultation Chat")
    
    # Welcome message
    if not st.session_state.messages:
        st.info("""
        👋 **Welcome to SueBot!**
        
        Upload a legal document and ask questions about:
        - FDCPA & TCPA compliance
        - Risk assessment
        - Clause extraction
        - Document summaries
        """)
    
    # Quick action buttons (if document loaded)
    if st.session_state.doc_loaded:
        st.subheader("Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        quick_queries = [
            ("📋 Summarize", "Provide a comprehensive summary of this document"),
            ("✅ FDCPA Check", "Check for FDCPA compliance issues"),
            ("☎️ TCPA Check", "Analyze for TCPA compliance"),
            ("⚠️ Risk Assessment", "Conduct a risk assessment")
        ]
        
        for col, (label, query) in zip([col1, col2, col3, col4], quick_queries):
            with col:
                if st.button(label, use_container_width=True):
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "user",
                        "content": query,
                        "timestamp": datetime.now()
                    })
                    
                    # Process query
                    with st.spinner("Analyzing..."):
                        success, response, metadata = process_query(query)
                        if success:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response,
                                "timestamp": datetime.now(),
                                "metadata": metadata
                            })
                        else:
                            st.session_state.messages.append({
                                "role": "error",
                                "content": f"Error: {response}",
                                "timestamp": datetime.now()
                            })
                    st.rerun()
        
        st.divider()
    
    # Display chat messages
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
                # Show query type badge if available
                if msg.get("metadata", {}).get("query_type"):
                    qt = msg["metadata"]["query_type"].replace("_", " ").title()
                    st.caption(f"🏷️ {qt}")
        
        elif role == "assistant":
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(content)
        
        elif role == "error":
            with st.chat_message("assistant", avatar="⚠️"):
                st.error(content)
        
        else:  # system
            st.info(content)
    
    # Chat input
    if prompt := st.chat_input("Ask about the legal document..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process and display response
        with st.chat_message("assistant", avatar="⚖️"):
            with st.spinner("Analyzing..."):
                success, response, metadata = process_query(prompt)
                
                if success:
                    st.write(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now(),
                        "metadata": metadata
                    })
                else:
                    st.error(f"Error: {response}")
                    st.session_state.messages.append({
                        "role": "error",
                        "content": f"Error: {response}",
                        "timestamp": datetime.now()
                    })
        
        st.rerun()

# ==================== Entry Point ====================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        st.error(f"Critical Error: {str(e)}")
        if st.button("🔄 Restart"):
            st.rerun()