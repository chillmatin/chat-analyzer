import streamlit as st
from datetime import datetime
from chat import WhatsAppChat
import tempfile
import os

# Page config
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    /* Make file uploader button smaller */
    [data-testid="stFileUploader"] button {
        font-size: 0.85rem !important;
        padding: 0.25rem 0.75rem !important;
    }
    [data-testid="stFileUploader"] {
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Load chat data
@st.cache_data
def load_chat(file_content, filename):
    """Load and parse WhatsApp chat from uploaded file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp_file:
        tmp_file.write(file_content)
        tmp_path = tmp_file.name
    
    try:
        chat = WhatsAppChat(tmp_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    return chat

# Header
st.markdown('<div class="main-header">WhatsApp Chat Analyzer</div>', unsafe_allow_html=True)

# File uploader in sidebar
with st.sidebar:
    uploaded_file = st.file_uploader(
        "Upload WhatsApp Chat",
        type=['txt'],
        help="Export your WhatsApp chat and upload the .txt file"
    )

# Show instructions if no file uploaded
if uploaded_file is None:
    st.info("👆 Upload your WhatsApp chat export file in the sidebar to begin")
    
    with st.expander("📖 How to export WhatsApp chat"):
        st.markdown("""
        **On Android:**
        1. Open the chat → ⋮ menu → More → Export chat
        2. Choose "Without Media" and save the .txt file
        
        **On iPhone:**
        1. Open the chat → Tap contact name → Export Chat
        2. Choose "Without Media" and save the .txt file
        
        *Your data is not stored.*
        """)
    st.stop()

# Load the chat
file_content = uploaded_file.read().decode('utf-8')
chat = load_chat(file_content, uploaded_file.name)

# Store chat in session state for pages to access
st.session_state.chat = chat

# Welcome message on main page
st.markdown("""
## Welcome to WhatsApp Chat Analyzer

This app helps you analyze and visualize your WhatsApp chat data with detailed insights into:

- **Overview**: High-level statistics and message distribution
- **Time Analysis**: Activity patterns, heatmaps, and trends over time
- **Participant Analysis**: Individual statistics and comparisons
- **Content Analysis**: Word clouds, emojis, media, and message search
- **Conversation Patterns**: Response times and conversation starters

### Getting Started
1. Upload your WhatsApp chat export file using the sidebar
2. Navigate between different analysis pages using the sidebar menu

*Your data is not stored.*
""")

# Sidebar - Chat statistics
with st.sidebar:
    st.info(f"""
**Chat Statistics**
- Total Messages: {chat.message_count:,}
- Duration: {chat.duration_days} days
- Participants: {len(chat.participants)}
- Period: {chat.start_date.strftime('%Y-%m-%d') if chat.start_date else 'N/A'} to {chat.end_date.strftime('%Y-%m-%d') if chat.end_date else 'N/A'}
""")
