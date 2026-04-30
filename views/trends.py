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
    is_insta = (tab_name == "Instagram")
    is_google = (tab_name == "Google")
    is_threads = (tab_name == "Threads")
    is_x = (tab_name == "X (Twitter)")
    
    col1, col2 = st.columns([2.5, 1])
    
    bot_col1 = bot_col2 = None
    if is_google or is_threads or is_x:
        bot_col1, bot_col2 = st.columns([2.5, 1])
        with col2:
            keyword_related_container = st.container()
            
        if is_google:
            with bot_col1:
                st.markdown("#### 지역별 관심도 분석 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
                map_col, rank_col = st.columns([1, 1.2])
                with rank_col:
                    category = categories[0]
                    st.markdown("#### 전국 랭킹 Top 5 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
                    rankings_container = st.container()
                with map_col:
                    map_container = st.container()
            with bot_col2:
                st.markdown("#### ❓ 함께 많이 찾는 질문 (FAQ) ❓")
                faqs_container = st.container()
        elif is_threads:
            with bot_col1:
                category = categories[0]
                st.markdown("#### 답글 / 인용이 많은 뜨거운 감자")
                hot_discussion_container = st.container()
            with bot_col2:
                st.markdown("#### 스레드 오피니언 리더", unsafe_allow_html=True)
                influencers_container = st.container()
        elif is_x:
            category = categories[0]
            with bot_col1:
                st.markdown("#### 정보 공유 및 감성 분석 지도 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
                sentiment_map_container = st.container()
            with bot_col2:
                st.markdown("#### 베스트 꿀팁 / 연관 노하우 💡 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
                tips_container = st.container()
    else:
        with col2:
            keyword_related_container = st.container()
            st.divider()
            cat_col, title_col = st.columns([1, 1])
            with cat_col:
                category = st.selectbox("카테고리 선택", categories, key=f"trend_category_{tab_name}", label_visibility="collapsed")
                st.caption("최근 1주일 기준")
            with title_col:
                if is_insta:
                    st.markdown("#### 인기 해시태그", unsafe_allow_html=True)
                else:
                    st.markdown("#### 인기검색어", unsafe_allow_html=True)

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
            main_trend_data = get_trend_summary(main_keyword, period=selected_period, platform=tab_name)
            st.session_state[state_main_data] = main_trend_data
            st.session_state[state_last_main] = main_keyword
            st.session_state[state_last_period] = selected_period

    if (state_last_cat not in st.session_state) or \
       (st.session_state[state_last_cat] != category) or \
       (st.session_state.get(state_last_cat_period) != selected_period) or \
       not st.session_state.get(state_cat_data):
        with st.spinner(f"'{category}' {tab_name} 인기검색어 가져오는 중..."):
            category_trend_data = get_trend_summary(category, period=selected_period, platform=tab_name)
            st.session_state[state_cat_data] = category_trend_data
            st.session_state[state_last_cat] = category
            st.session_state[state_last_cat_period] = selected_period

    main_data = st.session_state.get(state_main_data)
    cat_data = st.session_state.get(state_cat_data)

    if main_data and isinstance(main_data, dict):
        with col1:
            if is_insta:
                st.markdown(f"### <span style='color:#00E5FF'>{main_keyword}</span> 해시태그 언급량 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            elif is_google:
                st.markdown(f"### <span style='color:#448aff'>{main_keyword}</span> 트렌드 추이 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            elif is_threads:
                st.markdown(f"### <span style='color:#00E5FF'>{main_keyword}</span> 대화량 추이 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>(최근 24시간)</span>", unsafe_allow_html=True)
            elif is_x:
                st.markdown(f"### <span style='color:#4fc3f7'>{main_keyword}</span> 트렌드 추이 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"### <span style='color:#0056b3'>{main_keyword}</span> 검색어 순위 근황 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            x_format = '%m-%d'
                
            df_time = main_data['time_series']
            line_color = '#FF00FF' if is_threads else '#00E5FF' if (is_insta or is_google or is_x) else '#00c853'
            if is_x:
                chart = alt.Chart(df_time).mark_area(
                    line={'color': '#00E5FF'},
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[alt.GradientStop(color='#00E5FF', offset=0),
                               alt.GradientStop(color='rgba(0, 229, 255, 0)', offset=1)],
                        x1=1, x2=1, y1=1, y2=0
                    )
                ).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
            else:
                chart = alt.Chart(df_time).mark_line(color=line_color, strokeWidth=2).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
            
            if not (is_google or is_threads or is_x):
                if is_insta:
                    st.markdown("#### 인게이지먼트 / 성별 / 연령별 비중 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
                else:
                    st.markdown("#### 기기별 / 성별 / 연령별 비중 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
                st.write("---")
                subcol1, subcol2, subcol3 = st.columns(3)
                
                with subcol1:
                    st.caption("미디어 유형" if is_insta else "PC, 모바일")
                    df_device = main_data['device_ratio'].copy()
                    if is_insta:
                        df_device['device'] = ['릴스', '사진/게시물']
                    
                    d1_range = ['#00FF00', '#FF00FF'] if is_insta else ['#00c853', '#ff9800']
                    device_chart = alt.Chart(df_device).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="device", type="nominal", scale=alt.Scale(range=d1_range), legend=alt.Legend(title=None, orient="bottom")),
                        tooltip=['device', 'value']
                    ).properties(height=250)
                    st.altair_chart(device_chart, use_container_width=True)
                    
                with subcol2:
                    st.caption("성별")
                    df_gender = main_data['gender_ratio']
                    d2_range = ['#FF00FF', '#448aff'] if is_insta else ['#ff5252', '#448aff']
                    gender_chart = alt.Chart(df_gender).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="gender", type="nominal", scale=alt.Scale(range=d2_range), legend=alt.Legend(title=None, orient="bottom")),
                        tooltip=['gender', 'value']
                    ).properties(height=250)
                    st.altair_chart(gender_chart, use_container_width=True)
                    
                with subcol3:
                    st.caption("연령별")
                    df_age = main_data['age_ratio']
                    bar_color = '#00E5FF' if is_insta else '#448aff'
                    age_chart = alt.Chart(df_age).mark_bar(color=bar_color, size=15).encode(
                        x=alt.X('age:N', title='', axis=alt.Axis(labelAngle=0, grid=False)),
                        y=alt.Y('value:Q', title='', axis=None),
                        tooltip=['age', 'value']
                    ).properties(height=250)
                    st.altair_chart(age_chart, use_container_width=True)
                
        # HTML formatting for lists
        mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
        if is_insta:
            html_bg = "background-color: transparent;"
            text_color = "color: inherit;"
            num_color = "#00E5FF"
        elif is_google or is_threads or is_x:
            html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
            text_color = "color: #a9b1d6;"
            num_color = "#4fc3f7" if (is_threads or is_x) else "#448aff"
        else:
            html_bg = "background-color: #e8f5e9; border: 1px solid #c8e6c9;"
            text_color = "color: #333333;"
            num_color = "#2e7d32"

        with keyword_related_container:
            if is_insta:
                st.markdown(f"#### 📸 <span style='color:#00E5FF'>{main_keyword}</span> 연관 해시태그 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            elif is_google:
                st.markdown(f"#### <span style='color:#448aff'>{main_keyword}</span> 급상승 관련 검색어", unsafe_allow_html=True)
            elif is_threads:
                st.markdown(f"#### <span style='color:#4fc3f7'>{main_keyword}</span> 급상승 연관 대화 키워드 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>(Hot Topics)</span>", unsafe_allow_html=True)
            elif is_x:
                st.markdown(f"#### <span style='color:#a9b1d6'>{main_keyword}</span> 실시간 꿀팁 & 검색어 Top 7 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"#### <span style='color:#0056b3'>{main_keyword}</span> 연관 검색어 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            main_queries = main_data.get('top_queries', []) if main_data and isinstance(main_data, dict) else []
            
            if main_queries:
                html_content_main = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; {text_color} margin-bottom: 10px;'>"
                for i, q in enumerate(main_queries[:7] if (is_google or is_threads or is_x) else main_queries):
                    if q:
                        display_q = f"#{q.replace(' ', '')}" if is_insta else q
                        if is_threads:
                            count_html = f"<span style='color: #a9b1d6; font-size: 13px;'>{mock_counts[i % len(mock_counts)]} 포스트 🔥</span>"
                        elif is_x:
                            count_html = f"<span style='color: #4fc3f7; font-size: 13px;'>{mock_counts[i % len(mock_counts)]}</span>"
                        elif is_insta or is_google:
                            count_html = f"<span style='color: #888888;'>{mock_counts[i % len(mock_counts)]}</span>"
                        else:
                            count_html = ""
                        html_content_main += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color}; width: 25px;'>{i+1}</strong> <span>{display_q}</span></div> {count_html}</div>"
                html_content_main += "</div>"
                st.markdown(html_content_main, unsafe_allow_html=True)
            else:
                st.info("연관 데이터가 없습니다.")

        if not (is_google or is_threads or is_x):
            with col2:
                
                queries = cat_data.get('top_queries', []) if cat_data and isinstance(cat_data, dict) else []
                
                if queries:
                    html_bg2 = "background-color: transparent;" if is_insta else "background-color: #f9f9fc; border: 1px solid #e0e0e0;"
                    num_color2 = "#00E5FF" if is_insta else "#0056b3"
                    
                    html_content = f"<div style='{html_bg2} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; {text_color}'>"
                    for i, q in enumerate(queries):
                        if q:
                            display_q = f"#{q.replace(' ', '')}" if is_insta else q
                            html_content += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color2}; width: 25px;'>{i+1}</strong> <span>{display_q}</span></div> </div>" if is_insta else f"<div style='margin-bottom: 10px; font-size: 15px;'><strong style='color: {num_color2}; width: 25px; display: inline-block;'>{i+1}</strong> <span>{display_q}</span></div>"
                    html_content += "</div>"
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.info("인기 데이터가 없습니다.")
        elif is_google:
            with map_container:
                try:
                    import base64
                    map_path = r"C:\Users\Donga\.gemini\antigravity\brain\c8658fd3-d8ee-4fcf-9575-be78ad0f6083\korea_map_heatmap_1777449063355.png"
                    with open(map_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                        st.markdown(f"<img src='data:image/png;base64,{encoded_string}' style='width: 100%; border-radius: 10px;'>", unsafe_allow_html=True)
                except Exception as e:
                    st.info("지도 이미지를 불러올 수 없습니다.")

            with rankings_container:
                region_ranking = main_data.get('region_ranking')
                if region_ranking is not None and not region_ranking.empty:
                    rank_html = f"<div style='background-color: transparent; padding: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>"
                    for i, row in region_ranking.iterrows():
                        icon = "🔥 핫" if row['score'] > 75 else "☁️ 쿨"
                        rank_html += f"<div style='display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: #448aff; width: 25px;'>{i+1}</strong> <span>{row['region']} ({row['score']})</span></div> <span style='font-size: 12px;'>{icon}</span></div>"
                    rank_html += "</div>"
                    st.markdown(rank_html, unsafe_allow_html=True)

            with faqs_container:
                faqs = main_data.get('faqs', [])
                if faqs:
                    faq_html = f"<div style='background-color: #1a1b26; border: 1px solid #292e42; padding: 15px; border-radius: 10px; height: 350px; overflow-y: auto; color: #a9b1d6;'>"
                    for faq in faqs:
                        faq_html += f"<div style='margin-bottom: 25px; font-size: 15px; display: flex; justify-content: space-between; align-items: center;'><span>• {faq}</span></div>"
                    faq_html += "</div>"
                    st.markdown(faq_html, unsafe_allow_html=True)
                else:
                    st.info("FAQ 데이터가 없습니다.")

        elif is_threads:
            with hot_discussion_container:
                hot_discussions = main_data.get('hot_discussions', [])
                if hot_discussions:
                    cols = st.columns(3)
                    for i, disc in enumerate(hot_discussions[:3]):
                        with cols[i]:
                            st.markdown(f"<h5 style='color: #a9b1d6; font-size: 16px; margin-bottom: 5px;'><span style='color: #4fc3f7;'>{i+1}</span> {disc['title']}</h5>", unsafe_allow_html=True)
                            st.markdown(f"<div style='font-size: 13px; margin-bottom: 15px;'><span style='color: #00E5FF;'>↪ {disc['replies']}답글</span> &nbsp; <span style='color: #00E5FF;'>{disc['quotes']}인용</span> &nbsp; <span style='color: #FF00FF;'>{disc['likes']}좋아요</span></div>", unsafe_allow_html=True)
                            
                            import textwrap
                            card_html = textwrap.dedent(f"""
                            <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; color: #a9b1d6;'>
                                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                                    <div style='width: 35px; height: 35px; background-color: #448aff; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 18px; margin-right: 10px;'>👤</div>
                                    <div style='line-height: 1.2;'>
                                        <div style='font-weight: bold; font-size: 14px;'>{disc['handle']}</div>
                                        <div style='font-size: 12px; color: #888888;'>{disc['author']}</div>
                                    </div>
                                    <div style='margin-left: auto; color: #888888; font-size: 12px;'>{disc['time']} •••</div>
                                </div>
                                <div style='font-size: 14px; margin-bottom: 15px; line-height: 1.5;'>
                                    {disc['content']}
                                </div>
                                <div style='display: flex; gap: 15px; color: #888888; font-size: 16px;'>
                                    <span>♡</span> <span>💬</span> <span>⟲</span> <span>↗</span>
                                </div>
                                <div style='margin-top: 10px; font-size: 12px; color: #888888;'>
                                    {disc['replies']} 답글
                                </div>
                            </div>
                            """)
                            st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.info("뜨거운 감자 데이터가 없습니다.")
            
            with influencers_container:
                influencers = main_data.get('top_influencers', [])
                if influencers:
                    inf_html = "<div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; color: #a9b1d6;'>"
                    import textwrap
                    for inf in influencers:
                        inf_html += textwrap.dedent(f"""
                        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;'>
                            <div style='display: flex; align-items: center;'>
                                <div style='color: #4fc3f7; font-size: 18px; font-weight: bold; width: 25px;'>{inf['rank']}</div>
                                <div style='width: 40px; height: 40px; background-color: #e0e0e0; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 20px; margin-right: 10px;'>🧑‍🍳</div>
                                <div style='line-height: 1.2;'>
                                    <div style='font-size: 14px; font-weight: bold;'>{inf['handle']}</div>
                                    <div style='font-size: 12px; color: #888888;'>{inf['name']}</div>
                                </div>
                            </div>
                            <div style='text-align: right; line-height: 1.2;'>
                                <div style='font-size: 13px;'>{inf['mentions']} 멘션</div>
                                <div style='font-size: 12px; color: #888888;'>{inf['followers']} 팔로워</div>
                            </div>
                        </div>
                        """)
                    inf_html += "</div>"
                    st.markdown(inf_html, unsafe_allow_html=True)
                else:
                    st.info("인플루언서 데이터가 없습니다.")
        elif is_x:
            with sentiment_map_container:
                sc1, sc2, sc3, sc4 = st.columns([1.2, 2, 1, 1])
                
                with sc1:
                    st.markdown("<div style='text-align: center; font-size: 14px; color: #a9b1d6; margin-bottom: 5px;'>누적 언급량: 98k+</div>", unsafe_allow_html=True)
                    donut1_html = """
                    <div style='position: relative; width: 120px; height: 120px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% 60%, #FF00FF 60% 85%, #448aff 85% 95%, #888888 95% 100%); display: flex; justify-content: center; align-items: center;'>
                        <div style='width: 80px; height: 80px; background-color: #1a1b26; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #00E5FF;'>60%</div>
                    </div>
                    <div style='font-size: 11px; color: #a9b1d6; margin-top: 10px; line-height: 1.5;'>
                        <span style='color:#00E5FF'>●</span> 정보/노하우 (60%)<br>
                        <span style='color:#FF00FF'>●</span> 긍정 감성 (25%)<br>
                        <span style='color:#448aff'>●</span> 리뷰/후기 (10%)<br>
                        <span style='color:#888888'>●</span> 기타 (5%)
                    </div>
                    <div style='text-align: center; margin-top: 10px; font-weight: bold; color: #a9b1d6;'>게시물 성향</div>
                    """
                    st.markdown(donut1_html, unsafe_allow_html=True)
                
                with sc2:
                    st.markdown(f"<div style='text-align: center; font-size: 14px; color: #a9b1d6; margin-bottom: 5px;'>{main_keyword} 테마 맵</div>", unsafe_allow_html=True)
                    wordcloud_html = f"""
                    <div style='position: relative; height: 180px; background-color: transparent; display: flex; justify-content: center; align-items: center;'>
                        <div style='position: absolute; top: 10%; left: 20%; background-color: rgba(255, 0, 255, 0.2); border: 1px solid #FF00FF; color: #FF00FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);'>존맛</div>
                        <div style='position: absolute; top: 15%; right: 20%; background-color: rgba(255, 0, 255, 0.2); border: 1px solid #FF00FF; color: #FF00FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);'>감성적</div>
                        <div style='position: absolute; top: 40%; left: 10%; background-color: rgba(68, 138, 255, 0.2); border: 1px solid #448aff; color: #448aff; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(68, 138, 255, 0.5);'>행복적</div>
                        <div style='position: absolute; top: 45%; right: 10%; background-color: rgba(0, 229, 255, 0.2); border: 1px solid #00E5FF; color: #00E5FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);'>귀여운</div>
                        <div style='position: absolute; top: 50%; left: 40%; background-color: #00E5FF; color: #000; padding: 8px 15px; border-radius: 20px; font-size: 18px; font-weight: bold; box-shadow: 0 0 15px rgba(0, 229, 255, 0.8);'>행복</div>
                        <div style='position: absolute; bottom: 20%; left: 15%; background-color: rgba(0, 229, 255, 0.2); border: 1px solid #00E5FF; color: #00E5FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);'>카페투어</div>
                        <div style='position: absolute; bottom: 25%; right: 15%; background-color: rgba(68, 138, 255, 0.2); border: 1px solid #448aff; color: #448aff; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(68, 138, 255, 0.5);'>인증샷</div>
                        <div style='position: absolute; bottom: 5%; right: 30%; background-color: rgba(68, 138, 255, 0.2); border: 1px solid #448aff; color: #448aff; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(68, 138, 255, 0.5);'>성수동맛집</div>
                    </div>
                    <div style='text-align: center; margin-top: 10px; font-weight: bold; color: #a9b1d6;'>{main_keyword} 연관 <span style='color: #FF00FF;'>감성</span> 클러스터</div>
                    """
                    st.markdown(wordcloud_html, unsafe_allow_html=True)
                
                with sc3:
                    st.markdown("<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 25px;'>&nbsp;</div>", unsafe_allow_html=True)
                    gauge_html = """
                    <div style='position: relative; width: 100px; height: 50px; margin: 0 auto; background-color: #292e42; border-top-left-radius: 100px; border-top-right-radius: 100px; overflow: hidden;'>
                        <div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: conic-gradient(from 270deg, #00E5FF 0deg, #448aff 90deg, #FF00FF 180deg); opacity: 0.8;'></div>
                        <div style='position: absolute; bottom: 0; left: 50%; width: 60px; height: 30px; background-color: #1a1b26; border-top-left-radius: 60px; border-top-right-radius: 60px; transform: translateX(-50%);'></div>
                        <div style='position: absolute; bottom: 0; left: 50%; width: 2px; height: 40px; background-color: #a9b1d6; transform-origin: bottom center; transform: translateX(-50%) rotate(45deg);'></div>
                    </div>
                    <div style='display: flex; justify-content: space-between; width: 120px; margin: 5px auto 0; font-size: 11px; color: #a9b1d6;'>
                        <span>Low</span>
                        <span>매우 만족</span>
                    </div>
                    <div style='text-align: center; margin-top: 20px; font-weight: bold; color: #a9b1d6;'>감성 만족도</div>
                    """
                    st.markdown(gauge_html, unsafe_allow_html=True)
                
                with sc4:
                    st.markdown("<div style='text-align: center; font-size: 14px; color: #a9b1d6; margin-bottom: 5px;'>누적 언급량: 98k+</div>", unsafe_allow_html=True)
                    st.markdown("<div style='text-align: center; font-size: 12px; color: #ffb74d; margin-bottom: 5px;'>실시간 긍정 감성 전파 중</div>", unsafe_allow_html=True)
                    donut2_html = """
                    <div style='position: relative; width: 90px; height: 90px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% 35%, #FF00FF 35% 75%, #448aff 75% 95%, #888888 95% 100%); display: flex; justify-content: center; align-items: center;'>
                        <div style='width: 50px; height: 50px; background-color: #1a1b26; border-radius: 50%;'></div>
                        <div style='position: absolute; top: 35%; right: 10%; font-size: 10px; color: #FF00FF; font-weight: bold;'>40%</div>
                        <div style='position: absolute; bottom: 15%; left: 20%; font-size: 10px; color: #00E5FF; font-weight: bold;'>35%</div>
                        <div style='position: absolute; top: 35%; left: 10%; font-size: 10px; color: #448aff; font-weight: bold;'>20%</div>
                    </div>
                    <div style='text-align: center; margin-top: 15px; font-weight: bold; color: #a9b1d6;'>유입 맥락</div>
                    """
                    st.markdown(donut2_html, unsafe_allow_html=True)

            with tips_container:
                st.markdown("<div style='text-align: right; font-size: 12px; color: #888888; margin-bottom: 10px;'><span>🔖 인용</span> &nbsp;|&nbsp; <span>💬 맨션</span></div>", unsafe_allow_html=True)
                tips_html = f"""
                <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; margin-bottom: 10px;'>
                    <div style='display: flex; align-items: flex-start;'>
                        <div style='color: #4fc3f7; font-size: 16px; font-weight: bold; width: 20px;'>1</div>
                        <div>
                            <div style='color: #a9b1d6; font-size: 14px; margin-bottom: 5px;'>[{main_keyword}] 에어프라이어 완벽 해동! 시간 ❔</div>
                            <div style='color: #ffffff; font-size: 15px; font-weight: bold; margin-bottom: 5px;'>별 굽기 온도</div>
                            <div style='color: #888888; font-size: 12px;'>⏱️ 5분 &nbsp; 🌡️ 180도 &nbsp; 냉동은 5~7분이 적당합니다.</div>
                        </div>
                    </div>
                </div>
                <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; margin-bottom: 10px;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='color: #4fc3f7; font-size: 16px; font-weight: bold; width: 20px;'>2</div>
                        <div>
                            <div style='color: #a9b1d6; font-size: 14px; margin-bottom: 5px;'>맛있게 먹는 법: 버터 & 소금 조합 ❔</div>
                            <div style='color: #888888; font-size: 12px;'>🥐 맛있게 먹는 법: 버터 & 소금 조합</div>
                        </div>
                    </div>
                </div>
                <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='color: #4fc3f7; font-size: 16px; font-weight: bold; width: 20px;'>3</div>
                        <div>
                            <div style='color: #a9b1d6; font-size: 14px; margin-bottom: 5px;'>{main_keyword}과 잘 어울리는 음료 BEST 3</div>
                            <div style='color: #888888; font-size: 12px;'>☕ 🥛 🍵</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(tips_html, unsafe_allow_html=True)
    elif main_data:
        st.write(main_data)

def render_trends():
    st.header("📈 최신 트렌드")
    
    categories_dict = {
        "Instagram": [
            "패션 및 스타일", "음식 및 음료", "여행", "엔터테인먼트", 
            "운동 및 건강", "예술 및 디자인", "반려동물", "비즈니스 및 기술", "해당 카테고리 없음"
        ],
        "default": [
            "화장품/뷰티", "IT/가전", "패션/의류", "식품/건강", 
            "인테리어/가구", "여행/숙박", "금융/재테크", "게임/엔터", 
            "교육/도서", "자동차/모빌리티", "출산/육아", "반려동물 용품", "취미/스포츠", "해당 카테고리 없음"
        ]
    }
    
    prompt_input = st.session_state.get("prompt_input", "").strip()
    global_main_keyword = None
    
    if prompt_input:
        if ('last_prompt_for_keyword' not in st.session_state) or (st.session_state.last_prompt_for_keyword != prompt_input):
            with st.spinner("프롬프트에서 핵심 키워드 및 카테고리 분석 중..."):
                extracted_keyword = extract_keyword(prompt_input)
                st.session_state.extracted_keyword = extracted_keyword
                
                mapped_categories = {}
                for key, cats in categories_dict.items():
                    mapped_categories[key] = classify_category(extracted_keyword, cats[:-1])
                
                tab_names = ["Naver", "Google", "Instagram", "Threads", "X (Twitter)"]
                for t in tab_names:
                    cat_key = "Instagram" if t == "Instagram" else "default"
                    st.session_state[f"trend_category_{t}"] = mapped_categories[cat_key]
                    
                st.session_state.last_prompt_for_keyword = prompt_input
                
        global_main_keyword = st.session_state.extracted_keyword

    tab_names = ["Naver", "Google", "Instagram", "Threads", "X (Twitter)"]
    tabs = st.tabs(tab_names)
    
    for i, tab_name in enumerate(tab_names):
        with tabs[i]:
            tab_cats = categories_dict["Instagram"] if tab_name == "Instagram" else categories_dict["default"]
            render_trend_tab(tab_name, tab_cats, prompt_input, global_main_keyword)
