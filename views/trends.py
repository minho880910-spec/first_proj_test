import streamlit as st
from modules.keyword_extractor import extract_keyword
from modules.category_classifier import classify_category
from views.trends_tabs import naver_tab, google_tab, instagram_tab, threads_tab, x_twitter_tab

def render_trends():
    st.header("📈 최신 트렌드")
    
    # 1. 프롬프트 입력 확인 (없을 경우 안내 메시지 출력 후 중단)
    prompt_input = st.session_state.get("prompt_input", "").strip()
    
    if not prompt_input:
        st.info("💡 프롬프트를 입력하면 분석이 시작됩니다.")
        return  # 입력이 없으면 아래 분석 및 탭 렌더링을 하지 않음

    # 2. 카테고리 정의
    categories_dict = {
        "Naver": [
            "패션의류", "패션잡화", "화장품/미용", "디지털/가전", 
            "가구/인테리어", "출산/육아", "식품", "스포츠/레저", "생활/건강", 
            "여가/생활편의", "면세점", "도서", "해당 카테고리 없음"
        ],
        "Instagram": [
            "패션 및 스타일", "음식 및 음료", "여행", "엔터테인먼트", 
            "운동 및 건강", "예술 및 디자인", "반려동물", "비즈니스 및 기술", "해당 카테고리 없음"
        ]
    }
    
    global_main_keyword = None
    
    # 3. 키워드 추출 및 카테고리 분류 로직
    if ('last_prompt_for_keyword' not in st.session_state) or (st.session_state.last_prompt_for_keyword != prompt_input):
        with st.spinner("프롬프트 분석 중..."):
            extracted_keyword = extract_keyword(prompt_input)
            st.session_state.extracted_keyword = extracted_keyword
            
            for platform in ["Naver", "Instagram"]:
                st.session_state[f"trend_category_{platform}"] = classify_category(
                    extracted_keyword, categories_dict[platform][:-1]
                )
            
            st.session_state.last_prompt_for_keyword = prompt_input
    
    global_main_keyword = st.session_state.extracted_keyword

    # 4. 탭 렌더링
    tab_names = ["Naver", "Google", "Instagram", "Threads", "X (Twitter)"]
    tabs = st.tabs(tab_names)
    
    for i, tab_name in enumerate(tab_names):
        with tabs[i]:
            if tab_name == "Naver":
                naver_tab.render(tab_name, categories_dict["Naver"], prompt_input, global_main_keyword)
            elif tab_name == "Instagram":
                instagram_tab.render(tab_name, categories_dict["Instagram"], prompt_input, global_main_keyword)
            elif tab_name == "Google":
                google_tab.render(tab_name, prompt_input, global_main_keyword)
            elif tab_name == "Threads":
                threads_tab.render(tab_name, prompt_input, global_main_keyword)
            elif tab_name == "X (Twitter)":
                x_twitter_tab.render(tab_name, prompt_input, global_main_keyword)