import streamlit as st
from modules.trend_analyzer import get_trend_summary

def render_trends():
    st.header("📈 키워드 트렌드 분석")
    
    categories = [
        "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
        "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
        "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠"
    ]
    category = st.selectbox("카테고리 선택", categories, key="trend_category")
    
    if ('last_trend_category' not in st.session_state) or (st.session_state.last_trend_category != category) or not st.session_state.get('trend_data'):
        with st.spinner("트렌드 데이터를 가져오는 중..."):
            trend_data = get_trend_summary(category)
            st.session_state.trend_data = trend_data
            st.session_state.last_trend_category = category

    if st.session_state.get('trend_data'):
        st.write(st.session_state.trend_data)
