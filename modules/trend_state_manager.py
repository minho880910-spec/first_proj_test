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
    # 네이버 탭 등에서 직접 전달되는 카테고리 명칭 기준 매핑
    mapping = {
        "패션의류": "50000000", "패션잡화": "50000001", "화장품/미용": "50000002",
        "디지털/가전": "50000003", "가구/인테리어": "50000004", "출산/육아": "50000005",
        "식품": "50000006", "스포츠/레저": "50000007", "생활/건강": "50000008",
        "여가/생활편의": "50000009", "면세점": "50000010", "도서": "50000011"
    }
    return mapping.get(category_name)

def get_fixed_category_ranking(category_name):
    """사이드바와 무관하게, 내부 탭에서 선택된 카테고리명 기반으로 고정 데이터 반환"""
    fixed_data = {
        # --- 네이버 스타일 카테고리 데이터 ---
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
        "면세점": [],  # 면세점은 빈 리스트 반환
        "도서": ["포켓몬생태도감", "베스트셀러", "흔한남매22", "자몽살구클럽", "안녕이라그랬어", "프로젝트헤일메리책", "열혈강호95권", "위버멘쉬", "엄마가유령이되었어", "니체의초월자"],
        
        # --- 인스타그램 스타일 카테고리 데이터 ---
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

# --- 메인 통합 함수 ---

def fetch_naver_all_data(keyword, category_id, category_name):
    result = {
        'time_series': pd.DataFrame(), 'top_queries': [], 
        'device_ratio': None, 'gender_ratio': None, 'age_ratio': None,
        'category_ranking': [], 'region_ranking': pd.DataFrame(), 'faqs': [],
        'hot_discussions': [], 'top_influencers': [], 'x_sentiment': {}
    }

    # 1. 시계열 데이터 (구글 우선 -> 네이버 백업)
    iot = fetch_google_real_trend(keyword)
    if iot is None or iot.empty:
        iot = fetch_naver_search_trend(keyword)
    result['time_series'] = iot if iot is not None else pd.DataFrame()

    # 2. 쇼핑 랭킹 데이터 (실데이터 시도 -> 부재 시 고정 리스트)
    found_real = False
    if category_id:
        for delay in range(3, 8):
            t_date = (datetime.now() - timedelta(days=delay)).strftime('%Y-%m-%d')
            common_body = {"startDate": t_date, "endDate": t_date, "timeUnit": "date", "category": category_id}
            try:
                r_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/keywords", json=common_body, headers=get_naver_headers()).json()
                items = r_res.get('results', [{}])[0].get('data', [])
                if items:
                    result['category_ranking'] = [i.get('name') for i in items][:10]
                    found_real = True
                    break
            except: continue

    if not found_real:
        # 사이드바와 연동하지 않고, 현재 탭에서 들어온 category_name으로 직접 고정 데이터 매칭
        result['category_ranking'] = get_fixed_category_ranking(category_name)

    return result

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_key = f"main_trend_data_{tab_name}"
    # 탭 내부에서 전달된 category_name을 사용하여 ID 추출
    cid = get_naver_category_id(category_name)
    data = fetch_naver_all_data(main_keyword, cid, category_name)
    st.session_state[state_key] = data
    return data, data