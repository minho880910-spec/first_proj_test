import os
import json
import requests
import pandas as pd
import streamlit as st
from openai import OpenAI
from pytrends.request import TrendReq
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- [기본 설정 및 헤더] ---
def get_naver_headers():
    return {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
        "Content-Type": "application/json"
    }

def get_naver_category_id(category_name):
    mapping = {
        "패션의류": "50000000", "패션잡화": "50000001", "화장품/미용": "50000002",
        "디지털/가전": "50000003", "가구/인테리어": "50000004", "출산/육아": "50000005",
        "식품": "50000006", "스포츠/레저": "50000007", "생활/건강": "50000008",
        "여가/생활편의": "50000009", "면세점": "50000010", "도서": "50000011"
    }
    return mapping.get(category_name)

def get_fixed_category_ranking(category_name):
    """API 데이터 부재 시 출력할 플랫폼별 고정 데이터 리스트"""
    fixed_data = {
        "패션의류": ["원피스", "바람막이", "블라우스", "티셔츠", "올리비아로렌", "에고이스트", "남자반팔티", "잇미샤원피스", "럭키슈에뜨", "써스데이아일랜드"],
        "패션잡화": ["크록스", "슬리퍼", "나이키운동화", "양산", "백팩", "운동화", "크로스백", "안전화", "뉴발란스운동화", "아디다스운동화"],
        "화장품/미용": ["ahc아이크림", "선스틱", "헤라블랙쿠션", "선크림", "마데카크림", "설화수", "아모스컬링에센스", "세포랩", "샴푸", "썬크림"],
        "디지털/가전": ["냉장고", "노트북", "닌텐도스위치2", "모니터", "선풍기", "공기청정기", "제습기", "무선청소기", "음식물처리기", "키캡"],
        "가구/인테리어": ["화장대", "쇼파", "식탁의자", "침대프레임", "침대", "책상", "앞치마", "책상의자", "행거", "서랍장"],
        "출산/육아": ["레고", "포켓몬카드", "물티슈", "크록스키즈", "어린이날선물", "카네이션만들기", "키즈바람막이", "베베드피노", "돌반지", "다마고치"],
        "식품": ["쌀20kg", "닭가슴살", "오메가3", "쌀10kg", "마늘쫑", "참외", "창억떡", "콜라겐", "사과", "마그네슘"],
        "스포츠/레저": ["전기자전거", "등산화", "자전거", "트레킹화", "캠핑의자", "로드자전거", "원터치텐트", "파라솔", "자외선차단마스크", "무릎보호대"],
        "생활/건강": ["텀블러", "요소수", "스타벅스텀블러", "비데", "강아지사료", "빨래건조대", "어버이날이벤트", "카네이션", "식기건조대", "도시락통"],
        "여가/생활편의": ["부산요트투어", "대마도배편", "카네이션생화", "구글기프트카드", "혜화연극", "신세계상품권", "본죽메뉴", "이월드자유이용권", "크루즈여행", "메가커피메뉴"],
        "면세점": [],
        "도서": ["포켓몬생태도감", "베스트셀러", "흔한남매22", "자몽살구클럽", "안녕이라그랬어", "프로젝트헤일메리책", "열혈강호95권", "위버멘쉬", "엄마가유령이되었어", "니체의초월자"],
        "패션 및 스타일": ["데일리룩", "오오티디", "패션스타그램", "데일리코디", "옷스타그램", "패션피플", "스타일링", "봄코디", "여름코디", "인플루언서"],
        "음식 및 음료": ["먹스타그램", "맛스타그램", "맛집추천", "카페투어", "홈카페", "오늘뭐먹지", "집밥스타그램", "디저트카페", "야식추천", "베이커리"],
        "여행": ["여행스타그램", "국내여행", "해외여행", "여행에미치다", "감성여행", "호캉스", "제주여행", "여행사진", "바다여행", "가족여행"],
        "엔터테인먼트": ["영화추천", "콘서트", "뮤지컬", "넷플릭스추천", "음악추천", "덕질스타그램", "공연스타그램", "정주행", "문화생활", "팬스타그램"],
        "운동 및 건강": ["오운완", "헬스타그램", "운동하는여자", "운동하는남자", "필라테스", "바디프로필", "다이어트식단", "유지어터", "등산스타그램", "건강관리"],
        "예술 및 디자인": ["전시회추천", "미술관", "홈인테리어", "디자인소품", "그림스타그램", "감성사진", "인테리어그램", "예술가", "방꾸미기", "드로잉"],
        "반려동물": ["멍스타그램", "냥스타그램", "반려견", "댕댕이", "집사그램", "강아지사료", "고양이집사", "반려묘", "강아지옷", "멍팔"],
        "비즈니스 및 기술": ["자기계발", "재테크", "직장인스타그램", "스타트업", "경제공부", "신제품리뷰", "애플", "갤럭시", "데스크테리어", "마케팅트렌드"]
    }
    return fixed_data.get(category_name, ["실시간 트렌드", "인기 키워드", "추천 검색어"])

# --- [데이터 수집 엔진] ---

def fetch_google_real_trend(keyword, period='today 1-m'):
    try:
        pytrend = TrendReq(hl='ko-KR', tz=540)
        pytrend.build_payload(kw_list=[keyword], timeframe=period, geo='KR')
        iot = pytrend.interest_over_time()
        if not iot.empty:
            iot = iot.reset_index()
            iot.rename(columns={'date': 'date', keyword: 'clicks'}, inplace=True)
            iot['date'] = iot['date'].dt.strftime('%Y-%m-%d')
            return iot[['date', 'clicks']]
    except: return None

