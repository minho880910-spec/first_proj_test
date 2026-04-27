import streamlit as st
import datetime
import json

def render_page():
    # 💡 복사 버튼 상시 노출 및 박스 내부 스크롤 강제 제거 CSS
    st.markdown("""
        <style>
        /* 1. 복사 버튼 항상 보이게 고정 */
        .stCodeBlock button {
            opacity: 1 !important;
            visibility: visible !important;
            transform: scale(1) !important;
        }
        /* 2. 코드 박스 내부 스크롤바 없애고 전체 내용 한 번에 펼치기 */
        .stCodeBlock pre {
            max-height: none !important;      /* 최대 높이 제한 해제 */
            overflow-y: visible !important;   /* 세로 스크롤 숨김 */
            white-space: pre-wrap !important; /* 가로 스크롤 대신 줄바꿈 강제 */
            word-wrap: break-word !important; /* 긴 단어도 줄바꿈 */
        }
        </style>
        """, unsafe_allow_html=True)

    st.header("✍️ AI SNS 콘텐츠 통합 생성기")
    st.write("브랜드 정보와 주제를 바탕으로 5가지 맞춤형 마케팅 콘텐츠를 한 번에 기획합니다.")
    
    # 사용자 입력 폼
    with st.container(border=True):
        brand_name = st.text_input("🏢 브랜드명 (또는 가게명)", placeholder="예: 카페 지피지기")
        topic = st.text_input("💡 핵심 주제 또는 제품", value=st.session_state.get('search_keyword', ''))
        tone = st.select_slider("🎨 톤앤매너", options=["격식있는/전문적인", "진정성있는/감성적인", "친근한/일상적인", "유쾌한/재치있는"])

    if st.button("콘텐츠 일괄 생성하기", type="primary", use_container_width=True):
        client = st.session_state.get('openai_client')
        
        if not client:
            st.error("사이드바에 OpenAI API 키를 먼저 입력해주세요.")
            return
            
        if not brand_name:
            st.warning("브랜드명을 입력해주세요!")
            return

        with st.spinner("플랫폼별 최적화된 콘텐츠를 상세하게 기획 중입니다... (약 20초 소요)"):
            try:
                prompt = f"""
                당신은 최고의 SNS 마케팅 전략가입니다. 아래 정보를 바탕으로 불특정 다수에게 소구할 수 있는 5가지 형태의 콘텐츠를 작성하세요.

                - 브랜드명: {brand_name}
                - 핵심 주제: {topic}
                - 톤앤매너: {tone}

                [작성 지침]
                1. instagram: 시각적 묘사와 트렌디한 이모지를 활용해 감각적으로 작성하세요.
                2. threads: 친근하고 대화적인 어투로 짧고 강렬하게 소통을 유도하세요.
                3. blog: 
                   - 반드시 서론-본론-결론 구조를 갖출 것.
                   - 최소 3개 이상의 소제목(##)을 포함할 것.
                   - 분량은 공백 포함 1,500자 이상의 긴 글로 상세하게 작성할 것.
                   - 전문적이며 정보 전달력이 높아야 함.
                   - 마지막에 방문이나 구매를 유도하는 강력한 Call to Action(CTA) 문구를 포함할 것.
                4. cardnews: 4장 구성으로, 각 슬라이드에 들어갈 헤드라인과 구체적인 이미지 추천 내용을 포함할 것.
                5. hashtags: 키워드 경쟁력을 고려해 핵심 키워드와 세부 키워드를 섞어 15개 이상 나열할 것.

                결과는 반드시 아래의 JSON 양식으로만 출력하세요.
                {{
                    "instagram": "내용",
                    "threads": "내용",
                    "blog": "내용",
                    "cardnews": "내용",
                    "hashtags": "내용"
                }}
                """
                
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    response_format={"type": "json_object"}, 
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content_data = json.loads(res.choices[0].message.content)
                
                st.markdown("---")
                
                # 요청하신 대로 화면 분할 없이 세로로 하나씩 큼직하게 배치
                st.write("### 📱 인스타그램")
                st.code(content_data.get("instagram", ""), language="markdown")
                
                st.write("### 🧵 쓰레드(Threads)")
                st.code(content_data.get("threads", ""), language="markdown")
                
                st.write("### 📝 블로그 (Long-form 포스팅)")
                st.code(content_data.get("blog", ""), language="markdown")
                
                st.write("### 🗂️ 카드뉴스 기획안")
                st.code(content_data.get("cardnews", ""), language="markdown")
                
                st.write("### #️⃣ 해시태그 모음")
                st.code(content_data.get("hashtags", ""), language="markdown")
                
                # 히스토리 저장
                st.session_state['history'].append({
                    "날짜": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "브랜드": brand_name,
                    "주제": topic,
                    "결과물 요약": content_data.get("instagram", "")[:30] + "..."
                })
            except Exception as e:
                st.error(f"콘텐츠 생성 중 오류 발생: {e}")