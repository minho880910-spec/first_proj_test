import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    col1, col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        st.divider()
        st.markdown("#### 📂 카테고리 인기 검색어")
        
        # 카테고리 자동 동기화
        auto_cat = st.session_state.get(f"trend_category_{tab_name}")
        last_keyword = st.session_state.get(f"last_keyword_{tab_name}", "")
        if global_main_keyword != last_keyword:
            st.session_state[f"last_keyword_{tab_name}"] = global_main_keyword
            if auto_cat in categories:
                st.session_state[f"sb_{tab_name}"] = auto_cat

        category = st.selectbox("카테고리 선택", categories, key=f"sb_{tab_name}", label_visibility="collapsed")
        st.caption(f"📍 분석 대상: **{category}**")

    main_keyword = global_main_keyword if prompt_input else category
    main_data, _ = fetch_trend_data(tab_name, main_keyword, category)

    if main_data:
        is_ai = main_data.get('is_ai_generated', False)
        if is_ai:
            st.info("✨ 네이버 API 집계 지연으로 인해 **AI 분석 예상 트렌드**를 표시 중입니다.")

        with col1:
            # 1. 검색 추이
            st.markdown(f"### <span style='color:#00c853'>{main_keyword}</span> 검색 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='상대지수'), tooltip=['date:T', 'clicks:Q']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

            # 2. 하단 지표
            st.write("") 
            subcol1, subcol2, subcol3 = st.columns(3)
            suffix = " (AI 예측)" if is_ai else ""
            
            with subcol1:
                st.caption(f"💻 기기별{suffix}")
                df = main_data.get('device_ratio')
                if df is not None:
                    c = alt.Chart(df).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("device:N", scale=alt.Scale(range=['#00c853', '#ff9800'])), tooltip=['device', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol2:
                st.caption(f"👫 성별 비중{suffix}")
                df = main_data.get('gender_ratio')
                if df is not None:
                    c = alt.Chart(df).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("gender:N", scale=alt.Scale(range=['#448aff', '#ff5252'])), tooltip=['gender', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol3:
                st.caption(f"🎂 연령별 비중{suffix}")
                df = main_data.get('age_ratio')
                if df is not None:
                    c = alt.Chart(df).mark_bar(color='#448aff').encode(
                        x=alt.X('age:N', title=None, axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('value:Q', axis=None), tooltip=['age', 'value']
                    ).properties(height=200)
                    st.altair_chart(c, use_container_width=True)

        with col2:
            st.write("") 
            ranking = main_data.get('category_ranking', [])
            if ranking:
                st.markdown(f"#### 🏆 {category} 인기순{suffix}")
                html = f"<div style='background-color: {'#fff3e0' if is_ai else '#f9f9fc'}; padding: 15px; border-radius: 10px; height: 300px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(ranking):
                    html += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html + "</div>", unsafe_allow_html=True)