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
        st.markdown("#### 답글 / 인용이 많은 뜨거운 감자")
        hot_discussion_container = st.container()
        
    with bot_col2:
        st.markdown("#### 스레드 오피니언 리더", unsafe_allow_html=True)
        influencers_container = st.container()

    # 데이터 가져오기 (통합된 fetch_trend_data 사용)
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
            if isinstance(df_time, pd.DataFrame) and not df_time.empty:
                chart = alt.Chart(df_time).mark_line(color='#FF00FF', strokeWidth=3, point=True).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format='%m-%d', labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='대화지수', axis=alt.Axis(grid=True, tickCount=3)),
                    tooltip=['date', 'clicks']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("실시간 대화량 데이터를 분석 중입니다.")

        # --- [상단 오른쪽] 급상승 키워드 ---
        with keyword_related_container:
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
            else:
                st.caption("연관 키워드를 불러오지 못했습니다.")

        # --- [하단 왼쪽] 뜨거운 감자 (KeyError 방지 적용) ---
        with hot_discussion_container:
            hot_discussions = main_data.get('hot_discussions', [])
            if hot_discussions:
                cols = st.columns(3)
                for i, disc in enumerate(hot_discussions[:3]):
                    with cols[i]:
                        # .get()을 사용하여 데이터 부재 시에도 에러 방지
                        title = disc.get('title', '인기 게시글')
                        replies = disc.get('replies', 0)
                        quotes = disc.get('quotes', 0)
                        handle = disc.get('handle', '@user')
                        author = disc.get('author', 'Threads User')
                        content = disc.get('content', '내용을 불러올 수 없습니다.')

                        header = f"<div style='font-size: 14px; margin-bottom: 5px; font-weight: bold; color: #a9b1d6;'><span style='color: #4fc3f7;'>{i+1}</span> {title}</div>"
                        stats = f"""
                        <div style='font-size: 12px; margin-bottom: 8px;'>
                            <span style='color: #00E5FF;'>↪ {replies}답글</span> &nbsp; 
                            <span style='color: #00E5FF;'>{quotes}인용</span>
                        </div>
                        """
                        card = f"""
                        <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 12px; color: #a9b1d6;'>
                            <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                                <div style='width: 30px; height: 30px; background-color: #448aff; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 8px; font-size: 12px;'>👤</div>
                                <div style='line-height: 1.1;'>
                                    <div style='font-weight: bold; font-size: 12px; color: #fff;'>{handle}</div>
                                    <div style='font-size: 10px; color: #888;'>{author}</div>
                                </div>
                            </div>
                            <div style='font-size: 12px; line-height: 1.5; height: 55px; overflow: hidden;'>{content}</div>
                        </div>"""
                        st.markdown(header + stats + card, unsafe_allow_html=True)
            else:
                st.info("현재 뜨거운 반응이 있는 게시글을 분석 중입니다.")

        # --- [하단 오른쪽] 스레드 오피니언 리더 ---
        with influencers_container:
            influencers = main_data.get('top_influencers', [])
            if influencers:
                rows_html = ""
                for i, inf in enumerate(influencers[:5]):
                    # rank가 없으면 인덱스(i+1) 사용
                    rank = inf.get('rank', i + 1)
                    handle = inf.get('handle', '@user')
                    name = inf.get('name', '사용자')
                    mentions = inf.get('mentions', 0)
                    followers = inf.get('followers', 'N/A')

                    rows_html += f"""
                    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #292e42;'>
                        <div style='display: flex; align-items: center;'>
                            <div style='color: #4fc3f7; font-size: 14px; font-weight: bold; width: 25px;'>{rank}</div>
                            <div style='width: 30px; height: 30px; background-color: #2a2e3f; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 8px;'>👤</div>
                            <div style='line-height: 1.1;'>
                                <div style='font-size: 12px; font-weight: bold; color: #ffffff;'>{handle}</div>
                                <div style='font-size: 10px; color: #888888;'>{name}</div>
                            </div>
                        </div>
                        <div style='text-align: right; line-height: 1.1;'>
                            <div style='font-size: 11px; color: #4fc3f7;'>{mentions} 멘션</div>
                            <div style='font-size: 9px; color: #565f89;'>{followers}</div>
                        </div>
                    </div>"""
                st.markdown(f"<div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px;'>{rows_html}</div>", unsafe_allow_html=True)
            else:
                st.info("영향력 있는 오피니언 리더를 찾는 중입니다.")