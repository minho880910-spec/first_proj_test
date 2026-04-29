import os
import streamlit as st
import altair as alt
from openai import OpenAI
from modules.trend_analyzer import get_trend_summary
from modules.keyword_extractor import extract_keyword

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_category(keyword: str, categories: list) -> str:
    if not keyword:
        return "해당 카테고리 없음"
        
    categories_str = ", ".join(categories)
    system_prompt = (
        f"당신은 검색어 키워드를 다음 주어진 카테고리 중 하나로 분류하는 전문가입니다.\n"
        f"카테고리 목록: [{categories_str}]\n"
        f"사용자의 키워드가 위 카테고리 중 어디에 속하는지 판단하여, 오직 해당 카테고리 이름만 정확하게 출력하세요.\n"
        f"만약 키워드가 어느 카테고리에도 명확히 속하지 않는다면, '해당 카테고리 없음'이라고 출력하세요.\n"
        f"어떠한 설명이나 추가 문구 없이 카테고리명만 출력해야 합니다."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": keyword}
            ],
            temperature=0.1
        )
        category = response.choices[0].message.content.strip()
        category = category.replace('"', '').replace("'", "").rstrip('.')
        
        if category in categories:
            return category
        return "해당 카테고리 없음"
    except Exception as e:
        print(f"Category classification error: {e}")
        return "해당 카테고리 없음"

