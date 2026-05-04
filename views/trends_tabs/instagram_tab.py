import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    col1, col2 = st.columns([2.5, 1])
    
    # 카테고리 동기화 로직
    auto_cat = st.session_state.get(f"trend_category_{tab_name}")
    last_keyword = st.session_state.get(f"last_keyword_{tab_name}", "")
    if global_main_keyword != last_keyword:
        st.session_state[f"last_keyword_{tab_name}"] = global_main_keyword
        if auto_cat in categories:
            st.session_state[f"sb_{tab_name}"] = auto_cat

    # 데이터 호출
    temp_category = st.session_state.get(f"sb_{tab_name}", categories[0])
    main_keyword = global_main_keyword if prompt_input else temp_category
    main_data, _ = fetch_trend_data(tab_name, main_keyword, temp_category)

    if main_data and isinstance(main_data, dict):
        with col1:
            # 1. 언급량 차트
            st.markdown(f"### <span style='color:#00E5FF'>{main_keyword}</span> 언급량 "
                        f"<span style='font-size: 0.8rem; color: gray; font-weight: normal; margin-left: 10px;'>최근 1달</span>", 
                        unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if isinstance(df_time, pd.DataFrame) and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00E5FF', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='언급지수'), 
                    tooltip=['date:T', 'clicks:Q']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

            # 2. 비중 분석 (미디어/성별/연령)
            st.write("---")
            subcol1, subcol2, subcol3 = st.columns(3)
            
            with subcol1:
                st.caption("📱 미디어 유형")
                df_media = main_data.get('media_ratio')
                if isinstance(df_media, pd.DataFrame) and not df_media.empty:
                    # 데이터프레임의 컬럼명인 'type'과 'value'를 명확히 지정
                    chart = alt.Chart(df_media).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="type", type="nominal", legend=alt.Legend(orient="bottom", title=None)),
                        tooltip=['type', 'value']
                    ).properties(height=220)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("데이터 분석 중")

            with subcol2:
                st.caption("👫 성별 비중")
                df_gen = main_data.get('gender_ratio')
                if isinstance(df_gen, pd.DataFrame) and not df_gen.empty:
                    c = alt.Chart(df_gen).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="gender", type="nominal", 
                                        scale=alt.Scale(range=['#FF00FF', '#448aff']),
                                        legend=alt.Legend(orient="bottom", title=None)),
                        tooltip=['gender', 'value']
                    ).properties(height=220)
                    st.altair_chart(c, use_container_width=True)

            with subcol3:
                st.caption("🎂 연령별 비중")
                df_age = main_data.get('age_ratio')
                if isinstance(df_age, pd.DataFrame) and not df_age.empty:
                    c = alt.Chart(df_age).mark_bar(color='#00E5FF').encode(
                        x=alt.X('age:N', title='', axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('value:Q', axis=None), 
                        tooltip=['age', 'value']
                    ).properties(height=220)
                    st.altair_chart(c, use_container_width=True)

        with col2:
            # 3. 연관 해시태그
            st.markdown(f"#### 🔍 {main_keyword} 연관 해시태그")
            main_queries = main_data.get('top_queries', [])
            mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
            if main_queries:
                html_rel = "<div style='background-color: #1a1b26; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #a9b1d6;'>"
                for i, q in enumerate(main_queries):
                    display_q = f"#{q.replace(' ', '')}"
                    count = mock_counts[i % len(mock_counts)]
                    html_rel += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px;'><div style='display:flex;'><strong style='color: #00E5FF; width: 25px;'>{i+1}</strong> <span>{display_q}</span></div> <span style='color:#888;'>{count}</span></div>"
                st.markdown(html_rel + "</div>", unsafe_allow_html=True)

            st.divider()

            # 4. 카테고리 인기 해시태그
            st.markdown("#### 카테고리별 인기 해시태그")
            category = st.selectbox("카테고리 선택", categories, key=f"sb_{tab_name}", label_visibility="collapsed")
            st.caption("최근 1주일 고정 데이터")

            ranking = main_data.get('category_ranking', [])
            if ranking:
                html_rank = f"<div style='background-color: #1a1b26; padding: 15px; border-radius: 10px; height: 400px; overflow-y: auto; color: #a9b1d6;'>"
                for i, q in enumerate(ranking):
                    display_q = f"#{q.replace(' ', '')}"
                    html_rank += f"<div style='margin-bottom: 12px; font-size: 14px;'><strong style='color: #00E5FF; width: 25px; display: inline-block;'>{i+1}</strong> {display_q}</div>"
                st.markdown(html_rank + "</div>", unsafe_allow_html=True)