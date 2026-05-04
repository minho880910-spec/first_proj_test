import streamlit as st
import altair as alt
import pandas as pd
from .trend_state_manager import fetch_trend_data

def normalize_x_data(main_data, keyword):
    """데이터가 없거나 구조가 깨졌을 때를 대비한 최종 방어선"""
    if not main_data: main_data = {}
    
    # 1. x_sentiment 추출 및 보정
    x_ai = main_data.get("x_sentiment", {})
    if not isinstance(x_ai, dict): x_ai = {}

    # 감성 수치 보정
    if not x_ai.get("sentiment_stats"):
        x_ai["sentiment_stats"] = [65, 20, 10, 5]
    
    # 감성 단어 보정
    if not x_ai.get("emotional_words"):
        x_ai["emotional_words"] = [f"{keyword} 반응", "실시간", "인기", "이슈", "추천"]

    # 만족도 점수 보정
    if "satisfaction_score" not in x_ai:
        x_ai["satisfaction_score"] = 80

    # 꿀팁 보정 (리스트가 비었거나 개수가 모자랄 때)
    tips = x_ai.get("tips", [])
    if not isinstance(tips, list) or len(tips) < 1:
        x_ai["tips"] = [
            {"title": f"{keyword} 정보", "highlight": "실시간 분석 중", "desc": "현재 데이터를 분석하고 있습니다."}
        ] * 3
    
    main_data["x_sentiment"] = x_ai
    return main_data

def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    keyword = global_main_keyword

    # 1. 데이터 가져오기 및 보정
    try:
        main_data, _ = fetch_trend_data(tab_name, keyword)
    except Exception as e:
        st.error(f"데이터 로드 에러: {e}")
        main_data = {}

    main_data = normalize_x_data(main_data, keyword)
    x_ai = main_data["x_sentiment"]

    # 2. 레이아웃 구성
    left_col, right_col = st.columns([2, 1], gap="large")

    with left_col:
        st.markdown(f"### <span style='color:#4fc3f7'>{keyword}</span> 트렌드 분석", unsafe_allow_html=True)
        
        # [시계열 차트]
        df_time = main_data.get("time_series")
        if isinstance(df_time, pd.DataFrame) and not df_time.empty:
            chart = alt.Chart(df_time).mark_area(
                line={'color': '#00E5FF'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#00E5FF', offset=0), alt.GradientStop(color='transparent', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(x='date:T', y='clicks:Q').properties(height=250)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("실시간 트렌드 추이 데이터를 불러오는 중입니다.")

        # [감성 분석 섹션]
        st.markdown("#### 실시간 감성 지표")
        sc1, sc2, sc3 = st.columns([1, 1.8, 1])
        
        with sc1:
            st.markdown("##### 게시물 성향")
            s_stats = x_ai["sentiment_stats"]
            st.markdown(f"""
                <div style='width:100px;height:100px;margin:auto;border-radius:50%;
                background:conic-gradient(#00E5FF 0% {s_stats[0]}%, #FF00FF {s_stats[0]}% 85%, #448aff 85% 100%);
                display:flex;align-items:center;justify-content:center;'>
                <div style='width:70px;height:70px;background:#1a1b26;border-radius:50%;
                display:flex;align-items:center;justify-content:center;color:#00E5FF;font-weight:bold;'>
                {s_stats[0]}%</div></div>
            """, unsafe_allow_html=True)

        with sc2:
            st.markdown("##### 감성 키워드")
            e_words = x_ai["emotional_words"]
            bubble_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;justify-content:center;'>"
            colors = ["#FF00FF", "#00E5FF", "#448aff", "#a9b1d6"]
            for i, word in enumerate(e_words[:10]):
                c = colors[i % 4]
                bubble_html += f"<span style='color:{c};border:1px solid {c};padding:4px 8px;border-radius:12px;font-size:12px'>{word}</span>"
            bubble_html += "</div>"
            st.markdown(bubble_html, unsafe_allow_html=True)

        with sc3:
            st.markdown("##### 만족도 점수")
            st.metric("Score", f"{x_ai['satisfaction_score']}점")

    with right_col:
        # [실시간 토론 주제]
        st.markdown("#### 실시간 화제 주제 💬")
        hot_topics = main_data.get("hot_discussions", [])
        for topic in hot_topics:
            st.info(topic) if topic else st.write("-")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # [베스트 꿀팁]
        st.markdown("#### 베스트 꿀팁 💡")
        for t in x_ai.get("tips", []):
            st.markdown(f"""
                <div style='background:#1a1b26;padding:12px;border-radius:10px;margin-bottom:10px;border-left:4px solid #00E5FF'>
                    <b style='color:#00E5FF'>{t.get('highlight', '')}</b><br>
                    <span style='font-size:12px;color:#d1d5db'>{t.get('desc', '')}</span>
                </div>
            """, unsafe_allow_html=True)