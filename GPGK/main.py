# 지피지기_프로젝트/
# ├── main.py           (실행을 담당하는 메인 파일)
# ├── trend.py          (트렌드 대시보드 로직)
# ├── content.py        (콘텐츠 생성기 로직)
# ├── history.py        (발행 히스토리 로직)
# └── report.py         (성과 리포트 로직)

import streamlit as st
from openai import OpenAI

# 분리된 모듈들을 불러옵니다.
import trend
import content
import history
import report

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="지피지기(Zipi-Zigi) | 마케팅 인텔리전스",
    page_icon="📈",
    layout="wide"
)

# 2. 세션 상태 초기화 (데이터 임시 저장소)
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'search_keyword' not in st.session_state:
    st.session_state['search_keyword'] = "소상공인 마케팅"
if 'openai_client' not in st.session_state:
    st.session_state['openai_client'] = None

# 3. 사이드바 구성
with st.sidebar:
    st.title("지피지기 🔍")
    st.subheader("SNS 자동 생성 및 트렌드 분석")
    
    menu = st.radio(
        "이동할 메뉴를 선택하세요",
        ("트렌드 대시보드", "콘텐츠 생성기", "발행 히스토리", "성과 리포트")
    )
    
    st.divider()
    
    # API 키 입력란 (요청하신 대로 추가 문구 삭제)
    openai_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    
    if openai_key:
        st.session_state['openai_client'] = OpenAI(api_key=openai_key)
        st.success("OpenAI 연결 완료!")
    else:
        st.warning("OpenAI API 키가 필요합니다.")

# 4. 메뉴 선택에 따른 화면 렌더링 (import한 모듈의 함수 실행)
if menu == "트렌드 대시보드":
    trend.render_page()
elif menu == "콘텐츠 생성기":
    content.render_page()
elif menu == "발행 히스토리":
    history.render_page()
elif menu == "성과 리포트":
    report.render_page()