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
        "패션 및 스타일": ["데일리룩", "오오티디", "패션스타그램", "데일리코디", "옷스타그램"],
        "음식 및 음료": ["먹스타그램", "맛스타그램", "맛집추천", "카페투어", "홈카페"],
        "여행": ["여행스타그램", "국내여행", "해외여행", "여행에미치다", "감성여행"],
        "엔터테인먼트": ["영화추천", "콘서트", "뮤지컬", "넷플릭스추천", "음악추천"],
        "운동 및 건강": ["오운완", "헬스타그램", "운동하는여자", "운동하는남자", "필라테스"],
        "예술 및 디자인": ["전시회추천", "미술관", "홈인테리어", "디자인소품", "그림스타그램"],
        "반려동물": ["멍스타그램", "냥스타그램", "반려견", "댕댕이", "집사그램"],
        "비즈니스 및 기술": ["자기계발", "재테크", "직장인스타그램", "스타트업", "경제공부"]
    }
    return fixed_data.get(category_name, ["실시간 트렌드", "인기 키워드", "추천 검색어"])

# --- 데이터 수집 로직 ---

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

def generate_ai_estimates(keyword, category_name):
    """비중 데이터를 AI로 생성"""
    prompt = f"키워드 '{keyword}'와 카테고리 '{category_name}'의 한국 트렌드 분석 JSON. 형식: {{\"device\": {{\"mo\": 70, \"pc\": 30}}, \"gender\": {{\"f\": 55, \"m\": 45}}, \"age\": {{\"10\": 5, \"20\": 20, \"30\": 25, \"40\": 25, \"50\": 15, \"60\": 10}}}}"
    try:
        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        return json.loads(response.choices[0].message.content)
    except: return None

# --- 메인 통합 함수 ---

def fetch_naver_all_data(keyword, category_id, category_name):
    import random
    result = {
        'time_series': pd.DataFrame(), 'top_queries': [], 
        'device_ratio': None, 'gender_ratio': None, 'age_ratio': None,
        'category_ranking': [], 'region_ranking': pd.DataFrame(), 'faqs': [],
        'hot_discussions': [], 'top_influencers': [], 'x_sentiment': {}
    }

    # 1. 시계열 데이터
    iot = fetch_google_real_trend(keyword)
    if iot is None or iot.empty:
        iot = fetch_naver_search_trend(keyword)
    result['time_series'] = iot if iot is not None else pd.DataFrame()

    # 2. 쇼핑 랭킹 및 비중 데이터
    found_real = False
    if category_id:
        for delay in range(3, 8):
            t_date = (datetime.now() - timedelta(days=delay)).strftime('%Y-%m-%d')
            common_body = {"startDate": t_date, "endDate": t_date, "timeUnit": "date", "category": category_id}
            try:
                # 랭킹 호출
                r_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/keywords", json=common_body, headers=get_naver_headers()).json()
                items = r_res.get('results', [{}])[0].get('data', [])
                if items:
                    result['category_ranking'] = [i.get('name') for i in items][:10]
                    
                    # 비중 호출 (기기)
                    d_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/device", json=common_body, headers=get_naver_headers()).json()
                    d_data = d_res.get('results', [{}])[0].get('data', [])
                    if d_data:
                        result['device_ratio'] = pd.DataFrame(d_data).rename(columns={'group': 'device', 'ratio': 'value'}).replace({'mo': '모바일', 'pc': 'PC'})
                    
                    # 비중 호출 (성별)
                    g_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/gender", json=common_body, headers=get_naver_headers()).json()
                    g_data = g_res.get('results', [{}])[0].get('data', [])
                    if g_data:
                        result['gender_ratio'] = pd.DataFrame(g_data).rename(columns={'group': 'gender', 'ratio': 'value'}).replace({'f': '여성', 'm': '남성'})
                        
                    found_real = True
                    break
            except: continue

    # 3. 데이터 부재 시 AI/고정 데이터로 result 채우기
    if not found_real or result['device_ratio'] is None:
        result['category_ranking'] = get_fixed_category_ranking(category_name)
        ai_val = generate_ai_estimates(keyword, category_name)
        if ai_val:
            result['device_ratio'] = pd.DataFrame([{'device': '모바일', 'value': ai_val['device']['mo']}, {'device': 'PC', 'value': ai_val['device']['pc']}])
            result['gender_ratio'] = pd.DataFrame([{'gender': '여성', 'value': ai_val['gender']['f']}, {'gender': '남성', 'value': ai_val['gender']['m']}])
            result['age_ratio'] = pd.DataFrame([{'age': f"{k}대", 'value': v} for k, v in ai_val['age'].items()])
        else:
            # 완전 실패 시 백업용 더미
            result['device_ratio'] = pd.DataFrame([{'device': '모바일', 'value': 70}, {'device': 'PC', 'value': 30}])
            result['gender_ratio'] = pd.DataFrame([{'gender': '여성', 'value': 55}, {'gender': '남성', 'value': 45}])
            result['age_ratio'] = pd.DataFrame([{'age': f"{i}0대", 'value': random.randint(10, 30)} for i in range(1, 7)])

    # 4. 연관 검색어 (네이버 자동완성)
    import urllib.parse
    encoded = urllib.parse.quote(keyword)
    ac_url = f"https://ac.search.naver.com/nx/ac?q={encoded}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&t_koreng=1&rev=4&q_enc=UTF-8&st=100"
    try:
        ac_res = requests.get(ac_url, timeout=5).json()
        result['top_queries'] = [item[0] for item in ac_res.get('items', [[]])[0]][:10]
    except:
        result['top_queries'] = [f"{keyword} 추천", f"{keyword} 후기", f"{keyword} 순위", f"{keyword} 가격"]

    return result

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_key = f"main_trend_data_{tab_name}"
    cid = get_naver_category_id(category_name)
    data = fetch_naver_all_data(main_keyword, cid, category_name)
    st.session_state[state_key] = data
    return data, data