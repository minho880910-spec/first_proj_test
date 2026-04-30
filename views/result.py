import streamlit as st
from modules.llm_engine import generate_content
from modules.database import add_history

def render_result():
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
        /* 제작하기 버튼(primary) 스타일 */
        div.stButton > button[kind="primary"] {
            background-color: white !important;
            color: black !important; /* 텍스트 검은색으로 변경 */
            border-color: #CCCCCC !important;
            font-weight: bold !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #F3F4F6 !important;
            border-color: #999999 !important;
            color: black !important;
        }
        /* 플랫폼 선택(멀티셀렉트) 태그 스타일 */
        span[data-baseweb="tag"] {
            background-color: #FFFACD !important; /* 연한 노랑색 (LemonChiffon) */
            padding: 6px 16px !important; /* 좌우 길이를 적절히 늘림 */
            margin-right: 8px !important; /* 태그 간 간격 추가 */
            border-radius: 16px !important; /* 둥글게 */
            border: 1px solid #F0E68C !important;
        }
        span[data-baseweb="tag"] span {
            color: #333333 !important; /* 글자는 잘 보이게 진한 색 */
            font-size: 14px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.header("📢 콘텐츠 생성")
    
    tone_options = ["전문적인", "친근한", "유머러스한", "감성적인", "직접 입력"]
    selected_tone = st.selectbox("어떤 느낌으로 쓸까요?💬", tone_options, key="tone_select")
    
    if selected_tone == "직접 입력":
        tone = st.text_input("원하는 톤앤매너를 직접 입력해주세요 ✍️", key="custom_tone_input")
    else:
        tone = selected_tone
    
    sns_options = ["Instagram", "Threads", "X (Twitter)"]
    selected_sns = st.multiselect("포스팅 할 SNS 선택", sns_options, default=sns_options, key="sns_select")
    
    # 버튼 길이를 3분의 1로 줄이기 위해 컬럼 사용
    col1, col2, col3 = st.columns(3)
    with col1:
        submit_btn = st.button("제작하기", type="primary", use_container_width=True)
    
    if submit_btn:
        title = st.session_state.get("prompt_input", "")
        if title:
            if not selected_sns:
                st.warning("포스팅 할 SNS를 최소 하나 이상 선택해주세요.")
            elif selected_tone == "직접 입력" and not tone.strip():
                st.warning("원하는 톤앤매너를 입력해주세요.")
            else:
                with st.spinner("콘텐츠를 생성 중입니다..."):
                    # 트렌드 탭에서 선택한 카테고리가 있으면 사용하고, 없으면 기본값 사용
                    category = st.session_state.get("trend_category", "미지정")
                    results = generate_content(category, title, tone)
                    
                    st.session_state.results = results
                    st.session_state.selected_sns = selected_sns
                    
                    # 새 결과를 텍스트 에어리어에 즉시 반영하기 위해 session_state 업데이트
                    st.session_state['ig_res'] = results.get('instagram', '')
                    st.session_state['th_res'] = results.get('threads', '')
                    st.session_state['x_res'] = results.get('x', '')

                            
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
                    st.text_area("내용", x_content, height=280, key="x_res")
                    st.caption(f"글자 수: {len(x_content)}자")
