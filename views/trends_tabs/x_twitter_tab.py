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
        st.markdown("#### 정보 공유 및 감성 분석 지도 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
        sentiment_map_container = st.container()
        
    with bot_col2:
        st.markdown("#### 베스트 꿀팁 / 연관 노하우 💡 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
        tips_container = st.container()

    main_data, cat_data = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        with col1:
            st.markdown(f"### <span style='color:#4fc3f7'>{main_keyword}</span> 트렌드 추이 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            x_format = '%m-%d'
            df_time = main_data['time_series']
            chart = alt.Chart(df_time).mark_area(
                line={'color': '#00E5FF'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#00E5FF', offset=0),
                           alt.GradientStop(color='rgba(0, 229, 255, 0)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)

        mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
        
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#a9b1d6'>{main_keyword}</span> 실시간 꿀팁 & 검색어 Top 7 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>최근 1주일 기준</span>", unsafe_allow_html=True)
            
            main_queries = main_data.get('top_queries', [])
            
            if main_queries:
                html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
                text_color = "color: #a9b1d6;"
                num_color = "#4fc3f7"
                html_content_main = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; {text_color} margin-bottom: 10px;'>"
                for i, q in enumerate(main_queries[:7]):
                    if q:
                        count_html = f"<span style='color: #4fc3f7; font-size: 13px;'>{mock_counts[i % len(mock_counts)]}</span>"
                        html_content_main += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color}; width: 25px;'>{i+1}</strong> <span>{q}</span></div> {count_html}</div>"
                html_content_main += "</div>"
                st.markdown(html_content_main, unsafe_allow_html=True)
            else:
                st.info("연관 데이터가 없습니다.")

        with sentiment_map_container:
            sc1, sc2, sc3, sc4 = st.columns([1.2, 2, 1, 1])
            
            with sc1:
                st.markdown("<div style='text-align: center; font-size: 14px; color: #a9b1d6; margin-bottom: 5px;'>누적 언급량: 98k+</div>", unsafe_allow_html=True)
                donut1_html = """
                <div style='position: relative; width: 120px; height: 120px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% 60%, #FF00FF 60% 85%, #448aff 85% 95%, #888888 95% 100%); display: flex; justify-content: center; align-items: center;'>
                    <div style='width: 80px; height: 80px; background-color: #1a1b26; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; color: #00E5FF;'>60%</div>
                </div>
                <div style='font-size: 11px; color: #a9b1d6; margin-top: 10px; line-height: 1.5;'>
                    <span style='color:#00E5FF'>●</span> 정보/노하우 (60%)<br>
                    <span style='color:#FF00FF'>●</span> 긍정 감성 (25%)<br>
                    <span style='color:#448aff'>●</span> 리뷰/후기 (10%)<br>
                    <span style='color:#888888'>●</span> 기타 (5%)
                </div>
                <div style='text-align: center; margin-top: 10px; font-weight: bold; color: #a9b1d6;'>게시물 성향</div>
                """
                st.markdown(donut1_html, unsafe_allow_html=True)
            
            with sc2:
                st.markdown(f"<div style='text-align: center; font-size: 14px; color: #a9b1d6; margin-bottom: 5px;'>{main_keyword} 테마 맵</div>", unsafe_allow_html=True)
                wordcloud_html = f"""
                <div style='position: relative; height: 180px; background-color: transparent; display: flex; justify-content: center; align-items: center;'>
                    <div style='position: absolute; top: 10%; left: 20%; background-color: rgba(255, 0, 255, 0.2); border: 1px solid #FF00FF; color: #FF00FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);'>존맛</div>
                    <div style='position: absolute; top: 15%; right: 20%; background-color: rgba(255, 0, 255, 0.2); border: 1px solid #FF00FF; color: #FF00FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);'>감성적</div>
                    <div style='position: absolute; top: 40%; left: 10%; background-color: rgba(68, 138, 255, 0.2); border: 1px solid #448aff; color: #448aff; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(68, 138, 255, 0.5);'>행복적</div>
                    <div style='position: absolute; top: 45%; right: 10%; background-color: rgba(0, 229, 255, 0.2); border: 1px solid #00E5FF; color: #00E5FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);'>귀여운</div>
                    <div style='position: absolute; top: 50%; left: 40%; background-color: #00E5FF; color: #000; padding: 8px 15px; border-radius: 20px; font-size: 18px; font-weight: bold; box-shadow: 0 0 15px rgba(0, 229, 255, 0.8);'>행복</div>
                    <div style='position: absolute; bottom: 20%; left: 15%; background-color: rgba(0, 229, 255, 0.2); border: 1px solid #00E5FF; color: #00E5FF; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);'>카페투어</div>
                    <div style='position: absolute; bottom: 25%; right: 15%; background-color: rgba(68, 138, 255, 0.2); border: 1px solid #448aff; color: #448aff; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(68, 138, 255, 0.5);'>인증샷</div>
                    <div style='position: absolute; bottom: 5%; right: 30%; background-color: rgba(68, 138, 255, 0.2); border: 1px solid #448aff; color: #448aff; padding: 5px 10px; border-radius: 15px; font-size: 14px; box-shadow: 0 0 10px rgba(68, 138, 255, 0.5);'>성수동맛집</div>
                </div>
                <div style='text-align: center; margin-top: 10px; font-weight: bold; color: #a9b1d6;'>{main_keyword} 연관 <span style='color: #FF00FF;'>감성</span> 클러스터</div>
                """
                st.markdown(wordcloud_html, unsafe_allow_html=True)
            
            with sc3:
                st.markdown("<div style='text-align: center; font-size: 12px; color: #a9b1d6; margin-bottom: 25px;'>&nbsp;</div>", unsafe_allow_html=True)
                gauge_html = """
                <div style='position: relative; width: 100px; height: 50px; margin: 0 auto; background-color: #292e42; border-top-left-radius: 100px; border-top-right-radius: 100px; overflow: hidden;'>
                    <div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: conic-gradient(from 270deg, #00E5FF 0deg, #448aff 90deg, #FF00FF 180deg); opacity: 0.8;'></div>
                    <div style='position: absolute; bottom: 0; left: 50%; width: 60px; height: 30px; background-color: #1a1b26; border-top-left-radius: 60px; border-top-right-radius: 60px; transform: translateX(-50%);'></div>
                    <div style='position: absolute; bottom: 0; left: 50%; width: 2px; height: 40px; background-color: #a9b1d6; transform-origin: bottom center; transform: translateX(-50%) rotate(45deg);'></div>
                </div>
                <div style='display: flex; justify-content: space-between; width: 120px; margin: 5px auto 0; font-size: 11px; color: #a9b1d6;'>
                    <span>Low</span>
                    <span>매우 만족</span>
                </div>
                <div style='text-align: center; margin-top: 20px; font-weight: bold; color: #a9b1d6;'>감성 만족도</div>
                """
                st.markdown(gauge_html, unsafe_allow_html=True)
            
            with sc4:
                st.markdown("<div style='text-align: center; font-size: 14px; color: #a9b1d6; margin-bottom: 5px;'>누적 언급량: 98k+</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; font-size: 12px; color: #ffb74d; margin-bottom: 5px;'>실시간 긍정 감성 전파 중</div>", unsafe_allow_html=True)
                donut2_html = """
                <div style='position: relative; width: 90px; height: 90px; margin: 0 auto; border-radius: 50%; background: conic-gradient(#00E5FF 0% 35%, #FF00FF 35% 75%, #448aff 75% 95%, #888888 95% 100%); display: flex; justify-content: center; align-items: center;'>
                    <div style='width: 50px; height: 50px; background-color: #1a1b26; border-radius: 50%;'></div>
                    <div style='position: absolute; top: 35%; right: 10%; font-size: 10px; color: #FF00FF; font-weight: bold;'>40%</div>
                    <div style='position: absolute; bottom: 15%; left: 20%; font-size: 10px; color: #00E5FF; font-weight: bold;'>35%</div>
                    <div style='position: absolute; top: 35%; left: 10%; font-size: 10px; color: #448aff; font-weight: bold;'>20%</div>
                </div>
                <div style='text-align: center; margin-top: 15px; font-weight: bold; color: #a9b1d6;'>유입 맥락</div>
                """
                st.markdown(donut2_html, unsafe_allow_html=True)

        with tips_container:
            st.markdown("<div style='text-align: right; font-size: 12px; color: #888888; margin-bottom: 10px;'><span>🔖 인용</span> &nbsp;|&nbsp; <span>💬 맨션</span></div>", unsafe_allow_html=True)
            tips_html = f"""
            <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; margin-bottom: 10px;'>
                <div style='display: flex; align-items: flex-start;'>
                    <div style='color: #4fc3f7; font-size: 16px; font-weight: bold; width: 20px;'>1</div>
                    <div>
                        <div style='color: #a9b1d6; font-size: 14px; margin-bottom: 5px;'>[{main_keyword}] 에어프라이어 완벽 해동! 시간</div>
                        <div style='color: #ffffff; font-size: 15px; font-weight: bold; margin-bottom: 5px;'>별 굽기 온도</div>
                        <div style='color: #888888; font-size: 12px;'>⏱️ 5분 &nbsp; 🌡️ 180도 &nbsp; 냉동은 5~7분이 적당합니다.</div>
                    </div>
                </div>
            </div>
            <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; margin-bottom: 10px;'>
                <div style='display: flex; align-items: center;'>
                    <div style='color: #4fc3f7; font-size: 16px; font-weight: bold; width: 20px;'>2</div>
                    <div>
                        <div style='color: #a9b1d6; font-size: 14px; margin-bottom: 5px;'>맛있게 먹는 법: 버터 & 소금 조합</div>
                        <div style='color: #888888; font-size: 12px;'>🥐 맛있게 먹는 법: 버터 & 소금 조합</div>
                    </div>
                </div>
            </div>
            <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px;'>
                <div style='display: flex; align-items: center;'>
                    <div style='color: #4fc3f7; font-size: 16px; font-weight: bold; width: 20px;'>3</div>
                    <div>
                        <div style='color: #a9b1d6; font-size: 14px; margin-bottom: 5px;'>{main_keyword}과 잘 어울리는 음료 BEST 3</div>
                        <div style='color: #888888; font-size: 12px;'>☕ 🥛 🍵</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(tips_html, unsafe_allow_html=True)
    elif main_data:
        st.write(main_data)