def fetch_naver_search_trend(keyword):
    try:
        end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=32)).strftime('%Y-%m-%d')
        body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date", "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]}
        res = requests.post("https://openapi.naver.com/v1/datalab/search", json=body, headers=get_naver_headers()).json()
        return pd.DataFrame(res['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except: return None

def generate_ai_data(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except: return None

# --- [메인 데이터 통합 로직] ---

def fetch_naver_all_data(keyword, category_id, category_name):
    import random
    result = {
        'time_series': pd.DataFrame(), 'top_queries': [], 
        'device_ratio': None, 'gender_ratio': None, 'age_ratio': None,
        'category_ranking': [], 'region_ranking': pd.DataFrame(), 'faqs': [],
        'hot_discussions': [], 'top_influencers': [], 'x_sentiment': {}
    }

    # 1. 시계열 (구글 우선 -> 네이버 백업)
    iot = fetch_google_real_trend(keyword)
    if iot is None or iot.empty:
        iot = fetch_naver_search_trend(keyword)
    result['time_series'] = iot if iot is not None else pd.DataFrame()

    # 2. 구글/스레드/X 전용 AI 데이터 (FAQ, 지역, 감성 등)
    ai_prompt = f"키워드 '{keyword}' 분석. 1.한국지역관심도(5곳 score 0-100), 2.FAQ 5개, 3.Threads게시물 3개&인플루언서 5명, 4.X감성통계(4개비중)&감성단어&팁3개. JSON형식으로."
    ai_res = generate_ai_data(ai_prompt)
    if ai_res:
        result['region_ranking'] = pd.DataFrame(ai_res.get('region_ranking', [{'region':'서울','score':100}]))
        result['faqs'] = ai_res.get('faqs', [])
        result['hot_discussions'] = ai_res.get('hot_discussions', [])
        result['top_influencers'] = ai_res.get('top_influencers', [])
        result['x_sentiment'] = ai_res
    else:
        result['faqs'] = [f"{keyword} 추천", f"{keyword} 정보"]

    # 3. 네이버 쇼핑 및 비중 데이터
    found_real_shopping = False
    if category_id:
        for delay in range(3, 8):
            t_date = (datetime.now() - timedelta(days=delay)).strftime('%Y-%m-%d')
            body = {"startDate": t_date, "endDate": t_date, "timeUnit": "date", "category": category_id}
            try:
                # 랭킹 및 비중 호출
                rk_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/keywords", json=body, headers=get_naver_headers()).json()
                items = rk_res.get('results', [{}])[0].get('data', [])
                if items:
                    result['category_ranking'] = [i.get('name') for i in items][:10]
                    # 기기/성별 비중 호출
                    d_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/device", json=body, headers=get_naver_headers()).json()
                    g_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/gender", json=body, headers=get_naver_headers()).json()
                    
                    d_data = d_res.get('results', [{}])[0].get('data', [])
                    if d_data:
                        result['device_ratio'] = pd.DataFrame(d_data).rename(columns={'group': 'device', 'ratio': 'value'}).replace({'mo': '모바일', 'pc': 'PC'})
                    
                    g_data = g_res.get('results', [{}])[0].get('data', [])
                    if g_data:
                        result['gender_ratio'] = pd.DataFrame(g_data).rename(columns={'group': 'gender', 'ratio': 'value'}).replace({'f': '여성', 'm': '남성'})
                    
                    found_real_shopping = True
                    break
            except: continue

    # 4. 쇼핑 데이터 부재 시 AI 예측 및 고정 데이터 주입
    if not found_real_shopping:
        result['category_ranking'] = get_fixed_category_ranking(category_name)
        ratio_ai = generate_ai_data(f"'{keyword}'와 '{category_name}'의 한국 기기/성별/연령(10-60대) 비중 JSON")
        if ratio_ai:
            result['device_ratio'] = pd.DataFrame([{'device': '모바일', 'value': 70}, {'device': 'PC', 'value': 30}])
            result['gender_ratio'] = pd.DataFrame([{'gender': '여성', 'value': 55}, {'gender': '남성', 'value': 45}])
            result['age_ratio'] = pd.DataFrame([{'age': f"{k}대", 'value': v} for k, v in ratio_ai.get('age', {}).items()])
        else:
            result['device_ratio'] = pd.DataFrame([{'device': '모바일', 'value': 70}, {'device': 'PC', 'value': 30}])
            result['gender_ratio'] = pd.DataFrame([{'gender': '여성', 'value': 50}, {'gender': '남성', 'value': 50}])
            result['age_ratio'] = pd.DataFrame([{'age': f"{i}0대", 'value': 20} for i in range(1, 7)])

    # 5. 연관 검색어 (네이버 자동완성)
    import urllib.parse
    try:
        encoded = urllib.parse.quote(keyword)
        ac_res = requests.get(f"https://ac.search.naver.com/nx/ac?q={encoded}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&t_koreng=1&rev=4&q_enc=UTF-8&st=100", timeout=5).json()
        result['top_queries'] = [item[0] for item in ac_res.get('items', [[]])[0]][:10]
    except:
        result['top_queries'] = [f"{keyword} 추천", f"{keyword} 정보"]

    return result

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_key = f"main_trend_data_{tab_name}"
    cid = get_naver_category_id(category_name)
    data = fetch_naver_all_data(main_keyword, cid, category_name)
    st.session_state[state_key] = data
    return data, data