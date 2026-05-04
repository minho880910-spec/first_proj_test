import streamlit as st
import altair as alt
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    col1, col2 = st.columns([2.5, 1])
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        
    with bot_col1:
        st.markdown(f"#### 정보 공유 및 감성 분석 지도 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
        sentiment_map_container = st.container()
        
    with bot_col2:
        st.markdown("#### 베스트 꿀팁 / 연관 노하우 💡 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
        tips_container = st.container()

    # 데이터 가져오기
    main_data, _ = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        x_ai = main_data.get('x_sentiment', {})

        # --- [상단 왼쪽] 트렌드 추이 ---
        with col1:
            st.markdown(f"### <span style='color:#4fc3f7'>{main_keyword}</span> 트렌드 추이 <span style='font-size: 0.8rem; color: gray; font-weight: normal; margin-left: 10px;'>최근 1주일</span>", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_area(
                    line={'color': '#00E5FF'},
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[alt.GradientStop(color='#00E5FF', offset=0),
                               alt.GradientStop(color='rgba(0, 229, 255, 0)', offset=1)],
                        x1=1, x2=1, y1=1, y2=0
                    )
                ).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # --- [상단 오른쪽] 실시간 꿀팁 & 검색어 ---
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#a9b1d6'>{main_keyword}</span> 실시간 키워드 Top 7")
            main_queries = main_data.get('top_queries', [])
            mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
            if main_queries:
                html_items = ""
                for i, q in enumerate(main_queries[:7]):
                    html_items += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px;'><div><strong style='color: #4fc3f7; width: 25px; display:inline-block;'>{i+1}</strong> {q}</div> <span style='color: #4fc3f7;'>{mock_counts[i % len(mock_counts)]}</span></div>"
                st.markdown(f"<div style='background-color: #1a1b26; border: 1px solid #292e42; padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>{html_items}</div>", unsafe_allow_html=True)

        # --- [하단 왼쪽] 감성 분석 지도 (AI 데이터 반영) ---
        with sentiment_map_container:
            s_stats = x_ai.get('sentiment_stats', [60, 25, 10, 5])
            e_words = x_ai.get('emotional_words', ["정보", "리뷰", "꿀팁", "추천", "공유", "실시간", "인기"])
            s_score = x_ai.get('satisfaction_score', 80)
            c_ratio = x_ai.get('context_ratio', [40, 35, 25])

            sc1, sc2, sc3, sc4 = st.columns([1.2, 2, 1, 1])
            with sc1:
                st.markdown("<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 5px;'>게시물 성향</div>", unsafe_allow_html=True)
                donut_html = f"""
                <div style='position: relative; width: 100px; height: 100px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% {s_stats[0]}%, #FF00FF {s_stats[0]}% {s_stats[0]+s_stats[1]}%, #448aff {s_stats[0]+s_stats[1]}% {s_stats[0]+s_stats[1]+s_stats[2]}%, #888888 {s_stats[0]+s_stats[1]+s_stats[2]}% 100%); display: flex; justify-content: center; align-items: center;'>
                    <div style='width: 70px; height: 70px; background-color: #1a1b26; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #00E5FF; font-size: 14px;'>{s_stats[0]}%</div>
                </div>
                <div style='font-size: 10px; color: #a9b1d6; margin-top: 10px; line-height: 1.4;'>
                    <span style='color:#00E5FF'>●</span> 정보/노하우 ({s_stats[0]}%)<br><span style='color:#FF00FF'>●</span> 긍정 감성 ({s_stats[1]}%)
                </div>"""
                st.markdown(donut_html, unsafe_allow_html=True)
            
            with sc2:
                # AI가 생성한 감성 단어들로 워드클라우드 시뮬레이션
                st.markdown(f"<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 5px;'>감성 클러스터</div>", unsafe_allow_html=True)
                word_html = f"""
                <div style='position: relative; height: 150px; background-color: transparent;'>
                    <div style='position: absolute; top: 10%; left: 10%; color: #FF00FF; font-size: 13px;'>{e_words[0]}</div>
                    <div style='position: absolute; top: 20%; right: 10%; color: #00E5FF; font-size: 12px;'>{e_words[1]}</div>
                    <div style='position: absolute; top: 45%; left: 35%; color: #00E5FF; font-size: 18px; font-weight: bold;'>{e_words[2]}</div>
                    <div style='position: absolute; bottom: 20%; left: 5%; color: #448aff; font-size: 13px;'>{e_words[3]}</div>
                    <div style='position: absolute; bottom: 10%; right: 20%; color: #FF00FF; font-size: 14px;'>{e_words[4]}</div>
                </div>"""
                st.markdown(word_html, unsafe_allow_html=True)
            
            with sc3:
                # 만족도 게이지 바늘 각도 계산 (0~100점을 -90~90도로 변환)
                angle = (s_score * 1.8) - 90
                st.markdown("<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 5px;'>만족도</div>", unsafe_allow_html=True)
                gauge_html = f"""
                <div style='position: relative; width: 80px; height: 40px; margin: 0 auto; background-color: #292e42; border-top-left-radius: 80px; border-top-right-radius: 80px; overflow: hidden;'>
                    <div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: conic-gradient(from 270deg, #FF00FF, #00E5FF);'></div>
                    <div style='position: absolute; bottom: 0; left: 50%; width: 50px; height: 25px; background-color: #1a1b26; border-top-left-radius: 50px; border-top-right-radius: 50px; transform: translateX(-50%);'></div>
                    <div style='position: absolute; bottom: 0; left: 50%; width: 2px; height: 35px; background-color: #fff; transform-origin: bottom center; transform: translateX(-50%) rotate({angle}deg);'></div>
                </div>
                <div style='text-align: center; color: #00E5FF; font-weight: bold; font-size: 14px; margin-top: 5px;'>{s_score}점</div>"""
                st.markdown(gauge_html, unsafe_allow_html=True)
            
            with sc4:
                st.markdown("<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 5px;'>유입 맥락</div>", unsafe_allow_html=True)
                donut2_html = f"""
                <div style='position: relative; width: 80px; height: 80px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% {c_ratio[0]}%, #FF00FF {c_ratio[0]}% {c_ratio[0]+c_ratio[1]}%, #448aff {c_ratio[0]+c_ratio[1]}% 100%); display: flex; justify-content: center; align-items: center;'>
                    <div style='width: 50px; height: 50px; background-color: #1a1b26; border-radius: 50%;'></div>
                </div>"""
                st.markdown(donut2_html, unsafe_allow_html=True)

        # --- [하단 오른쪽] 베스트 꿀팁 (AI 데이터 반영) ---
        with tips_container:
            st.markdown("<div style='text-align: right; font-size: 11px; color: #888888; margin-bottom: 5px;'><span>🔖 실시간 유저 노하우</span></div>", unsafe_allow_html=True)
            tips = x_ai.get('tips', [])
            if tips:
                tips_html = ""
                for i, t in enumerate(tips):
                    tips_html += f"""
                    <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 12px; margin-bottom: 8px;'>
                        <div style='display: flex; align-items: flex-start;'>
                            <div style='color: #4fc3f7; font-size: 15px; font-weight: bold; width: 20px;'>{i+1}</div>
                            <div>
                                <div style='color: #a9b1d6; font-size: 13px; margin-bottom: 3px;'>{t['title']}</div>
                                <div style='color: #ffffff; font-size: 14px; font-weight: bold; margin-bottom: 3px;'>{t['highlight']}</div>
                                <div style='color: #888888; font-size: 11px;'>{t['desc']}</div>
                            </div>
                        </div>
                    </div>"""
                st.markdown(tips_html, unsafe_allow_html=True)