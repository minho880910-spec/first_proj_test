import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    col1, col2 = st.columns([2.5, 1])
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
    with bot_col1:
        st.markdown("#### 정보 공유 및 감성 분석 지도", unsafe_allow_html=True)
        sentiment_map_container = st.container()
    with bot_col2:
        st.markdown("#### 베스트 꿀팁 / 연관 노하우 💡", unsafe_allow_html=True)
        tips_container = st.container()

    main_data, _ = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        x_ai = main_data.get('x_sentiment')
        if not x_ai or not isinstance(x_ai, dict):
            x_ai = main_data
        
        # --- [상단 오른쪽] 실시간 키워드 Top 7 복구 ---
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#a9b1d6'>{main_keyword}</span> 실시간 키워드 Top 7", unsafe_allow_html=True)
            main_queries = main_data.get('top_queries', [])
            mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700"]
            
            if main_queries:
                html_items = ""
                for i, q in enumerate(main_queries[:7]):
                    count = mock_counts[i % len(mock_counts)]
                    html_items += f"""
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px;'>
                        <div><strong style='color: #4fc3f7; width: 25px; display:inline-block;'>{i+1}</strong> {q}</div> 
                        <span style='color: #4fc3f7;'>{count}</span>
                    </div>"""
                st.markdown(f"<div style='background-color: #1a1b26; border: 1px solid #292e42; padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>{html_items}</div>", unsafe_allow_html=True)
            else:
                st.info("실시간 키워드 데이터를 분석 중입니다.")

        # --- [상단 왼쪽] 트렌드 추이 ---
        with col1:
            st.markdown(f"### <span style='color:#4fc3f7'>{main_keyword}</span> 트렌드 추이", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if isinstance(df_time, pd.DataFrame) and not df_time.empty:
                chart = alt.Chart(df_time).mark_area(line={'color': '#00E5FF'}).encode(
                    x=alt.X('date:T', title=''),
                    y=alt.Y('clicks:Q', title='')
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # --- [하단 왼쪽] 감성 분석 지도 ---
        with sentiment_map_container:
            e_words = x_ai.get('emotional_words', [])
            if not e_words or len(e_words) < 3:
                e_words = [f"{main_keyword}리뷰", "성능", "추천", "이슈", "꿀팁", "디자인", "가격", "반응", "특징", "인기"]
            
            s_stats = x_ai.get('sentiment_stats', [50, 30, 15, 5])
            s_score = x_ai.get('satisfaction_score', 80)
            
            sc1, sc2, sc3 = st.columns([1, 2.5, 1])
            with sc1:
                st.markdown(f"""<div style='position: relative; width: 100px; height: 100px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% {s_stats[0]}%, #FF00FF {s_stats[0]}% 80%, #448aff 80% 100%); display: flex; justify-content: center; align-items: center;'><div style='width: 70px; height: 70px; background-color: #1a1b26; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #00E5FF; font-size: 14px;'>{s_stats[0]}%</div></div>""", unsafe_allow_html=True)
            
            with sc2:
                bubble_html = "<div style='display: flex; flex-wrap: wrap; justify-content: center; align-content: center; gap: 8px; height: 160px; padding: 10px;'>"
                colors = ["#FF00FF", "#00E5FF", "#448aff", "#a9b1d6"]
                for i, word in enumerate(e_words[:10]):
                    color = colors[i % len(colors)]
                    bubble_html += f"<div style='color: {color}; font-size: 14px; font-weight: bold; background: rgba(255,255,255,0.08); padding: 5px 12px; border-radius: 20px; border: 1px solid {color}44; white-space: nowrap;'>{word}</div>"
                st.markdown(bubble_html + "</div>", unsafe_allow_html=True)

            with sc3:
                angle = (s_score * 1.8) - 90
                st.markdown(f"<div style='text-align: center; color: #00E5FF; font-weight: bold; font-size: 14px; margin-top: 15px;'>{s_score}점</div>", unsafe_allow_html=True)

        # --- [하단 오른쪽] 베스트 꿀팁 ---
        with tips_container:
            st.markdown("<div style='text-align: right; font-size: 11px; color: #888888;'><span>🔖 실시간 유저 노하우</span></div>", unsafe_allow_html=True)
            tips = x_ai.get('tips') or x_ai.get('user_tips') or x_ai.get('knowhow') or main_data.get('tips')
            
            if tips and isinstance(tips, list) and len(tips) > 0:
                tips_html = ""
                for i, t in enumerate(tips[:3]):
                    t_title = t.get('title', '실시간 정보')
                    t_high = t.get('highlight', t.get('title', '노하우'))
                    t_desc = t.get('desc', '상세 내용을 가져오지 못했습니다.')
                    
                    tips_html += f"""
                    <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 12px; margin-bottom: 8px;'>
                        <div style='color: #ffffff; font-size: 14px; font-weight: bold;'>{t_high}</div>
                        <div style='color: #888888; font-size: 11px;'>{t_desc}</div>
                    </div>"""
                st.markdown(tips_html, unsafe_allow_html=True)