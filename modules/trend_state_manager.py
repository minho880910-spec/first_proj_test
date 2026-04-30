import streamlit as st
import altair as alt
import textwrap
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
            st.markdown(f"### <span style='color:#00E5FF'>{main_keyword}</span> 대화량 추이 <span style='font-size: 0.6em; color: #888888; font-weight: normal; margin-left: 8px;'>(최근 24시간)</span>", unsafe_allow_html=True)
            df_time = main_data.get('time_series')
            if df_time is not None:
                chart = alt.Chart(df_time).mark_line(color='#FF00FF', strokeWidth=2).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # --- [상단 오른쪽] 급상승 연관 대화 키워드 ---
        mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#4fc3f7'>{main_keyword}</span> 급상승 키워드", unsafe_allow_html=True)
            main_queries = main_data.get('top_queries', [])
            if main_queries:
                html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
                items_html = ""
                for i, q in enumerate(main_queries[:7]):
                    count_txt = f"{mock_counts[i % len(mock_counts)]} 포스트 🔥"
                    items_html += f"""
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'>
                        <div style='display:flex; align-items:center;'><strong style='color: #4fc3f7; width: 25px;'>{i+1}</strong> <span>{q}</span></div>
                        <span style='color: #a9b1d6; font-size: 13px;'>{count_txt}</span>
                    </div>"""
                
                full_html = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; color: #a9b1d6;'>{items_html}</div>"
                st.markdown(full_html, unsafe_allow_html=True)

        # --- [하단 왼쪽] 뜨거운 감자 (Hot Discussions) ---
        with hot_discussion_container:
            hot_discussions = main_data.get('hot_discussions', [])
            if hot_discussions:
                cols = st.columns(3)
                for i, disc in enumerate(hot_discussions[:3]):
                    with cols[i]:
                        header = f"<h5 style='color: #a9b1d6; font-size: 16px; margin-bottom: 5px;'><span style='color: #4fc3f7;'>{i+1}</span> {disc['title']}</h5>"
                        stats = f"<div style='font-size: 13px; margin-bottom: 10px;'><span style='color: #00E5FF;'>↪ {disc['replies']}답글</span> &nbsp; <span style='color: #00E5FF;'>{disc['quotes']}인용</span></div>"
                        
                        card = f"""
                        <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; color: #a9b1d6;'>
                            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                                <div style='width: 35px; height: 35px; background-color: #448aff; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 10px;'>👤</div>
                                <div style='line-height: 1.2;'>
                                    <div style='font-weight: bold; font-size: 13px;'>{disc['handle']}</div>
                                    <div style='font-size: 11px; color: #888888;'>{disc['author']}</div>
                                </div>
                            </div>
                            <div style='font-size: 13px; line-height: 1.4; height: 60px; overflow: hidden;'>{disc['content']}</div>
                        </div>"""
                        st.markdown(header + stats + card, unsafe_allow_html=True)

        # --- [하단 오른쪽] 스레드 오피니언 리더 ---
        with influencers_container:
            influencers = main_data.get('top_influencers', [])
            if influencers:
                rows_html = ""
                for inf in influencers:
                    rows_html += f"""
                    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #292e42;'>
                        <div style='display: flex; align-items: center;'>
                            <div style='color: #4fc3f7; font-size: 16px; font-weight: bold; width: 25px;'>{inf.get('rank', '-')}</div>
                            <div style='width: 35px; height: 35px; background-color: #2a2e3f; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 10px;'>👤</div>
                            <div style='line-height: 1.2;'>
                                <div style='font-size: 13px; font-weight: bold; color: #ffffff;'>{inf.get('handle', '@user')}</div>
                                <div style='font-size: 11px; color: #888888;'>{inf.get('name', '사용자')}</div>
                            </div>
                        </div>
                        <div style='text-align: right; line-height: 1.2;'>
                            <div style='font-size: 12px; color: #4fc3f7;'>{inf.get('mentions', '0')} 멘션</div>
                            <div style='font-size: 10px; color: #565f89;'>{inf.get('followers', '0')}</div>
                        </div>
                    </div>"""
                
                full_box = f"<div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px;'>{rows_html}</div>"
                st.markdown(full_box, unsafe_allow_html=True)
            else:
                st.info("데이터가 없습니다.")