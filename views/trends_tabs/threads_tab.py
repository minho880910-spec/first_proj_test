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
            
            x_format = '%m-%d'
            df_time = main_data.get('time_series')
            if df_time is not None:
                chart = alt.Chart(df_time).mark_line(color='#FF00FF', strokeWidth=2).encode(
                    x=alt.X('date:T', title='', axis=alt.Axis(format=x_format, labelAngle=0, grid=False)),
                    y=alt.Y('clicks:Q', title='', axis=alt.Axis(grid=True, tickCount=3))
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        # --- [상단 오른쪽] 급상승 연관 대화 키워드 ---
        mock_counts = ["3.2k", "2.1k", "1.6k", "1.2k", "900", "850", "700", "500", "450", "300"]
        
        with keyword_related_container:
            st.markdown(f"#### <span style='color:#4fc3f7'>{main_keyword}</span> 급상승 연관 대화 키워드", unsafe_allow_html=True)
            main_queries = main_data.get('top_queries', [])
            
            if main_queries:
                html_bg = "background-color: #1a1b26; border: 1px solid #292e42;"
                text_color = "color: #a9b1d6;"
                num_color = "#4fc3f7"
                html_content_main = f"<div style='{html_bg} padding: 15px; border-radius: 10px; height: 250px; overflow-y: auto; {text_color} margin-bottom: 10px;'>"
                for i, q in enumerate(main_queries[:7]):
                    if q:
                        count_html = f"<span style='color: #a9b1d6; font-size: 13px;'>{mock_counts[i % len(mock_counts)]} 포스트 🔥</span>"
                        html_content_main += f"<div style='display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px;'><div style='display:flex; align-items:center;'><strong style='color: {num_color}; width: 25px;'>{i+1}</strong> <span>{q}</span></div> {count_html}</div>"
                html_content_main += "</div>"
                st.markdown(html_content_main, unsafe_allow_html=True)
            else:
                st.info("연관 데이터가 없습니다.")

        # --- [하단 왼쪽] 뜨거운 감자 (Hot Discussions) ---
        with hot_discussion_container:
            hot_discussions = main_data.get('hot_discussions', [])
            if hot_discussions:
                cols = st.columns(3)
                for i, disc in enumerate(hot_discussions[:3]):
                    with cols[i]:
                        st.markdown(f"<h5 style='color: #a9b1d6; font-size: 16px; margin-bottom: 5px;'><span style='color: #4fc3f7;'>{i+1}</span> {disc['title']}</h5>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size: 13px; margin-bottom: 15px;'><span style='color: #00E5FF;'>↪ {disc['replies']}답글</span> &nbsp; <span style='color: #00E5FF;'>{disc['quotes']}인용</span></div>", unsafe_allow_html=True)
                        
                        card_html = textwrap.dedent(f"""
                        <div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 15px; color: #a9b1d6;'>
                            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                                <div style='width: 35px; height: 35px; background-color: #448aff; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 18px; margin-right: 10px;'>👤</div>
                                <div>
                                    <div style='font-weight: bold; font-size: 14px;'>{disc['handle']}</div>
                                    <div style='font-size: 12px; color: #888888;'>{disc['author']}</div>
                                </div>
                            </div>
                            <div style='font-size: 14px; margin-bottom: 15px; line-height: 1.5;'>{disc['content']}</div>
                            <div style='display: flex; gap: 15px; color: #888888; font-size: 16px;'>♡ 💬 ⟲ ↗</div>
                        </div>
                        """)
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("뜨거운 감자 데이터가 없습니다.")
        
        # --- [하단 오른쪽] 스레드 오피니언 리더 ---
        with influencers_container:
            influencers = main_data.get('top_influencers', [])
            
            if influencers:
                # 1. 전체를 감싸는 컨테이너 시작
                inf_html = "<div style='background-color: #1a1b26; border: 1px solid #292e42; border-radius: 12px; padding: 20px; color: #a9b1d6;'>"
                
                # 2. 반복문을 통해 데이터 하나씩 HTML 생성
                for inf in influencers:
                    inf_html += f"""
                    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;'>
                        <div style='display: flex; align-items: center;'>
                            <!-- 순위 -->
                            <div style='color: #4fc3f7; font-size: 18px; font-weight: bold; width: 30px;'>{inf.get('rank', '-')}</div>
                            
                            <!-- 프로필 아이콘 (원형) -->
                            <div style='width: 40px; height: 40px; background-color: #2a2e3f; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 20px; margin-right: 12px; border: 1px solid #3b4261;'>
                                👤
                            </div>
                            
                            <!-- 핸들 및 이름 -->
                            <div style='line-height: 1.3;'>
                                <div style='font-size: 14px; font-weight: bold; color: #ffffff;'>{inf.get('handle', '@user')}</div>
                                <div style='font-size: 12px; color: #888888;'>{inf.get('name', '사용자')}</div>
                            </div>
                        </div>
                        
                        <!-- 멘션 및 팔로워 정보 (오른쪽 정렬) -->
                        <div style='text-align: right; line-height: 1.3;'>
                            <div style='font-size: 13px; color: #4fc3f7; font-weight: 500;'>{inf.get('mentions', '0')} 멘션</div>
                            <div style='font-size: 11px; color: #565f89;'>{inf.get('followers', '0')} 팔로워</div>
                        </div>
                    </div>
                    """
                
                # 3. 컨테이너 닫기
                inf_html += "</div>"
                
                # 4. 최종적으로 한 번만 렌더링
                st.markdown(inf_html, unsafe_allow_html=True)
            else:
                st.info("오피니언 리더 데이터가 없습니다.")