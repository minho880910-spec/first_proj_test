import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    # 데이터 가져오기
    main_data, _ = fetch_trend_data(tab_name, main_keyword)

    if not main_data or not isinstance(main_data, dict):
        st.warning("데이터를 불러올 수 없습니다.")
        return

    # 데이터 위치 유연하게 탐색
    x_ai = main_data.get('x_sentiment') or main_data
    
    # ---------------------------------------------------------
    # 화면을 좌(Main 분석) : 우(Side 정보) = 2 : 1 비율로 분할
    # ---------------------------------------------------------
    left_col, right_col = st.columns([2, 1], gap="large")

    # --- [왼쪽 섹션: 분석 중심] ---
    with left_col:
        # 1. 트렌드 추이 그래프
        st.markdown(f"### <span style='color:#4fc3f7'>{main_keyword}</span> 트렌드 추이", unsafe_allow_html=True)
        df_time = main_data.get('time_series')
        if isinstance(df_time, pd.DataFrame) and not df_time.empty:
            chart = alt.Chart(df_time).mark_area(
                line={'color': '#00E5FF'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#00E5FF', offset=0), 
                           alt.GradientStop(color='transparent', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('date:T', title=''),
                y=alt.Y('clicks:Q', title='')
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True) # 간격 조절

        # 2. 정보 공유 및 감성 분석 지도
        st.markdown("#### 정보 공유 및 감성 분석 지도", unsafe_allow_html=True)
        
        s_stats = x_ai.get('sentiment_stats', [60, 25, 15])
        e_words = x_ai.get('emotional_words')
        if not e_words:
            e_words = [f"{main_keyword}리뷰", "성능", "추천", "이슈", "꿀팁", "디자인", "가격", "반응", "특징", "인기"]
        s_score = x_ai.get('satisfaction_score', 80)
        
        # 내부를 3단 분할
        sc1, sc2, sc3 = st.columns([1, 1.8, 1])
        
        with sc1:
            st.markdown("<div style='text-align: center; font-size: 13px; color: #a9b1d6; font-weight: bold; margin-bottom: 10px;'>게시물 성향</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='position: relative; width: 100px; height: 100px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% {s_stats[0]}%, #FF00FF {s_stats[0]}% 85%, #448aff 85% 100%); display: flex; justify-content: center; align-items: center;'>
                <div style='width: 70px; height: 70px; background-color: #1a1b26; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #00E5FF; font-size: 15px;'>{s_stats[0]}%</div>
            </div>""", unsafe_allow_html=True)
        
        with sc2:
            st.markdown("<div style='text-align: center; font-size: 13px; color: #a9b1d6; font-weight: bold; margin-bottom: 10px;'>감성 클러스터</div>", unsafe_allow_html=True)
            bubble_html = "<div style='display: flex; flex-wrap: wrap; justify-content: center; align-content: center; gap: 6px; min-height: 100px;'>"
            colors = ["#FF00FF", "#00E5FF", "#448aff", "#a9b1d6"]
            for i, word in enumerate(e_words[:10]):
                color = colors[i % len(colors)]
                bubble_html += f"<div style='color: {color} !important; font-size: 12px; font-weight: bold; background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 15px; border: 1px solid {color}; white-space: nowrap;'>{word}</div>"
            st.markdown(bubble_html + "</div>", unsafe_allow_html=True)
        
        with sc3:
            st.markdown("<div style='text-align: center; font-size: 13px; color: #a9b1d6; font-weight: bold; margin-bottom: 10px;'>만족도</div>", unsafe_allow_html=True)
            angle = (s_score * 1.8) - 90
            st.markdown(f"""
            <div style='position: relative; width: 80px; height: 40px; margin: 0 auto; background-color: #292e42; border-top-left-radius: 80px; border-top-right-radius: 80px; overflow: hidden;'>
                <div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: conic-gradient(from 270deg, #FF00FF, #00E5FF);'></div>
                <div style='position: absolute; bottom: 0; left: 50%; width: 50px; height: 25px; background-color: #1a1b26; border-top-left-radius: 50px; border-top-right-radius: 50px; transform: translateX(-50%);'></div>
                <div style='position: absolute; bottom: 0; left: 50%; width: 3px; height: 35px; background-color: #ffffff; transform-origin: bottom center; transform: translateX(-50%) rotate({angle}deg);'></div>
            </div>
            <div style='text-align: center; color: #00E5FF; font-weight: bold; font-size: 16px; margin-top: 8px;'>{s_score}점</div>""", unsafe_allow_html=True)

    # --- [오른쪽 섹션: 리스트 중심] ---
    with right_col:
        # 1. 실시간 키워드
        st.markdown(f"#### 실시간 키워드", unsafe_allow_html=True)
        main_queries = main_data.get('top_queries', [])
        mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700"]
        if main_queries:
            html_items = ""
            for i, q in enumerate(main_queries[:7]):
                count = mock_counts[i % len(mock_counts)]
                html_items += f"""
                <div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 13px; color: #a9b1d6;'>
                    <div><strong style='color: #4fc3f7; width: 20px; display:inline-block;'>{i+1}</strong> {q}</div> 
                    <span style='color: #4fc3f7;'>{count}</span>
                </div>"""
            st.markdown(f"<div style='background-color: #1a1b26; border: 1px solid #292e42; padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto;'>{html_items}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # 2. 베스트 꿀팁 / 연관 노하우
        st.markdown("#### 베스트 꿀팁 💡", unsafe_allow_html=True)
        tips = x_ai.get('tips') or x_ai.get('user_tips') or x_ai.get('knowhow')
        
        if tips and isinstance(tips, list) and len(tips) > 0:
            tips_html = ""
            for i, t in enumerate(tips[:3]):
                t_high = t.get('highlight', '노하우')
                t_desc = t.get('desc', '상세 정보 수집 중')
                tips_html += f"""
                <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 10px; padding: 12px; margin-bottom: 10px;'>
                    <div style='color: #ffffff; font-size: 13px; font-weight: bold; margin-bottom: 4px;'>{t_high}</div>
                    <div style='color: #888888; font-size: 11px; line-height: 1.4;'>{t_desc}</div>
                </div>"""
            st.markdown(tips_html, unsafe_allow_html=True)
        else:
            st.caption("새로운 노하우를 분석 중입니다.")