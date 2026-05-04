import streamlit as st
import altair as alt
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    col1, col2 = st.columns([2.5, 1])
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    # 데이터 가져오기
    main_data, _ = fetch_trend_data(tab_name, main_keyword)

    if main_data:
        # --- [상단 왼쪽] 트렌드 추이 ---
        with col1:
            st.markdown(f"### <span style='color:#4285F4'>{main_keyword}</span> 관심도 변화 <span style='font-size: 0.8rem; color: gray; font-weight: normal; margin-left: 10px;'>최근 1달</span>", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#4285F4', strokeWidth=3).encode(
                    x=alt.X('date:T', title=''),
                    y=alt.Y('clicks:Q', title='')
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # --- [상단 오른쪽] 연관 검색어 ---
        with col2:
            st.markdown(f"#### 🔍 {main_keyword} 연관 키워드")
            top_queries = main_data.get('top_queries', [])
            if top_queries:
                for i, q in enumerate(top_queries[:10]):
                    st.write(f"{i+1}. {q}")

        # --- [하단 왼쪽] 전국 랭킹 Top 5 (수정 지점) ---
        with bot_col1:
            st.markdown(f"#### 📍 {main_keyword} 전국 랭킹 Top 5")
            # 변수명을 'region_ranking'으로 정확히 매칭
            df_region = main_data.get('region_ranking') 
            if df_region is not None and not df_region.empty:
                region_chart = alt.Chart(df_region.head(5)).mark_bar(color='#FBBC05').encode(
                    x=alt.X('score:Q', title='관심도 점수'),
                    y=alt.Y('region:N', sort='-x', title='')
                ).properties(height=250)
                st.altair_chart(region_chart, use_container_width=True)
            else:
                st.info("지역별 데이터를 분석 중입니다.")

        # --- [하단 오른쪽] FAQ (수정 지점) ---
        with bot_col2:
            st.markdown("#### ❓ 함께 많이 찾는 질문 (FAQ) ❓")
            # 변수명을 'faqs'로 정확히 매칭
            faqs = main_data.get('faqs', [])
            if faqs:
                for faq in faqs:
                    with st.expander(faq):
                        st.write("관련 트렌드에 기반한 실시간 답변을 준비 중입니다.")
            else:
                st.info("질문 데이터를 생성 중입니다.")