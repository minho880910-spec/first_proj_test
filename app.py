# 지피지기_프로젝트/
# ├── app.py           (실행을 담당하는 메인 파일)
# ├── trend.py          (트렌드 대시보드 로직)
# ├── content.py        (콘텐츠 생성기 로직)
# ├── history.py        (발행 히스토리 로직)
# └── report.py         (성과 리포트 로직)

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os


# 1. 페이지 기본 설정
st.set_page_config(
    page_title="지피지기(Zipi-Zigi) | 마케팅 인텔리전스",
    page_icon="📈",
    layout="wide"
)

# 2. CSS 주입 (강제 왼쪽 정렬 및 내부 여백 제어)
st.markdown("""
    <style>
    /* 버튼 자체의 정렬 */    
    div.stButton > button {
        width: 100% !important;
        border: none !important;
        background-color: transparent !important;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;

        /* 1. 버튼 내부 상하 여백을 확 줄임 (딱 붙어 보이게 하는 핵심) */
        padding-top: 2px !important;
        padding-bottom: 2px !important;
        padding-left: 15px !important;

        /* 2. 버튼 사이의 바깥 간격을 0으로 설정 */
        margin-top: 0px !important;
        margin-bottom: 0px !important;

        border-radius: 4px !important;
        min-height: unset !important; /* 최소 높이 해제 */
    }

    /* 버튼 안의 텍스트가 차지하는 기본 여백도 제거 */
    div.stButton p {
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    /* 버튼 내부 텍스트 및 이모지 정렬 강제 고정 */
    div.stButton > button div {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        justify-content: flex-start !important;
        text-align: left !important;
    }

    /* 버튼 텍스트 문구 정렬 */
    div.stButton p {
        margin: 0 !important;
        text-align: left !important;
        font-size: 15px !important;
        font-weight: 500 !important;
    }

    /* 호버 시 효과 */
    div.stButton > button:hover {
        background-color: rgba(151, 166, 195, 0.15) !important;
    }

    /* 포커스 시 테두리 제거 */
    div.stButton > button:focus {
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 세션 상태 초기화
load_dotenv()
if 'openai_client' not in st.session_state:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.session_state['openai_client'] = OpenAI(api_key=api_key)
    else:
        st.error("⚠️ API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")
        st.session_state['openai_client'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Content"
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'search_keyword' not in st.session_state:
    st.session_state['search_keyword'] = "소상공인 마케팅"

# 4. 사이드바 구성
with st.sidebar:
    # --- [최상단 타이틀] ---
    st.markdown("# 知彼知己 (지피지기)")
    st.markdown("### 트렌드를 알고 나를 안다.")
    st.caption("실패없는 마케팅을 드리겠습니다.")
    st.divider()

    # --- [메뉴 구역] ---
    st.write("Main Service")
    if st.button("✍️ Content", key="content_btn", use_container_width=True):
        st.session_state['current_page'] = "Content"
    if st.button("📜 History", key="history_btn", use_container_width=True):
        st.session_state['current_page'] = "History"
    if st.button("📊 Report", key="report_btn", use_container_width=True):
        st.session_state['current_page'] = "Report"
    if st.button("📈 Trend", key="trend_btn", use_container_width=True):
        st.session_state['current_page'] = "Trend"

    st.write("") 
    st.write("Test Menu")
    if st.button("🔥 test1", key="test1_btn", use_container_width=True):
        st.session_state['current_page'] = "test1"
    if st.button("⭐ test2", key="test2_btn", use_container_width=True):
        st.session_state['current_page'] = "test2"
    if st.button("🍀 test3", key="test3_btn", use_container_width=True):
        st.session_state['current_page'] = "test3"
    if st.button("👻 test4", key="test4_btn", use_container_width=True):
        st.session_state['current_page'] = "test4"
    
    st.divider()

# 5. 페이지 로딩 로직
def run_page(page_name):
    file_path = f"pages/{page_name.lower()}.py"
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            exec(f.read(), globals())

run_page(st.session_state['current_page'])