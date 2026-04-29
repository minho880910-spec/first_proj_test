import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import re
import os
from dotenv import load_dotenv
from pathlib import Path
from modules.keyword_extractor import extract_keyword

current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / "modules" / ".env"
load_dotenv(dotenv_path=env_path)


def get_naver_popular_posts(keyword, client_id, client_secret):
    url = f"https://openapi.naver.com/v1/search/blog?query={keyword}&display=6&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        response = requests.get(url, headers=headers)
        return response.json().get('items', []) if response.status_code == 200 else []
    except: return []

def get_blog_content(url):
    try:
        if "blog.naver.com" in url: url = url.replace("blog.naver.com", "m.blog.naver.com")
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.select_one('.se-main-container')
        return content_div.text.strip()[:1500] if content_div else ""
    except: return ""

def get_blog_comments(url):
    try:
        if "blog.naver.com" not in url: return ""
        match = re.search(r"blogId=(.*?)&logNo=(\d+)", url)
        if not match: return "댓글 없음"
        blog_id, log_no = match.groups()
        comment_url = f"https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=blog&pool=cbox9&lang=ko&country=KR&objectId={blog_id}_{log_no}"
        res = requests.get(comment_url, headers={"Referer": url})
        content = res.text[res.text.find('(')+1 : res.text.rfind(')')]
        data = json.loads(content)
        comments = [c.get('contents') for c in data.get('result', {}).get('commentList', [])[:10]]
        return " | ".join(comments) if comments else "댓글 없음"
    except: return "댓글 수집 불가"

