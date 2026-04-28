import streamlit as st
from modules.llm_engine import generate_content
from modules.database import add_history

def render_result():
    st.header("✨ 콘텐츠 제작 결과")
    
    tone = st.selectbox("톤앤매너 선택", ["전문적인", "친근한", "유머러스한", "감성적인"], key="tone_select")
    
    auto_gen = st.session_state.pop("auto_generate", False)
    
    if auto_gen:
        title = st.session_state.get("prompt_input", "")
        if title:
            with st.spinner("콘텐츠를 생성 중입니다..."):
                # 트렌드 탭에서 선택한 카테고리가 있으면 사용하고, 없으면 기본값 사용
                category = st.session_state.get("trend_category", "미지정")
                results = generate_content(category, title, tone)
                st.session_state.results = results
                add_history(category, title, tone, results.get('instagram', ''), results.get('threads', ''), results.get('x', ''))
        else:
            st.warning("👈 좌측 메뉴에서 프롬프트를 먼저 입력해주세요.")

    if st.session_state.get('results'):
        st.write("---")
        tab1, tab2, tab3 = st.tabs(["📸 Instagram", "💬 Threads", "🐦 X (Twitter)"])
        
        with tab1:
            st.subheader("Instagram 포스팅")
            st.text_area("내용", st.session_state.results.get('instagram', ''), height=300, key="ig_res")
            
        with tab2:
            st.subheader("Threads 포스팅")
            st.text_area("내용", st.session_state.results.get('threads', ''), height=300, key="th_res")
            
        with tab3:
            st.subheader("X (Twitter) 포스팅")
            st.caption("주의: X는 280자 제한이 있습니다.")
            x_content = st.session_state.results.get('x', '')
            st.text_area("내용", x_content, height=200, key="x_res")
            st.caption(f"글자 수: {len(x_content)}자")
