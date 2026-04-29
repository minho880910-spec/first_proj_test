import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import re
import os
from dotenv import load_dotenv
from pathlib import Path

# --- 1. 환경 변수 설정 ---
current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / "modules" / ".env"
load_dotenv(dotenv_path=env_path)

# --- 2. 데이터 수집 함수 (텍스트 데이터만 집중) ---

def get_naver_popular_posts(keyword, client_id, client_secret):
    """네이버 검색 API로 목록 수집"""
    url = f"https://openapi.naver.com/v1/search/blog?query={keyword}&display=5&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        response = requests.get(url, headers=headers)
        return response.json().get('items', []) if response.status_code == 200 else []
    except:
        return []

def get_blog_content(url):
    """본문 텍스트 크롤링 (이미지 로직 완전 제거)"""
    try:
        if "blog.naver.com" in url:
            url = url.replace("blog.naver.com", "m.blog.naver.com")
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.select_one('.se-main-container')
        return content_div.text.strip()[:1500] if content_div else ""
    except:
        return ""

def get_blog_comments(url):
    """댓글 수집"""
    try:
        if "blog.naver.com" not in url: return ""
        match = re.search(r"blogId=(.*?)&logNo=(\d+)", url)
        if not match:
            parts = url.split('/')
            blog_id = parts[-2] if "m.blog" not in url else parts[-1].split('?')[0]
            log_no = parts[-1].split('?')[0]
        else:
            blog_id, log_no = match.groups()
        
        comment_url = f"https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=blog&pool=cbox9&lang=ko&country=KR&objectId={blog_id}_{log_no}"
        res = requests.get(comment_url, headers={"Referer": url})
        content = res.text[res.text.find('(')+1 : res.text.rfind(')')]
        data = json.loads(content)
        comments = [c.get('contents') for c in data.get('result', {}).get('commentList', [])[:10]]
        return " | ".join(comments) if comments else "댓글 없음"
    except:
        return "댓글 수집 불가"

def analyze_with_ai(data_bundle, api_key):
    """AI 트렌드 분석"""
    if not api_key: return "API 키가 없습니다."
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 블로그 트렌드 분석가입니다."},
                {"role": "user", "content": f"다음 블로그들의 본문과 댓글을 바탕으로 트렌드를 4~5줄 요약하고, 치트키 키워드도 알려줘:\n\n{data_bundle}"}
            ]
        )
        return response.choices[0].message.content
    except:
        return "AI 분석 중 오류가 발생했습니다."

# --- 3. 메인 렌더링 함수 ---

def render_popular():
    st.header("✨ 네이버 인기 포스팅 & AI 분석")
    st.write("인기 포스팅 5개를 수집하고 AI가 본문과 댓글을 정밀 분석합니다.")

    # API 키 로드
    c_id = os.getenv("NAVER_CLIENT_ID")
    c_secret = os.getenv("NAVER_CLIENT_SECRET")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not all([c_id, c_secret, openai_key]):
        st.error("⚠️ .env 파일의 API 키 설정을 확인해주세요.")
        return

    # 검색창 레이아웃
    search_query = st.session_state.get("prompt_input", "").strip()
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        search_input = st.text_input("검색할 키워드", value=search_query, key="no_img_pop_input", label_visibility="collapsed")
    with col_btn:
        if st.button("다시 검색", use_container_width=True):
            st.session_state.last_query = ""
            st.rerun()

    # 검색 처리
    if search_input and st.session_state.get("last_query") != search_input:
        with st.spinner(f"🔍 '{search_input}'의 본문과 댓글을 분석 중입니다..."):
            items = get_naver_popular_posts(search_input, c_id, c_secret)
            
            if items:
                analysis_data = ""
                processed_items = []
                for item in items:
                    text = get_blog_content(item['link'])
                    comments = get_blog_comments(item['link'])
                    analysis_data += f"\n제목:{item['title']}\n본문:{text}\n댓글:{comments}\n"
                    
                    processed_items.append({
                        "title": item['title'].replace("<b>","").replace("</b>",""),
                        "author": item['bloggername'],
                        "date": item['postdate'],
                        "desc": item['description'].replace("<b>","").replace("</b>",""),
                        "link": item['link']
                    })
                
                # 분석 결과 저장
                st.session_state.popular_summary = analyze_with_ai(analysis_data, openai_key)
                st.session_state.popular_items = processed_items
                st.session_state.last_query = search_input
            else:
                st.warning("검색 결과가 없습니다.")

    # 결과 출력 (이미지 없이 텍스트 카드 스타일)
    if "popular_items" in st.session_state:
        st.divider()
        if "popular_summary" in st.session_state:
            st.subheader("🤖 AI 트렌드 & 반응 분석")
            st.info(st.session_state.popular_summary)
        
        st.subheader(f"🔍 '{st.session_state.last_query}' 관련 인기글 Top 5")
        for i, item in enumerate(st.session_state.popular_items):
            with st.container():
                st.markdown(f"#### {i+1}. {item['title']}")
                st.caption(f"✍️ {item['author']} | 📅 {item['date']}")
                st.write(f"{item['desc']}...")
                st.link_button("원본 포스팅 보기", item['link'])
                st.write("") # 간격
                st.divider()