def analyze_with_ai(data_bundle, api_key, platform="NAVER"):
    if not api_key: return "API 키가 없습니다."
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    분석 데이터를 바탕으로 반드시 아래 HTML 구조 '하나'만 출력하세요. 
    마크다운 기호(```)나 추가 설명은 절대 금지합니다.

    <div style="background-color: #f8f9fa; border-radius: 20px; padding: 5px 10px 20px 30px; border: 1px solid #e9ecef;">
        <h2 style="margin: 0 0 10px 0; color: #333; font-size: 1.8rem; font-weight: bold;">🤖 최신 트렌드</h2>
        <ul style="color: #444; line-height: 1.6; font-size: 1.1rem; margin: 0 0 5px 0; padding-left: 20px;">
            <li style="margin-bottom: 5px;">분석 내용 1</li>
            <li style="margin-bottom: 5px;">분석 내용 2</li>
            <li style="margin-bottom: 5px;">분석 내용 3</li>
        </ul>
        <h2 style="margin: 0 0 10px 0; color: #333; font-size: 1.8rem; font-weight: bold;">🤖 Keyword</h2>
        <p style="color: #0366d6; font-weight: bold; font-size: 1.2rem; margin: 0; line-height: 1.4;">
            #키워드1 #키워드2 #키워드3 #키워드4 #키워드5 #키워드6
        </p>
    </div>

    데이터: {data_bundle}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You only output pure HTML tags without backticks."},
                      {"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content
    except: return "분석 중 오류 발생"


def render_sns_section(platform_name, keyword, api_key):
    dummy_bundle = f"{platform_name}에서 '{keyword}' 관련 언급량 급증함."
    with st.spinner(f"{platform_name} 분석 중..."):
        report = analyze_with_ai(dummy_bundle, api_key, platform_name)
        clean_report = report.replace('```html', '').replace('```', '').strip()
        st.markdown(clean_report, unsafe_allow_html=True)
    
    st.write("") 

    def get_platform_dummies(p_name, kw, idx):
        if p_name == "Instagram":
            contents = [
                f"요즘 {kw} 사진 찍는 재미에 빠졌어요✨ 분위기 대박! 역시 이게 대세네요.",
                f"드디어 다녀온 {kw} 핫플! 정보 궁금하시면 DM 주세요 💌 주말 나들이 추천!",
                f"나만 알고 싶은 {kw} 꿀팁 방출📌 이거 하나면 삶의 질 수직 상승. 저장 필수!",
                f"오늘의 {kw} 룩 기록하기👗 날씨랑 너무 잘 어울리는 조합이라 기분 좋네요.",
                f"친구랑 {kw} 챌린지 도전! 생각보다 어렵지만 재밌네요 🙌 같이 해요!",
                f"주말의 마무리는 {kw}와 함께☕ 인친님들 오늘 하루 어떠셨나요? 굿밤!"
            ]
            tags = [
                f"#{kw} #갬성 #daily #인스타무드", f"#{kw} #핫플 #주말데이트 #맛집탐방",
                f"#{kw} #꿀팁 #정보공유 #살림꿀팁", f"#{kw} #OOTD #데일리룩 #감성코디",
                f"#{kw} #챌린지 #운동하는여자 #취미", f"#{kw} #힐링 #카페투어 #소통해요"
            ]
        elif p_name == "Threads":
            contents = [
                f"{kw}에 대해서 다들 어떻게 생각하시나요? 저는 솔직히 이게 더 낫다고 봅니다.. 🧵",
                f"오늘 아침 {kw} 관련해서 겪은 황당한 일 ㅋㅋㅋ 다들 이런 적 있으신가요?",
                f"{kw} 입문자에게 가장 추천하는 조합은 뭔가요? 답변 기다립니다!",
                f"아무도 안 궁금하시겠지만 저 방금 {kw} 결제했습니다. 후기 커밍순.",
                f"{kw} 열풍이 일시적일까요, 아니면 메가 트렌드가 될까요? 제 생각은..",
                f"탐라에 {kw} 관련 글이 많네요. 역시 대세는 대세인가 봅니다."
            ]
            tags = [
                f"#{kw} #스레드 #생각공유 #토론", f"#{kw} #TMI #데일리 #일상썰",
                f"#{kw} #질문 #답변환영 #입문추천", f"#{kw} #내돈내산 #솔직후기 #지름신",
                f"#{kw} #트렌드분석 #메가트렌드 #생각정리", f"#{kw} #실시간공유 #트렌드파악 #소통"
            ]
        else: # X (Twitter)
            contents = [
                f"아니 {kw} 이거 실화냐? 탐라에 이거밖에 안 보임 ㅋㅋㅋㅋ 가보자고~ 🚀",
                f"RT 부탁) {kw} 관련 긴급 제보 받습니다. 아시는 분 타래로 제보 부탁드려요!",
                f"오늘의 국룰: {kw} 즐기면서 트위터 하기. 극락 그 자체임. 반박 불가.",
                f"세상 사람들 다 {kw} 하는데 나만 안 할 수 없지 캠페인 진행 중 (1/100)",
                f"{kw} 때문에 통장 잔고 바닥났지만 후회는 없다. 사랑했다..💸",
                f"{kw} 관련 쩌는 썰 하나 알려줌. 일단 타래로 이어짐 👇"
            ]
            tags = [
                f"#{kw} #실시간트렌드 #국룰 #가보자고", f"#{kw} #정보찾아요 #RT부탁 #제보",
                f"#{kw} #덕질 #극락 #트위터라이프", f"#{kw} #밈 #동참 #실트",
                f"#{kw} #금융치료 #사랑했다 #덕질자금", f"#{kw} #꿀팁 #썰 #타래필독"
            ]
        return contents[idx], tags[idx]

    cols = st.columns(3)
    for i in range(6):
        content, tag = get_platform_dummies(platform_name, keyword, i)
        user_id = f"{platform_name.lower()}_user_{i+101}"
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                border: 1px solid #e1e4e8; padding: 15px; border-radius: 12px; 
                margin-bottom: 8px; background-color: white; min-height: 150px;
                display: flex; flex-direction: column; justify-content: space-between;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.02);">
                <div>
                    <p style="font-size: 0.75rem; color: #888; font-weight: bold; margin-bottom: 5px;">@{user_id}</p>
                    <p style="font-size: 0.85rem; font-weight: 500; line-height:1.4; color: #222; margin-bottom: 5px;">{content}</p>
                </div>
                <p style="color: #0366d6; font-size: 0.75rem; margin: 0;">{tag}</p>
            </div>
            """, unsafe_allow_html=True)


def render_popular():
    st.header("🔥 인기 포스팅")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    c_id, c_secret = os.getenv("NAVER_CLIENT_ID"), os.getenv("NAVER_CLIENT_SECRET")

    prompt_input = st.session_state.get("prompt_input", "").strip()
    if not prompt_input:
        st.info("💡 프롬프트를 입력하면 분석이 시작됩니다.")
        return

    if st.session_state.get("last_prompt_for_keyword") != prompt_input:
        with st.spinner("키워드 분석 중..."):
            st.session_state.extracted_keyword = extract_keyword(prompt_input)
            st.session_state.last_prompt_for_keyword = prompt_input
    
    search_query = st.session_state.get("extracted_keyword", "")

    tab_naver, tab_insta, tab_threads, tab_x = st.tabs(["NAVER", "Instagram", "Threads", "X (Twitter)"])

    with tab_naver:
        if search_query and st.session_state.get("last_query") != search_query:
            with st.spinner(f"🔍 NAVER 분석 중..."):
                items = get_naver_popular_posts(search_query, c_id, c_secret)
                if items:
                    analysis_data = ""
                    processed_items = []
                    for item in items:
                        text, comments = get_blog_content(item['link']), get_blog_comments(item['link'])
                        analysis_data += f"\n제목:{item['title']}\n본문:{text}\n댓글:{comments}\n"
                        processed_items.append({
                            "title": item['title'].replace("<b>","").replace("</b>",""),
                            "author": item['bloggername'], "date": item['postdate'],
                            "desc": item['description'].replace("<b>","").replace("</b>",""), "link": item['link']
                        })
                    st.session_state.popular_summary = analyze_with_ai(analysis_data, openai_key, "NAVER")
                    st.session_state.popular_items = processed_items
                    st.session_state.last_query = search_query

        if "popular_items" in st.session_state:
            summary = st.session_state.popular_summary.replace('```html', '').replace('```', '').strip()
            st.markdown(summary, unsafe_allow_html=True)
            
            st.write("")
            
            cols = st.columns(3)
            for i, item in enumerate(st.session_state.popular_items):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #e1e4e8; padding: 18px; border-radius: 12px; 
                        margin-bottom: 10px; background-color: white; min-height: 260px; 
                        display: flex; flex-direction: column; justify-content: space-between;
                        box-shadow: 1px 1px 5px rgba(0,0,0,0.04);
                    ">
                        <div>
                            <h5 style="margin: 0 0 8px 0; font-size: 0.95rem; color: #1a1a1a; line-height: 1.4;">
                                {i+1}. {item['title']}
                            </h5>
                            <div style="display: flex; align-items: center; gap: 5px; margin-bottom: 8px;">
                                <span style="font-size: 0.8rem;">✍️</span>
                                <span style="font-size: 0.75rem; color: #555; font-weight: bold;">{item['author']}</span>
                                <span style="font-size: 0.75rem; color: #999;">| 📅 {item['date']}</span>
                            </div>
                            <p style="font-size: 0.85rem; color: #666; line-height: 1.5; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; margin-bottom: 8px;">
                                {item['desc']}
                            </p>
                        </div>
                        <div style="margin-top: auto;">
                            <a href="{item['link']}" target="_blank" style="
                                display: inline-block;
                                padding: 5px 12px;
                                background-color: #ffffff;
                                border: 1px solid #ddd;
                                border-radius: 4px;
                                color: #333;
                                text-decoration: none;
                                font-size: 0.75rem;
                                font-weight: bold;
                            ">원본 포스팅 보기</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_insta: render_sns_section("Instagram", search_query, openai_key)
    with tab_threads: render_sns_section("Threads", search_query, openai_key)
    with tab_x: render_sns_section("X", search_query, openai_key)