def render_trend_tab(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    col1, col2 = st.columns([2.5, 1])

    with col2:
        keyword_related_container = st.container()
        st.divider()
        category = st.selectbox("카테고리 선택", categories, key=f"trend_category_{tab_name}", label_visibility="collapsed")

    if not prompt_input:
        main_keyword = category
    else:
        main_keyword = global_main_keyword

    selected_period = "now 7-d"

    state_last_main = f"last_main_keyword_{tab_name}"
    state_last_period = f"last_period_{tab_name}"
    state_main_data = f"main_trend_data_{tab_name}"
    state_last_cat = f"last_trend_category_{tab_name}"
    state_last_cat_period = f"last_cat_period_{tab_name}"
    state_cat_data = f"category_trend_data_{tab_name}"

    if (state_last_main not in st.session_state) or \
       (st.session_state[state_last_main] != main_keyword) or \
       (st.session_state.get(state_last_period) != selected_period) or \
       not st.session_state.get(state_main_data):
        with st.spinner(f"'{main_keyword}' {tab_name} 트렌드 분석 중..."):
            main_trend_data = get_trend_summary(main_keyword, period=selected_period)
            st.session_state[state_main_data] = main_trend_data
            st.session_state[state_last_main] = main_keyword
            st.session_state[state_last_period] = selected_period

    if (state_last_cat not in st.session_state) or \
       (st.session_state[state_last_cat] != category) or \
       (st.session_state.get(state_last_cat_period) != selected_period) or \
       not st.session_state.get(state_cat_data):
        with st.spinner(f"'{category}' {tab_name} 인기검색어 가져오는 중..."):
            category_trend_data = get_trend_summary(category, period=selected_period)
            st.session_state[state_cat_data] = category_trend_data
            st.session_state[state_last_cat] = category
            st.session_state[state_last_cat_period] = selected_period

    main_data = st.session_state.get(state_main_data)
    cat_data = st.session_state.get(state_cat_data)

    if main_data and isinstance(main_data, dict):
        with col1:
            st.markdown(f"### <span style='color:#0056b3'>{main_keyword}</span> {tab_name} 검색어 순위 근황 (최근 1주일 기준)", unsafe_allow_html=True)
            
            x_format = '%m-%d'
                
            df_time = main_data['time_series']
            chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=2).encode(
                x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
            
            st.markdown("#### 기기별 / 성별 / 연령별 비중 (최근 1주일 기준)")
            st.write("---")
            subcol1, subcol2, subcol3 = st.columns(3)
            
            with subcol1:
                st.caption("PC, 모바일")
                df_device = main_data['device_ratio']
                device_chart = alt.Chart(df_device).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="value", type="quantitative"),
                    color=alt.Color(field="device", type="nominal", scale=alt.Scale(range=['#00c853', '#ff9800']), legend=alt.Legend(title=None, orient="bottom")),
                    tooltip=['device', 'value']
                ).properties(height=250)
                st.altair_chart(device_chart, use_container_width=True)
                
            with subcol2:
                st.caption("여성, 남성")
                df_gender = main_data['gender_ratio']
                gender_chart = alt.Chart(df_gender).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="value", type="quantitative"),
                    color=alt.Color(field="gender", type="nominal", scale=alt.Scale(range=['#ff5252', '#448aff']), legend=alt.Legend(title=None, orient="bottom")),
                    tooltip=['gender', 'value']
                ).properties(height=250)
                st.altair_chart(gender_chart, use_container_width=True)
                
            with subcol3:
                st.caption("연령별")
                df_age = main_data['age_ratio']
                age_chart = alt.Chart(df_age).mark_bar(color='#448aff', size=15).encode(
                    x=alt.X('age:N', title='', axis=alt.Axis(labelAngle=0, grid=False)),
                    y=alt.Y('value:Q', title='', axis=None),
                    tooltip=['age', 'value']
                ).properties(height=250)
                st.altair_chart(age_chart, use_container_width=True)
                
        with keyword_related_container:
            st.markdown(f"#### {main_keyword} 연관 검색어")
            st.caption("최근 1주일 기준")
            
            main_queries = main_data.get('top_queries', []) if main_data and isinstance(main_data, dict) else []
            
            if main_queries:
                html_content_main = "<div style='background-color: #e8f5e9; border: 1px solid #c8e6c9; padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; margin-bottom: 10px; color: #333333;'>"
                for i, q in enumerate(main_queries):
                    if q:
                        html_content_main += f"<div style='margin-bottom: 10px; font-size: 15px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> <span>{q}</span></div>"
                html_content_main += "</div>"
                st.markdown(html_content_main, unsafe_allow_html=True)
            else:
                st.info("연관 검색어 데이터가 없습니다.")

        with col2:
            st.markdown("#### 인기검색어")
            st.caption(f"'{category}' 카테고리 (최근 1주일)")
            
            queries = cat_data.get('top_queries', []) if cat_data and isinstance(cat_data, dict) else []
            
            if queries:
                html_content = "<div style='background-color: #f9f9fc; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #333333;'>"
                for i, q in enumerate(queries):
                    if q:
                        html_content += f"<div style='margin-bottom: 10px; font-size: 15px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> <span>{q}</span></div>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("인기 검색어 데이터가 없습니다.")
                
    elif main_data:
        st.write(main_data)

def render_trends():
    st.header("📈 최신 트렌드")
    
    categories = [
        "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
        "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
        "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠", "해당 카테고리 없음"
    ]
    
    prompt_input = st.session_state.get("prompt_input", "").strip()
    global_main_keyword = None
    
    if prompt_input:
        if ('last_prompt_for_keyword' not in st.session_state) or (st.session_state.last_prompt_for_keyword != prompt_input):
            with st.spinner("프롬프트에서 핵심 키워드 및 카테고리 분석 중..."):
                extracted_keyword = extract_keyword(prompt_input)
                mapped_category = classify_category(extracted_keyword, categories[:-1])
                
                st.session_state.extracted_keyword = extracted_keyword
                tab_names = ["Naver", "Google", "Instagram", "Threads", "X (Twitter)"]
                for t in tab_names:
                    st.session_state[f"trend_category_{t}"] = mapped_category
                st.session_state.last_prompt_for_keyword = prompt_input
                
        global_main_keyword = st.session_state.extracted_keyword

    tab_names = ["Naver", "Google", "Instagram", "Threads", "X (Twitter)"]
    tabs = st.tabs(tab_names)
    
    for i, tab_name in enumerate(tab_names):
        with tabs[i]:
            render_trend_tab(tab_name, categories, prompt_input, global_main_keyword)
