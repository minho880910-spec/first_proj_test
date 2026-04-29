import streamlit as st
from modules.llm_engine import generate_content
from modules.database import add_history

def render_result():
    st.markdown("""
        <style>
        div.stButton > button[kind="primary"] {
            background-color: #87CEFA !important;
            color: #333333 !important;
            border-color: #87CEFA !important;
            font-weight: bold !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #00BFFF !important;
            border-color: #00BFFF !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.header("✨ 콘텐츠 제작")
    
    tone = st.selectbox("어떤 느낌으로 쓸까요?💬", ["전문적인", "친근한", "유머러스한", "감성적인"], key="tone_select")
    
    sns_options = ["Instagram", "Threads", "X (Twitter)"]
    selected_sns = st.multiselect("포스팅 할 SNS 선택", sns_options, default=sns_options, key="sns_select")
    
    if st.button("제작하기", type="primary", use_container_width=True):
        title = st.session_state.get("prompt_input", "")
        if title:
            if not selected_sns:
                st.warning("포스팅 할 SNS를 최소 하나 이상 선택해주세요.")
            else:
                with st.spinner("콘텐츠를 생성 중입니다..."):
                    # 트렌드 탭에서 선택한 카테고리가 있으면 사용하고, 없으면 기본값 사용
                    category = st.session_state.get("trend_category", "미지정")
                    results = generate_content(category, title, tone)
                    
                    st.session_state.results = results
                    st.session_state.selected_sns = selected_sns
                    
                    # 새 결과를 텍스트 에어리어에 즉시 반영하기 위해 기존 캐시 키 삭제
                    for key in ['ig_res', 'th_res', 'x_res']:
                        if key in st.session_state:
                            del st.session_state[key]
                            
                    add_history(category, title, tone, results.get('instagram', ''), results.get('threads', ''), results.get('x', ''))
        else:
            st.warning("👈 좌측 메뉴에서 프롬프트를 먼저 입력해주세요.")

    if st.session_state.get('results') and st.session_state.get('selected_sns'):
        st.write("---")
        st.subheader("✨ 콘텐츠 제작 결과")
        
        selected_sns = st.session_state.selected_sns
        tabs = st.tabs(selected_sns)
        
        for i, sns in enumerate(selected_sns):
            with tabs[i]:
                if sns == "Instagram":
                    st.subheader("Instagram 포스팅")
                    st.text_area("내용", st.session_state.results.get('instagram', ''), height=300, key="ig_res")
                elif sns == "Threads":
                    st.subheader("Threads 포스팅")
                    st.text_area("내용", st.session_state.results.get('threads', ''), height=300, key="th_res")
                elif sns == "X (Twitter)":
                    st.subheader("X (Twitter) 포스팅")
                    st.caption("주의: X는 280자 제한이 있습니다.")
                    x_content = st.session_state.results.get('x', '')
                    st.text_area("내용", x_content, height=200, key="x_res")
                    st.caption(f"글자 수: {len(x_content)}자")
