import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    col1, col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        st.divider()
        st.markdown("#### 📂 카테고리 선택", unsafe_allow_html=True)
        cat_col, _ = st.columns([1, 0.1])
        with cat_col:
            auto_cat = st.session_state.get(f"trend_category_{tab_name}", categories[0])
            try:
                default_idx = categories.index(auto_cat)
            except ValueError:
                default_idx = 0
            
            category = st.selectbox("카테고리 선택", categories, index=default_idx, key=f"sb_{tab_name}", label_visibility="collapsed")
            st.caption("네이버 쇼핑인사이트 기준")

    main_keyword = global_main_keyword if prompt_input else category
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword, category)

    if main_data and isinstance(main_data, dict):
        with col1:
            st.markdown(f"### <span style='color:#00c853'>{main_keyword}</span> 검색 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='상대지수'),
                    tooltip=['date:T', 'clicks:Q']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("해당 키워드에 대한 검색 추이 데이터가 없습니다.")

            st.write("") 
            subcol1, subcol2, subcol3 = st.columns(3)
            
            # 비중 분석 (데이터가 있을 때만 렌더링)
            with subcol1:
                st.caption("💻 기기별")
                df_device = main_data.get('device_ratio')
                if df_device is not None:
                    c = alt.Chart(df_device).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("device:N", scale=alt.Scale(range=['#00c853', '#ff9800'])), tooltip=['device', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol2:
                st.caption("👫 성별")
                df_gender = main_data.get('gender_ratio')
                if df_gender is not None:
                    c = alt.Chart(df_gender).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("gender:N", scale=alt.Scale(range=['#448aff', '#ff5252'])), tooltip=['gender', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol3:
                st.caption("🎂 연령별")
                df_age = main_data.get('age_ratio')
                if df_age is not None:
                    c = alt.Chart(df_age).mark_bar(color='#448aff').encode(
                        x=alt.X('age:N', axis=alt.Axis(labelAngle=0)), y='value:Q', tooltip=['age', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)

    # 우측 실시간 정보
    with keyword_related_container:
        st.markdown(f"#### 🔍 {main_keyword} 연관어")
        main_queries = main_data.get('top_queries', []) if main_data else []
        if main_queries:
            html = f"<div style='background-color: #f1f8e9; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto;'>"
            for i, q in enumerate(main_queries):
                html += f"<div style='margin-bottom: 8px;'><strong style='color: #2e7d32;'>{i+1}</strong> {q}</div>"
            st.markdown(html + "</div>", unsafe_allow_html=True)

    with col2:
        st.write("") 
        cat_ranking = cat_data.get('category_ranking', []) if isinstance(cat_data, dict) else []
        if cat_ranking:
            st.markdown(f"#### 🏆 {category} 인기순")
            html = f"<div style='background-color: #f9f9fc; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto;'>"
            for i, q in enumerate(cat_ranking):
                html += f"<div style='margin-bottom: 8px;'><strong style='color: #0056b3;'>{i+1}</strong> {q}</div>"
            st.markdown(html + "</div>", unsafe_allow_html=True)
        else:
            st.caption("카테고리 랭킹 정보가 없습니다.")