import streamlit as st
import os
from openai import OpenAI
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
st.set_page_config(page_title="지피지기 포스팅 자동 생성기", page_icon="logo.png", layout="wide")


# Main App State
if 'openai_client' not in st.session_state:
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key:
        st.session_state['openai_client'] = OpenAI(api_key=api_key)
    else:
        st.error("⚠️ API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")
        st.session_state['openai_client'] = None
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
# Create a placeholder for the main content
main_content = st.empty()

# Clear the placeholder explicitly to remove any ghosting from the previous view ONLY when transitioning
if st.session_state.get("is_transitioning"):
    st.session_state.is_transitioning = False
    main_content.empty()

with main_content.container():
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
