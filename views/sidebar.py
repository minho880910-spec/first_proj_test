import streamlit as st
from modules.database import add_history
from modules.llm_engine import generate_content
from modules.trend_analyzer import get_trend_summary
import base64
import os

@st.cache_data
def get_logo_base64():
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def render_sidebar():
    def change_view(view):
        if st.session_state.get('current_view') != view:
            st.session_state.is_transitioning = True
        st.session_state.current_view = view
        if view == 'result' and st.session_state.get("prompt_input"):
            st.session_state.auto_generate = True

    logo_b64 = get_logo_base64()

    with st.sidebar:
        st.markdown(f"""
            <style>
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) {{
                display: none;
            }}
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button {{
                background: transparent !important;
                border: transparent !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
                justify-content: flex-start !important;
            }}
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button:hover {{
                background: transparent !important;
                border: transparent !important;
                box-shadow: none !important;
            }}
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button:focus:not(:active) {{
                border-color: transparent !important;
                box-shadow: none !important;
                color: inherit !important;
            }}
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button p {{
                font-size: 1.85rem !important;
                font-weight: 600 !important;
                margin: 0 !important;
                padding: 1.25rem 0px 1rem 0px !important;
                color: inherit;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            div[data-testid="stElementContainer"]:has(.logo-btn-marker) + div[data-testid="stElementContainer"] button p::before {{
                content: "";
                display: inline-block;
                width: 2.2rem;
                height: 2.2rem;
                background-image: url("data:image/png;base64,{logo_b64}");
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
            }}
            </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="logo-btn-marker"></div>', unsafe_allow_html=True)
        st.button("지피지기", key="logo_btn", on_click=change_view, args=('home',))
        st.write("---")

        categories = [
            "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
            "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
            "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠"
        ]

        title = st.text_area("프롬프트 입력", placeholder="예: 신제품 립스틱 출시 홍보를 위한 인스타그램 글 작성해줘\n(자세한 타겟 고객이나 강조할 특징을 함께 적어주시면 더 좋습니다.)", height=150, key="prompt_input")

        st.write("---")
        st.markdown("### 📌 메뉴")
        st.button("📢 콘텐츠 생성", use_container_width=True, on_click=change_view, args=('result',))
        st.button("🕒 생성 내역 관리", use_container_width=True, on_click=change_view, args=('history',))
        st.button("🔥 인기 포스팅", use_container_width=True, on_click=change_view, args=('popular',))
        st.button("📈 최신 트렌드", use_container_width=True, on_click=change_view, args=('trends',))
