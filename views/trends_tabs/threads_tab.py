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
        st.markdown("#### 답글 / 인용이 많은 뜨거운 감자")
        hot_discussion_container = st.container()
        
    with bot_col2:
        st.markdown("#### 스레드 오피니언 리더", unsafe_allow_html=True)
        influencers_container = st.container()

    # 데이터 가져오기
    main_data, cat_data = fetch_trend_data(tab_name, main_keyword)

    if main_data and isinstance(main_data, dict):
        # --- [상단 왼쪽] 대화량 추이 ---
        with col1:
            st.markdown(
                f"### <span style='color:#00E5FF'>{main_keyword}</span> 대화량 추이 "
                f"<span style='font-size: 0.8rem; color: gray; font-weight: normal; margin-left: 10px;'>최근 1달</span>", 
                unsafe_allow_html=True
            )
            df_time = main_data.get('time_series')
            if df_time is not None and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#FF00FF', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='대화지수', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # --- [상단 오른쪽] 급상승 키워드 (태그 노출 문제 해결) ---
        with keyword_related_container:
            # f-string 내부에서 HTML 태그가 깨지지 않도록 구조를 정리했습니다.
            st.markdown(f"#### <span style='color:#4fc3f7'>{main_keyword}</span> 급상승 키워드", unsafe_allow_html=True)
            
            main_queries = main_data.get('top_queries', [])
            mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
            if main_queries:
                html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
                items_html = ""
                for i, q in enumerate(main_queries[:7]):
                    count_txt = f"{mock_counts[i % len(mock_counts)]} 포스트 🔥"
                    items_html += f"""
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px;'>
                        <div style='display:flex; align-items:center;'><strong style='color: #4fc3f7; width: 25px;'>{i+1}</strong> <span>{q}</span></div>
                        <span style='color: #a9b1d6; font-size: 12px;'>{count_txt}</span>
                    </div>"""
                st.markdown(f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>{items_html}</div>", unsafe_allow_html=True)

        # --- [하단 왼쪽] 뜨거운 감자 (AI 보완 로직 적용) ---
        with hot_discussion_container:
            hot_discussions = main_data.get('hot_discussions', [])
            if hot_discussions:
                cols = st.columns(3)
                for i, disc in enumerate(hot_discussions[:3]):
                    with cols[i]:
                        header = f"<div style='font-size: 14px; margin-bottom: 5px; font-weight: bold; color: #a9b1d6;'><span style='color: #4fc3f7;'>{i+1}</span> {disc['title']}</div>"
                        stats = f"""
                        <div style='font-size: 12px; margin-bottom: 8px;'>
                            <span style='color: #00E5FF;'>↪ {disc.get('replies', 0)}답글</span> &nbsp; 
                            <span style='color: #00E5FF;'>{disc.get('quotes', 0)}인용</span>
                        </div>
                        """
                        card = f"""
                        <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 12px; color: #a9b1d6;'>
                            <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                                <div style='width: 30px; height: 30px; background-color: #448aff; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 8px; font-size: 12px;'>👤</div>
                                <div style='line-height: 1.1;'>
                                    <div style='font-weight: bold; font-size: 12px; color: #fff;'>{disc['handle']}</div>
                                    <div style='font-size: 10px; color: #888;'>{disc['author']}</div>
                                </div>
                            </div>
                            <div style='font-size: 12px; line-height: 1.5; height: 55px; overflow: hidden;'>{disc['content']}</div>
                        </div>"""
                        st.markdown(header + stats + card, unsafe_allow_html=True)

        # --- [하단 오른쪽] 스레드 오피니언 리더 (AI 보완 로직 적용) ---
        with influencers_container:
            influencers = main_data.get('top_influencers', [])
            if influencers:
                rows_html = ""
                for inf in influencers:
                    rows_html += f"""
                    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #292e42;'>
                        <div style='display: flex; align-items: center;'>
                            <div style='color: #4fc3f7; font-size: 14px; font-weight: bold; width: 25px;'>{inf.get('rank')}</div>
                            <div style='width: 30px; height: 30px; background-color: #2a2e3f; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 8px;'>👤</div>
                            <div style='line-height: 1.1;'>
                                <div style='font-size: 12px; font-weight: bold; color: #ffffff;'>{inf.get('handle')}</div>
                                <div style='font-size: 10px; color: #888888;'>{inf.get('name')}</div>
                            </div>
                        </div>
                        <div style='text-align: right; line-height: 1.1;'>
                            <div style='font-size: 11px; color: #4fc3f7;'>{inf.get('mentions')} 멘션</div>
                            <div style='font-size: 9px; color: #565f89;'>{inf.get('followers')}</div>
                        </div>
                    </div>"""
                st.markdown(f"<div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px;'>{rows_html}</div>", unsafe_allow_html=True)