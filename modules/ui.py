import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("✨ 지피지기")
        st.caption("포스팅 자동 생성기")
        st.write("---")

        categories = [
            "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
            "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
            "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠"
        ]
        
        # We need default values in session state for persistence
        if 'category' not in st.session_state:
            st.session_state.category = categories[0]
        if 'prompt_text' not in st.session_state:
            st.session_state.prompt_text = ""
        if 'tone' not in st.session_state:
            st.session_state.tone = "전문적인"

        st.selectbox("카테고리", categories, key='category')
        st.text_area("프롬프트 입력", 
                     placeholder="예: 신제품 립스틱 출시 홍보를 위한 인스타그램 글 작성해줘\n(자세한 타겟 고객이나 강조할 특징을 함께 적어주시면 더 좋습니다.)", 
                     height=150, 
                     key='prompt_text')
        
        st.selectbox("톤앤매너", ["전문적인", "친근한", "유머러스한", "감성적인"], key='tone')
        
        st.write("---")
