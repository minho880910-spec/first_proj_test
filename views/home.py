import streamlit as st

def render_home():
    st.markdown("<h1 style='text-align: center; margin-top: 100px;'>지피지기면 백전백승</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>당신의 제품을 가장 빛나게 할 포스팅을 생성합니다.</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👈 좌측 사이드바에서 프롬프트를 입력하고 콘텐츠 제작을 시작해보세요!")
