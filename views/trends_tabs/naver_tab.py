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
        
        # [수정] 검색어가 바뀔 때 카테고리 셀렉트박스 상태 초기화 로직
        auto_cat = st.session_state.get(f"trend_category_{tab_name}")
        
        # 세션에 기록된 마지막 검색어와 현재 검색어를 비교하여 카테고리 강제 변경
        last_keyword = st.session_state.get(f"last_keyword_{tab_name}", "")
        
        # 새로운 검색어가 입력된 경우, 위젯의 index를 강제로 auto_cat에 맞춤
        if global_main_keyword != last_keyword:
            st.session_state[f"last_keyword_{tab_name}"] = global_main_keyword
            # 새로운 검색어일 때 셀렉트박스 값 강제 업데이트
            if auto_cat in categories:
                st.session_state[f"sb_{tab_name}"] = auto_cat

        # 셀렉트박스 생성
        category = st.selectbox(
            "카테고리 선택", 
            categories, 
            key=f"sb_{tab_name}", 
            label_visibility="collapsed"
        )
        st.caption(f"현재 분석 대상: {category}")

    # 데이터 호출
    main_keyword = global_main_keyword if prompt_input else category
    main_data, _ = fetch_trend_data(tab_name, main_keyword, category)

    if main_data:
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

            # (2) 하단 비중 그래프
            if main_data.get('error') == 'mapping_failed':
                st.warning(f"⚠️ '{category}' 카테고리는 쇼핑 통계 매핑 정보가 부족합니다.")
            else:
                st.write("") 
                subcol1, subcol2, subcol3 = st.columns(3)
                with subcol1:
                    st.caption("💻 기기별 (PC/모바일)")
                    df_dev = main_data.get('device_ratio')
                    if df_dev is not None:
                        c = alt.Chart(df_dev).mark_arc(innerRadius=45).encode(
                            theta="value:Q", color=alt.Color("device:N", scale=alt.Scale(range=['#00c853', '#ff9800'])), tooltip=['device', 'value']
                        ).properties(height=200)
                        st.altair_chart(c, use_container_width=True)
                with subcol2:
                    st.caption("👫 성별 비중")
                    df_gen = main_data.get('gender_ratio')
                    if df_gen is not None:
                        c = alt.Chart(df_gen).mark_arc(innerRadius=45).encode(
                            theta="value:Q", color=alt.Color("gender:N", scale=alt.Scale(range=['#448aff', '#ff5252'])), tooltip=['gender', 'value']
                        ).properties(height=200)
                        st.altair_chart(c, use_container_width=True)
                with subcol3:
                    st.caption("🎂 연령별 비중")
                    df_age = main_data.get('age_ratio')
                    if df_age is not None:
                        c = alt.Chart(df_age).mark_bar(color='#448aff').encode(
                            x=alt.X('age:N', title=None, axis=alt.Axis(labelAngle=0)),
                            y=alt.Y('value:Q', axis=None), tooltip=['age', 'value']
                        ).properties(height=200)
                        st.altair_chart(c, use_container_width=True)

        # 3. 우측 실시간 정보 (연관어)
        with keyword_related_container:
            st.markdown(f"#### 🔍 {main_keyword} 연관어")
            queries = main_data.get('top_queries', [])
            if queries:
                html = "<div style='background-color: #f1f8e9; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(queries):
                    html += f"<div style='margin-bottom: 8px; font-size: 14px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html + "</div>", unsafe_allow_html=True)

        # 4. 우측 하단 카테고리 랭킹 (인기 검색어 순위)
        with col2:
            st.write("") 
            ranking = main_data.get('category_ranking', [])
            if ranking:
                st.markdown(f"#### 🏆 {category} 인기순")
                html_rank = "<div style='background-color: #f9f9fc; padding: 15px; border-radius: 10px; height: 230px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(ranking):
                    html_rank += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                st.markdown(html_rank + "</div>", unsafe_allow_html=True)
            elif category != "해당 카테고리 없음":
                # 데이터가 안 나올 때 디버깅용 메시지
                st.info(f"'{category}' 랭킹 정보를 호출 중입니다.")