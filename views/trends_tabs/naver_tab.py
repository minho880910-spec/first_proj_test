import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    col1, col2 = st.columns([2.5, 1])
    
    with col2:
        # [수정] 연관검색어를 담을 컨테이너를 상단에 배치
        keyword_related_container = st.container()
        st.divider()
        st.markdown("#### 📂 카테고리 선택")
        auto_cat = st.session_state.get(f"trend_category_{tab_name}")
        default_idx = categories.index(auto_cat) if auto_cat in categories else 0
        category = st.selectbox("카테고리 선택", categories, index=default_idx, key=f"sb_{tab_name}", label_visibility="collapsed")

    main_keyword = global_main_keyword if prompt_input else category
    main_data, _ = fetch_trend_data(tab_name, main_keyword, category)

    if main_data:
        with col1:
            # 1. 검색 추이 그래프 (매핑 실패와 무관하게 항상 출력)
            st.markdown(f"### <span style='color:#00c853'>{main_keyword}</span> 검색 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='상대지수'), tooltip=['date:T', 'clicks:Q']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

            # 2. 매핑 실패 메시지 및 통계 처리
            if main_data.get('error') == 'mapping_failed':
                st.warning(f"⚠️ '{category}' 카테고리는 쇼핑 통계 매핑을 지원하지 않아 하단 지표가 표시되지 않습니다.")
            else:
                st.write("") 
                subcol1, subcol2, subcol3 = st.columns(3)
                with subcol1:
                    st.caption("💻 기기별")
                    df_dev = main_data.get('device_ratio')
                    if df_dev is not None:
                        c = alt.Chart(df_dev).mark_arc(innerRadius=45).encode(
                            theta="value:Q", color="device:N", tooltip=['device', 'value']
                        ).properties(height=200)
                        st.altair_chart(c, use_container_width=True)
                with subcol2:
                    st.caption("👫 성별")
                    df_gen = main_data.get('gender_ratio')
                    if df_gen is not None:
                        c = alt.Chart(df_gen).mark_arc(innerRadius=45).encode(
                            theta="value:Q", color="gender:N", tooltip=['gender', 'value']
                        ).properties(height=200)
                        st.altair_chart(c, use_container_width=True)
                with subcol3:
                    st.caption("🎂 연령별")
                    df_age = main_data.get('age_ratio')
                    if df_age is not None:
                        c = alt.Chart(df_age).mark_bar(color='#448aff').encode(
                            x=alt.X('age:N', title=None, axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('value:Q', axis=None), tooltip=['age', 'value']
                        ).properties(height=200)
                        st.altair_chart(c, use_container_width=True)

        # 3. 우측 실시간 정보 (연관어 상단 배치)
        with keyword_related_container:
            st.markdown(f"#### 🔍 {main_keyword} 연관어")
            queries = main_data.get('top_queries', [])
            if queries:
                html = "<div style='background-color: #f1f8e9; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(queries):
                    html += f"<div style='margin-bottom: 8px; font-size: 14px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html + "</div>", unsafe_allow_html=True)

        with col2:
            st.write("") 
            ranking = main_data.get('category_ranking', [])
            if ranking:
                st.markdown(f"#### 🏆 {category} 인기순")
                html = "<div style='background-color: #f9f9fc; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(ranking):
                    html += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html + "</div>", unsafe_allow_html=True)
            elif category != "해당 카테고리 없음":
                st.caption(f"'{category}' 랭킹 정보가 없습니다.")