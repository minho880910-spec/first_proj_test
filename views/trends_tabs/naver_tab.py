import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, categories: list, prompt_input: str, global_main_keyword: str):
    # 1. 상단 레이아웃 분할
    col1, col2 = st.columns([2.5, 1])
    
    with col2:
        # 연관 검색어 등을 담을 컨테이너
        keyword_related_container = st.container()
        st.divider()
        
        # 카테고리 선택 UI
        st.markdown("#### 📂 카테고리 랭킹", unsafe_allow_html=True)
        cat_col, _ = st.columns([1, 0.1])
        with cat_col:
            auto_cat = st.session_state.get(f"trend_category_{tab_name}", categories[0])
            try:
                default_idx = categories.index(auto_cat)
            except ValueError:
                default_idx = 0
                
            category = st.selectbox(
                "카테고리 선택", 
                categories, 
                index=default_idx, 
                key=f"sb_{tab_name}", 
                label_visibility="collapsed"
            )
            st.caption("네이버 쇼핑인사이트 기준")

    # 2. 분석 키워드 결정
    main_keyword = global_main_keyword if prompt_input else category
    
    # 3. 데이터 가져오기
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword, category)

    # 4. 데이터 렌더링 시작
    if main_data and isinstance(main_data, dict):
        with col1:
            # (1) 시계열 트렌드 차트
            st.markdown(f"### <span style='color:#00c853'>{main_keyword}</span> 쇼핑 트렌드 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 클릭 추이</span>", unsafe_allow_html=True)
            
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#00c853', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0)),
                    y=alt.Y('clicks:Q', title='클릭 지수', axis=alt.Axis(grid=True)),
                    tooltip=[alt.Tooltip('date:T', title='날짜'), alt.Tooltip('clicks:Q', title='지수')]
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("시계열 데이터를 불러올 수 없습니다.")

            # (2) 비중 분석 섹션 (제목과 구분선 제거, 차트 레이아웃은 유지)
            st.write("") # 시계열 차트와의 약간의 간격 확보
            subcol1, subcol2, subcol3 = st.columns(3)
            
            # 기기별 비중
            with subcol1:
                st.caption("💻 기기별 (PC/모바일)")
                df_device = main_data.get('device_ratio')
                if df_device is not None:
                    device_chart = alt.Chart(df_device).mark_arc(innerRadius=45).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="device", type="nominal", scale=alt.Scale(range=['#00c853', '#ff9800']), legend=alt.Legend(orient="bottom")),
                        tooltip=['device', 'value']
                    ).properties(height=220)
                    st.altair_chart(device_chart, use_container_width=True)
            
            # 성별 비중
            with subcol2:
                st.caption("👫 성별 비중")
                df_gender = main_data.get('gender_ratio')
                if df_gender is not None:
                    gender_chart = alt.Chart(df_gender).mark_arc(innerRadius=45).encode(
                        theta=alt.Theta(field="value", type="quantitative"),
                        color=alt.Color(field="gender", type="nominal", scale=alt.Scale(range=['#448aff', '#ff5252']), legend=alt.Legend(orient="bottom")),
                        tooltip=['gender', 'value']
                    ).properties(height=220)
                    st.altair_chart(gender_chart, use_container_width=True)
            
            # 연령별 비중
            with subcol3:
                st.caption("🎂 연령별 비중")
                df_age = main_data.get('age_ratio')
                if df_age is not None:
                    age_chart = alt.Chart(df_age).mark_bar(color='#448aff', cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                        x=alt.X('age:N', title='', axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('value:Q', title='', axis=None),
                        tooltip=['age', 'value']
                    ).properties(height=220)
                    st.altair_chart(age_chart, use_container_width=True)

        # 5. 오른쪽 사이드바 콘텐츠
        with keyword_related_container:
            st.markdown(f"#### 🔍 {main_keyword} 연관 검색어", unsafe_allow_html=True)
            main_queries = main_data.get('top_queries', [])
            
            if main_queries:
                html_bg = "background-color: #f1f8e9; border: 1px solid #c8e6c9;"
                html_content = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(main_queries):
                    html_content += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong style='color: #2e7d32; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)

        with col2:
            st.write("") 
            queries = cat_data.get('top_queries', []) if cat_data else []
            if queries:
                html_bg2 = "background-color: #f9f9fc; border: 1px solid #e0e0e0;"
                html_content2 = f"<div style='{html_bg2} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #333;'>"
                for i, q in enumerate(queries):
                    html_content2 += f"<div style='margin-bottom: 10px; font-size: 14px;'><strong style='color: #0056b3; width: 25px; display: inline-block;'>{i+1}</strong> {q}</div>"
                html_content2 += "</div>"
                st.markdown(html_content2, unsafe_allow_html=True)