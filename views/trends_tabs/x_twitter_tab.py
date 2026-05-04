import streamlit as st
import altair as alt
import pandas as pd
from modules.trend_state_manager import fetch_trend_data

# --------------------------------------
# 🔥 데이터 보정 및 계층 구조 정규화 함수
# --------------------------------------
def normalize_x_data(main_data, keyword):
    """
    AI 응답이 실패하거나 구조가 꼬였을 때를 대비해 
    데이터 계층을 강제로 맞추고 기본값을 할당합니다.
    """
    if not main_data or not isinstance(main_data, dict):
        main_data = {}

    # 1. x_sentiment 계층 확보
    # fetch_trend_data에서 넘어온 데이터 구조를 한번 더 검생
    x_ai = main_data.get("x_sentiment", {})
    if not isinstance(x_ai, dict):
        x_ai = {}

    # 2. 감성 수치(stats) 보정
    if not isinstance(x_ai.get("sentiment_stats"), list) or len(x_ai.get("sentiment_stats", [])) < 4:
        x_ai["sentiment_stats"] = [65, 20, 10, 5]

    # 3. 감성 키워드(emotional_words) 보정
    if not x_ai.get("emotional_words"):
        x_ai["emotional_words"] = [
            f"{keyword} 반응", f"{keyword} 이슈", f"{keyword} 추천", 
            "실시간", "트렌드", "인기", "공유", "궁금", "대박", "후기"
        ]

    # 4. 만족도 점수 보정
    if not isinstance(x_ai.get("satisfaction_score"), (int, float)):
        x_ai["satisfaction_score"] = 80

    # 5. 꿀팁(tips) 보정 (무조건 3개 리스트 보장)
    tips = x_ai.get("tips", [])
    if not isinstance(tips, list) or len(tips) < 1:
        x_ai["tips"] = [
            {
                "title": f"{keyword} 분석 진행 중",
                "highlight": "데이터 로드 중",
                "desc": "실시간 트위터 반응을 AI가 정밀하게 분석하고 있습니다."
            }
        ] * 3
    elif len(tips) < 3:
        # 개수가 부족할 경우 기본 팁으로 채움
        while len(x_ai["tips"]) < 3:
            x_ai["tips"].append({
                "title": f"{keyword} 추가 팁",
                "highlight": "트렌드 모니터링",
                "desc": "해당 키워드에 대한 실시간 언급량을 지속적으로 확인하세요."
            })

    # 최종적으로 정제된 데이터를 다시 할당
    main_data["x_sentiment"] = x_ai
    return main_data

# --------------------------------------
# 🔥 메인 렌더링 함수
# --------------------------------------
def render(tab_name: str, prompt_input: str, global_main_keyword: str):
    keyword = global_main_keyword

    # 1. 데이터 가져오기
    try:
        # fetch_trend_data 내부에서 네이버 연관 검색어를 realtime_keywords에 이미 매핑한 상태여야 함
        main_data, _ = fetch_trend_data(tab_name, keyword)
    except Exception as e:
        st.error(f"X 탭 데이터 로드 실패: {e}")
        main_data = {}

    # 2. 데이터 정규화 및 보정 (기본값만 뜨는 문제 해결 핵심)
    main_data = normalize_x_data(main_data, keyword)
    
    x_ai = main_data["x_sentiment"]
    real_keywords = main_data.get("realtime_keywords", []) # 네이버 검색어 데이터

    # 3. 화면 레이아웃 구성
    left_col, right_col = st.columns([2, 1], gap="large")

    # ======================================
    # 🔵 LEFT COLUMN: 트렌드 및 감성 분석
    # ======================================
    with left_col:
        st.markdown(f"### <span style='color:#4fc3f7'>{keyword}</span> 트렌드 추이", unsafe_allow_html=True)

        # [차트 영역]
        df_time = main_data.get("time_series")
        if isinstance(df_time, pd.DataFrame) and not df_time.empty:
            chart = alt.Chart(df_time).mark_area(
                line={'color': '#00E5FF'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#00E5FF', offset=0),
                        alt.GradientStop(color='transparent', offset=1)
                    ],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('date:T', title='날짜'),
                y=alt.Y('clicks:Q', title='검색/언급량')
            ).properties(height=300)

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("실시간 트렌드 추이 데이터를 분석 중입니다.")

        st.markdown("<br>", unsafe_allow_html=True)

        # [감성 분석 영역]
        st.markdown("#### 정보 공유 및 감성 분석 지도")
        
        s_stats = x_ai["sentiment_stats"]
        e_words = x_ai["emotional_words"]
        s_score = x_ai["satisfaction_score"]

        sc1, sc2, sc3 = st.columns([1, 1.8, 1])

        with sc1:
            st.markdown("##### 게시물 성향")
            st.markdown(f"""
            <div style='width:100px;height:100px;margin:auto;border-radius:50%;
            background:conic-gradient(#00E5FF 0% {s_stats[0]}%, #FF00FF {s_stats[0]}% 85%, #448aff 85% 100%);
            display:flex;align-items:center;justify-content:center;'>
                <div style='width:70px;height:70px;background:#1a1b26;border-radius:50%;
                display:flex;align-items:center;justify-content:center;color:#00E5FF;font-weight:bold;font-size:18px;'>
                {s_stats[0]}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("긍정 반응 비율")

        with sc2:
            st.markdown("##### 감성 클러스터")
            bubble_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;justify-content:center;'>"
            colors = ["#FF00FF", "#00E5FF", "#448aff", "#a9b1d6"]
            for i, word in enumerate(e_words[:10]):
                c = colors[i % 4]
                bubble_html += f"<span style='color:{c};border:1px solid {c};padding:4px 8px;border-radius:12px;font-size:12px'>{word}</span>"
            bubble_html += "</div>"
            st.markdown(bubble_html, unsafe_allow_html=True)

        with sc3:
            st.markdown("##### 만족도")
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            st.metric("Trend Score", f"{s_score}점")

    # ======================================
    # 🟣 RIGHT COLUMN: 키워드 및 팁
    # ======================================
    with right_col:
        # [실시간 키워드 TOP 7] - 네이버 검색어 기반
        st.markdown("#### 실시간 키워드 TOP 7")
        if real_keywords:
            for i, k in enumerate(real_keywords[:7]):
                st.markdown(f"""
                <div style='padding:8px 0; border-bottom:1px solid #2d2e3a; font-size:15px;'>
                    <span style='color:#00E5FF; font-weight:bold; margin-right:10px;'>{i+1}</span> {k}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("연관 키워드 데이터를 불러올 수 없습니다.")

        st.markdown("<br>", unsafe_allow_html=True)

        # [AI 베스트 꿀팁]
        st.markdown("#### 베스트 꿀팁 💡")
        for t in x_ai.get("tips", []):
            st.markdown(f"""
            <div style='background:#1a1b26; padding:12px; border-radius:10px; margin-bottom:10px; border-left:4px solid #FF00FF'>
                <b style='color:#FF00FF; font-size:14px;'>{t.get('highlight', 'Check Point')}</b><br>
                <span style='font-size:12px; color:#d1d5db; line-height:1.6;'>{t.get('desc', '')}</span>
            </div>
            """, unsafe_allow_html=True)