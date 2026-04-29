import streamlit as st
import streamlit.components.v1 as components
from modules.database import init_db
from views.sidebar import render_sidebar
from views.home import render_home
from views.result import render_result
from views.popular import render_popular
from views.trends import render_trends
from views.history import render_history

# Initialize DB on startup
init_db()

# Configure page
st.set_page_config(page_title="지피지기 포스팅 자동 생성기", page_icon="✨", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .btn-primary>button {
        background-color: #111827;
        color: white;
    }
    .btn-secondary>button {
        background-color: #F3F4F6;
        color: #4F46E5;
        border: 1px solid #E5E7EB;
    }
    .btn-outline>button {
        background-color: white;
        color: #6B7280;
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Main App State
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home' # home, result, trends, history
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'trend_data' not in st.session_state:
    st.session_state.trend_data = ""

# Render Sidebar
render_sidebar()

# JS to set initial sidebar width, allowing native resizing
components.html(
    """
    <script>
    const doc = window.parent.document;
    if (!doc.getElementById('sidebar-adjuster')) {
        const script = doc.createElement('script');
        script.id = 'sidebar-adjuster';
        script.innerHTML = `
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                sidebar.style.width = '40vw';
            }
        `;
        doc.body.appendChild(script);
    }
    </script>
    """,
    height=0,
    width=0,
)

# Main Content Area Routing
if st.session_state.get("is_transitioning"):
    st.session_state.is_transitioning = False
    st.rerun()

if st.session_state.current_view == 'home':
    render_home()
elif st.session_state.current_view == 'result':
    render_result()
elif st.session_state.current_view == 'popular':
    render_popular()
elif st.session_state.current_view == 'trends':
    render_trends()
elif st.session_state.current_view == 'history':
    render_history()
