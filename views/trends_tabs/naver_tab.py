import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    # 레이아웃 정의
    col1, col2 = st.columns([2.5, 1])
    
    # 카테고리 설정
    auto_cat = st.session_state.get(f"trend_category_{tab_name}")
    last_keyword = st.session_state.get(f"last_keyword_{tab_name}", "")
    if global_main_keyword != last_keyword:
        st.session_state[f"last_keyword_{tab_name}"] = global_main_keyword
        if auto_cat in categories:
            st.session_state[f"sb_{tab_name}"] = auto_cat

    # 데이터 호출
    main_keyword = global_main_keyword if prompt_input else categories[0]
    temp_category = st.session_state.get(f"sb_{tab_name}", categories[0])
    main_data, _ = fetch_trend_data(tab_name, main_keyword, temp_category)

    if main_data:
        # --- 좌측 컬럼 (그래프 및 상세 비중) ---
        with col1:
            # (1) 검색 추이 그래프
            st.markdown(f"### <span style='color:#00c853'>{main_keyword}</span> 검색 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='상대지수'), tooltip=['date:T', 'clicks:Q']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

            # (2) 하단 비중 분석 (기기/성별/연령)
            st.write("---")
            subcol1, subcol2, subcol3 = st.columns(3)
            
            with subcol1:
                st.caption("💻 기기별 비중")
                df = main_data.get('device_ratio')
                if df is not None:
                    c = alt.Chart(df).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("device:N", scale=alt.Scale(range=['#00c853', '#ff9800'])), tooltip=['device', 'value']
                    ).properties(height=180)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol2:
                st.caption("👫 성별 비중")
                df = main_data.get('gender_ratio')
                if df is not None:
                    c = alt.Chart(df).mark_arc(innerRadius=45).encode(
                        theta="value:Q", color=alt.Color("gender:N", scale=alt.Scale(range=['#448aff', '#ff5252'])), tooltip=['gender', 'value']
                    ).properties(height=180)
                    st.altair_chart(c, use_container_width=True)
            
            with subcol3:
                st.caption("🎂 연령별 비중")
                df = main_data.get('age_ratio')
                if df is not None:
                    c = alt.Chart(df).mark_bar(color='#448aff').encode(
                        x=alt.X('age:N', title=None, axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('value:Q', axis=None), tooltip=['age', 'value']
                    ).properties(height=180)
                    st.altair_chart(c, use_container_width=True)

        # --- 우측 컬럼 (연관어 및 카테고리 랭킹) ---
        with col2:
            # (1) 연관 검색어 (수정: 항상 표시되도록 컨테이너 관리)
            st.markdown(f"#### 🔍 {main_keyword} 연관 검색어")
            queries = main_data.get('top_queries', [])
            if queries:
                html_rel = "<div style='background-color: #f1f8e9; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333; margin-bottom: 20px;'>"
                for i, q in enumerate(queries):
                    html_rel += f"<div style='margin-bottom: 8px; font-size: 14px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html_rel + "</div>", unsafe_allow_html=True)
            else:
                st.caption("불러오는 중...")

            st.divider()

            # (2) 카테고리 설정 및 랭킹
            st.markdown("#### 📂 카테고리 인기 검색어")
            category = st.selectbox("카테고리 선택", categories, key=f"sb_{tab_name}", label_visibility="collapsed")
            
            ranking = main_data.get('category_ranking', [])
            if ranking:
                st.write("")
                st.markdown(f"#### 🏆 {category} 인기순")
                html_rank = f"<div style='background-color: #f9f9fc; padding: 15px; border-radius: 10px; height: 350px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(ranking):
                    html_rank += f"<div style='margin-bottom: 12px; font-size: 14px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html_rank + "</div>", unsafe_allow_html=True)