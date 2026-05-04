import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    main_keyword = global_main_keyword
    
    # 레이아웃 설정
    col1, col2 = st.columns([2.5, 1])
    bot_col1, bot_col2 = st.columns([2.5, 1])
    
    with col2:
        keyword_related_container = st.container()
        
    with bot_col1:
        st.markdown("#### 정보 공유 및 감성 분석 지도 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
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
            if isinstance(df_time, pd.DataFrame) and not df_time.empty:
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
            else:
                st.info("시계열 데이터를 불러오는 중입니다.")

        # --- [상단 오른쪽] 실시간 키워드 ---
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
                st.caption("연관 데이터를 수집 중입니다.")

        # --- [하단 왼쪽] 감성 분석 지도 (오밀조밀한 버블 레이아웃 적용) ---
        with sentiment_map_container:
            s_stats = x_ai.get('sentiment_stats', [60, 25, 10, 5])
            e_words = x_ai.get('emotional_words', [])
            # 단어가 부족할 경우를 대비한 기본값
            if len(e_words) < 5:
                e_words.extend(["트렌드", "반응", "이슈", "특징", "리뷰", "꿀팁", "장점", "단점", "추천", "공유"])
                
            s_score = x_ai.get('satisfaction_score', 80)
            
            sc1, sc2, sc3 = st.columns([1, 2.5, 1])
            
            with sc1:
                st.markdown("<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 5px;'>게시물 성향</div>", unsafe_allow_html=True)
                donut_html = f"""
                <div style='position: relative; width: 100px; height: 100px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% {s_stats[0]}%, #FF00FF {s_stats[0]}% {s_stats[0]+s_stats[1]}%, #448aff {s_stats[0]+s_stats[1]}% 100%); display: flex; justify-content: center; align-items: center;'>
                    <div style='width: 70px; height: 70px; background-color: #1a1b26; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #00E5FF; font-size: 14px;'>{s_stats[0]}%</div>
                </div>"""
                st.markdown(donut_html, unsafe_allow_html=True)
            
            with sc2:
                st.markdown(f"<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 5px;'>감성 클러스터</div>", unsafe_allow_html=True)
                
                # Flexbox를 활용해 단어들을 중앙으로 오밀조밀하게 모으는 로직
                bubble_html = "<div style='display: flex; flex-wrap: wrap; justify-content: center; align-content: center; gap: 8px; height: 160px; padding: 10px;'>"
                colors = ["#FF00FF", "#00E5FF", "#448aff", "#a9b1d6", "#00E5FF", "#FF00FF", "#448aff", "#a9b1d6", "#FF00FF", "#00E5FF"]
                sizes = [18, 14, 20, 13, 16, 12, 17, 11, 15, 13] # 다양한 크기
                
                for i, word in enumerate(e_words[:10]):
                    color = colors[i % len(colors)]
                    size = sizes[i % len(sizes)]
                    bubble_html += f"<div style='color: {color}; font-size: {size}px; font-weight: bold; background: rgba(255,255,255,0.08); padding: 5px 12px; border-radius: 20px; border: 1px solid {color}44; white-space: nowrap;'>{word}</div>"
                bubble_html += "</div>"
                
                st.markdown(bubble_html, unsafe_allow_html=True)
            
            with sc3:
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

        # --- [하단 오른쪽] 베스트 꿀팁 / 연관 노하우 ---
        with tips_container:
            st.markdown("<div style='text-align: right; font-size: 11px; color: #888888; margin-bottom: 5px;'><span>🔖 실시간 유저 노하우</span></div>", unsafe_allow_html=True)
            
            # 1. 다중 키 검사 (or 연산자를 사용하여 null이나 빈 리스트를 완벽히 걸러냄)
            tips = x_ai.get('tips') or x_ai.get('user_tips') or x_ai.get('knowhow')
            
            # 2. AI가 빈 값을 줬을 때 앱이 깨지지 않도록 '무조건' 출력할 기본 데이터 강제 주입
            if not tips or not isinstance(tips, list) or len(tips) == 0:
                tips = [
                    {"title": "구매/사용 팁", "highlight": f"{main_keyword} 핵심 포인트", "desc": "현재 SNS 상의 다양한 의견과 노하우를 종합하고 있습니다."},
                    {"title": "연관 정보", "highlight": "유저들의 숨은 꿀팁", "desc": "실시간 반응이 모이면 더욱 구체적인 팁이 표시됩니다."}
                ]
            
            # 3. 카드 무조건 렌더링
            tips_html = ""
            for i, t in enumerate(tips[:3]):
                # 만약 AI가 딕셔너리 구조가 아닌 이상한 텍스트를 넣었을 경우를 대비한 방어
                if not isinstance(t, dict):
                    continue
                    
                t_title = t.get('title', '정보')
                t_high = t.get('highlight', t.get('title', f'{main_keyword} 노하우'))
                t_desc = t.get('desc', '상세 내용을 확인 중입니다.')
                
                tips_html += f"""
                <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 12px; margin-bottom: 8px;'>
                    <div style='display: flex; align-items: flex-start;'>
                        <div style='color: #4fc3f7; font-size: 15px; font-weight: bold; width: 25px;'>{i+1}</div>
                        <div style='flex: 1;'>
                            <div style='color: #a9b1d6; font-size: 12px; margin-bottom: 2px;'>{t_title}</div>
                            <div style='color: #ffffff; font-size: 14px; font-weight: bold; margin-bottom: 2px;'>{t_high}</div>
                            <div style='color: #888888; font-size: 11px; line-height: 1.3;'>{t_desc}</div>
                        </div>
                    </div>
                </div>"""
            st.markdown(tips_html, unsafe_allow_html=True)