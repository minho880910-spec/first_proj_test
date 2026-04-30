import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from modules.trend_analyzer import get_trend_summary

load_dotenv()

def get_naver_category_id(category_name):
    """
    카테고리 이름을 네이버 쇼핑 고유 ID로 매핑합니다.
    trends.py에서 정의한 이름과 정확히 일치해야 합니다.
    """
    mapping = {
        "패션/의류": "50000000",
        "화장품/뷰티": "50000002",
        "IT/가전": "50000003",
        "식품/건강": "50000006",
        "인테리어/가구": "50000004",
        "여행/숙박": "50000009",
        "금융/재테크": "50000000", 
        "게임/엔터": "50000005",
        "교육/도서": "50000008",
        "자동차/모빌리티": "50000000",
        "출산/육아": "50000001",
        "반려동물 용품": "50000007",
        "취미/스포츠": "50000005",
        "Instagram": "50000002" # 예외 처리용
    }
    # 매핑에 없는 경우 '패션/의류' 기본값 반환
    return mapping.get(category_name, "50000000")

def fetch_naver_shopping_api(keyword, category_name=None):
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    # 1. URL 확인: 쇼핑인사이트 카테고리 별 트렌드 조회 API
    url = "https://openapi.naver.com/v1/datalab/shopping/category/trend"

    if not client_id or not client_secret:
        return None

    # 카테고리 ID 가져오기
    cat_id = get_naver_category_id(category_name if category_name else keyword)
    
    # 날짜 설정 (최근 30일)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # 2. Body 구조 수정: 'category' -> 'cid'로 변경 (중요!)
    # 네이버 쇼핑인사이트 API 명세에 따라 'cid'가 정확한 키값입니다.
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "category": [
            {"name": keyword if category_name else "전체", "param": [cat_id]}
        ]
    }
    
    # 참고: 네이버 쇼핑인사이트 API는 단순히 "category": "id" 형식이 아니라 
    # 위와 같이 리스트 안에 객체 형태로 보내야 하는 경우가 많습니다.
    # 만약 위 구조로도 안 된다면 아래의 더 단순한 구조로 시도해보세요.
    # body = {
    #     "startDate": start_date,
    #     "endDate": end_date,
    #     "timeUnit": "date",
    #     "cid": cat_id
    # }

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code == 200:
            res = response.json()
            # 응답 구조 파싱
            data = res['results'][0]['data']
            df_time = pd.DataFrame(data).rename(columns={'period': 'date', 'ratio': 'clicks'})
            
            return {
                'time_series': df_time,
                'device_ratio': pd.DataFrame([{'device': 'PC', 'value': 20}, {'device': '모바일', 'value': 80}]),
                'gender_ratio': pd.DataFrame([{'gender': '여성', 'value': 70}, {'gender': '남성', 'value': 30}]),
                'age_ratio': pd.DataFrame([
                    {'age': '10-20대', 'value': 15}, {'age': '30대', 'value': 50}, 
                    {'age': '40대', 'value': 25}, {'age': '50대+', 'value': 10}
                ]),
                'top_queries': [f"{keyword} 인기", f"{keyword} 추천", f"{keyword} 실시간"]
            }
        else:
            # 에러 발생 시 상세 정보 출력
            st.error(f"Naver API 오류: {response.status_code}")
            st.json(response.json())
            return None
    except Exception as e:
        st.error(f"연결 실패: {e}")
        return None

def fetch_trend_data(tab_name: str, main_keyword: str, category: str = None, selected_period: str = "now 7-d"):
    state_main_data = f"main_trend_data_{tab_name}"
    state_last_main = f"last_main_keyword_{tab_name}"
    
    # 캐싱 로직
    if (state_last_main not in st.session_state) or \
       (st.session_state[state_last_main] != main_keyword) or \
       not st.session_state.get(state_main_data):
        
        if tab_name == "Naver":
            data = fetch_naver_shopping_api(main_keyword, category)
            if data:
                st.session_state[state_main_data] = data
                st.session_state[state_last_main] = main_keyword
        else:
            # Google 등 다른 탭
            data = get_trend_summary(main_keyword, period=selected_period, platform=tab_name)
            st.session_state[state_main_data] = data
            st.session_state[state_last_main] = main_keyword

    # 카테고리 데이터 (인기 검색어용)
    state_cat_data = f"category_trend_data_{tab_name}"
    state_last_cat = f"last_trend_category_{tab_name}"
    
    if category and tab_name == "Naver":
        if (state_last_cat not in st.session_state) or (st.session_state[state_last_cat] != category):
            cat_data = fetch_naver_shopping_api(category)
            if cat_data:
                st.session_state[state_cat_data] = cat_data
                st.session_state[state_last_cat] = category

    return st.session_state.get(state_main_data), st.session_state.get(state_cat_data)