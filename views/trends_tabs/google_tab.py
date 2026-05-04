import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    # 메인 키워드 설정
    main_keyword = global_main_keyword
    
    # 레이아웃 분할: 왼쪽(큰 화면용), 오른쪽(정보 요약용)
    col1, col2 = st.columns([2.5, 1])
    
    # 통합 매니저로부터 데이터 호출
    main_data, _ = fetch_trend_data(tab_name, main_keyword)

    if main_data:
        # --- [왼쪽 라인] 시각화 영역 (관심도 그래프 & 지역 랭킹) ---
        with col1:
            # 1. 상단: 구글/네이버 관심도 변화 그래프
            st.markdown(f"### <span style='color:#4285F4'>{main_keyword}</span> 관심도 변화 <span style='font-size: 0.8rem; color: gray; font-weight: normal; margin-left: 10px;'>최근 1달</span>", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            
            if isinstance(df_time, pd.DataFrame) and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#4285F4', strokeWidth=3).encode(
                    x=alt.X('date:T', title='날짜'),
                    y=alt.Y('clicks:Q', title='관심도 수치'),
                    tooltip=['date', 'clicks']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("시계열 데이터를 분석 중입니다.")

            st.write("") # 간격 조절용
            st.write("---") # 구분선

            # 2. 하단: 전국 지역별 관심도 랭킹 (AI 분석 데이터)
            st.markdown(f"#### 📍 {main_keyword} 전국 랭킹 Top 5")
            df_region = main_data.get('region_ranking')
            
            if isinstance(df_region, pd.DataFrame) and not df_region.empty:
                region_chart = alt.Chart(df_region.head(5)).mark_bar(color='#FBBC05').encode(
                    x=alt.X('score:Q', title='관심도 점수'),
                    y=alt.Y('region:N', sort='-x', title='지역명'),
                    tooltip=['region', 'score']
                ).properties(height=300) # 높이를 조금 더 키워 가독성을 높였습니다.
                st.altair_chart(region_chart, use_container_width=True)
            else:
                st.info("전국 지역별 트렌드 수치를 계산 중입니다.")

        # --- [오른쪽 라인] 정보 영역 (연관 키워드 & FAQ) ---
        with col2:
            # 1. 상단: 연관 검색어 리스트
            st.markdown(f"#### 🔍 {main_keyword} 연관 키워드")
            top_queries = main_data.get('top_queries', [])
            if top_queries:
                # 박스 형태의 디자인 적용 (가독성 증대)
                html_rel = "<div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; margin-bottom: 20px; color: #333;'>"
                for i, q in enumerate(top_queries[:10]):
                    html_rel += f"<div style='margin-bottom: 8px;'><strong>{i+1}.</strong> {q}</div>"
                st.markdown(html_rel + "</div>", unsafe_allow_html=True)
            else:
                st.caption("연관된 키워드가 없습니다.")

            st.write("") # 간격 조절용
            
            # 2. 하단: 함께 많이 찾는 질문 (FAQ)
            st.markdown("#### ❓ FAQ ❓")
            st.caption("관련 질문 리스트")
            faqs = main_data.get('faqs', [])
            if faqs:
                # 배경색을 살짝 넣어 연관 키워드 영역과 구분
                html_faq = "<div style='background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px dashed #dee2e6; color: #444;'>"
                for i, faq in enumerate(faqs):
                    html_faq += f"<div style='margin-bottom: 12px; font-size: 14px;'><strong>Q{i+1}.</strong> {faq}</div>"
                st.markdown(html_faq + "</div>", unsafe_allow_html=True)
            else:
                st.info("관련 질문 데이터를 생성 중입니다.")

    else:
        st.warning("데이터를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.")