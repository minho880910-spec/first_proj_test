import streamlit as st
import altair as alt
from modules.trend_state_manager import fetch_trend_data
import base64
import os

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    # 레이아웃 정의
    col1, col2 = st.columns([2.5, 1])
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        
    with bot_col1:
        st.markdown("#### 지역별 관심도 분석 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
        map_col, rank_col = st.columns([1, 1.2])
        with rank_col:
            st.markdown("#### 전국 랭킹 Top 5", unsafe_allow_html=True)
            rankings_container = st.container()
        with map_col:
            map_container = st.container()
            
    with bot_col2:
        st.markdown("#### ❓ 함께 많이 찾는 질문 (FAQ) ❓")
        faqs_container = st.container()

    # 데이터 가져오기 (fetch_trend_data 내부에서 'top_queries'를 반환해야 함)
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        # 1. 트렌드 추이 그래프 (왼쪽 상단)
        with col1:
            st.markdown(f"### <span style='color:#448aff'>{main_keyword}</span> 트렌드 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None:
                chart = alt.Chart(df_time).mark_line(color='#00E5FF', strokeWidth=2).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # 2. 급상승 관련 검색어 (오른쪽 상단) - 이 부분이 복구되었습니다.
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#448aff'>{main_keyword}</span> 급상승 관련어", unsafe_allow_html=True)
            main_queries = main_data.get('top_queries', [])
            
            if main_queries:
                html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
                html_content = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>"
                for i, q in enumerate(main_queries[:7]):
                    html_content += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex;'><strong style='color: #448aff; width: 25px;'>{i+1}</strong> <span>{q}</span></div></div>"
                html_content += "</div>"
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("연관 검색어 데이터가 없습니다.")

        # 3. 지도 로딩
        # --- 지도 이미지 로딩 로직 (강화형) ---
        with map_container:
            try:
                # 1. 절대 경로 추출
                # __file__은 views/google_tab.py를 가리킴
                current_file_path = os.path.abspath(__file__)
                # views 폴더
                views_dir = os.path.dirname(current_file_path)
                # 프로젝트 최상단(Root)
                project_root = os.path.dirname(views_dir)
                
                # 2. 최종 경로 생성
                map_path = os.path.join(project_root, "assets", "korea_map.png")

                # 3. 파일 존재 여부 확인 및 로딩
                if os.path.exists(map_path):
                    with open(map_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                        st.markdown(
                            f"""
                            <div style="text-align: center;">
                                <img src="data:image/png;base64,{encoded_string}" 
                                     style="width: 100%; max-width: 400px; border-radius: 10px; filter: drop-shadow(0px 4px 10px rgba(0,0,0,0.3));">
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                else:
                    # 파일이 없을 경우 실제 경로를 화면에 출력해서 디버깅 도와줌
                    st.error(f"⚠️ 파일을 찾을 수 없습니다.")
                    st.caption(f"찾으려는 경로: {map_path}")
                    
            except Exception as e:
                st.error(f"❌ 이미지 로딩 중 오류 발생: {e}")

        # 4. 지역 랭킹 및 FAQ (하단)
        with rankings_container:
            pass
        
        with faqs_container:
            pass