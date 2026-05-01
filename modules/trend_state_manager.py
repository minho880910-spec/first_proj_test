import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_naver_headers():
    return {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
        "Content-Type": "application/json"
    }

def get_naver_category_id(category_name):
    """
    네이버 쇼핑인사이트 표준 카테고리 ID 매핑
    양말, 티셔츠 등 패션 관련 카테고리를 보강했습니다.
    """
    mapping = {
        "패션의류": "50000000",
        "패션잡화": "50000001",
        "화장품/미용": "50000002",
        "디지털/가전": "50000003",
        "가구/인테리어": "50000004",
        "출산/육아": "50000005",
        "식품": "50000006",
        "스포츠/레저": "50000007",
        "생활/건강": "50000008",
        "여가/생활편의": "50000009",
        "면세점": "50000010",
        "도서": "50000011"
    }
    # 분류기 결과에서 공백이나 특수문자 차이가 발생할 수 있으므로 .get()으로 안전하게 가져옴
    return mapping.get(category_name)

def fetch_naver_all_data(keyword, category_id):
    # 1. 공통 데이터 (연관 검색어, 검색 추이)
    from modules.trend_state_manager import get_naver_related_keywords
    related = get_naver_related_keywords(keyword)
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    search_url = "https://openapi.naver.com/v1/datalab/search"
    search_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date",
                   "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]}
    try:
        res_search = requests.post(search_url, json=search_body, headers=get_naver_headers()).json()
        df_time = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except:
        df_time = pd.DataFrame()

    # 2. 결과 구조 초기화
    result = {
        'time_series': df_time, 'top_queries': related,
        'device_ratio': None, 'gender_ratio': None, 'age_ratio': None, 'category_ranking': []
    }

    # 3. 매핑 실패 시 에러 반환
    if not category_id:
        result['error'] = 'mapping_failed'
        return result

    # 4. 쇼핑 데이터 호출
    common_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date", "category": category_id}
    
    def get_data(endpoint):
        url = f"https://openapi.naver.com/v1/datalab/shopping/category/{endpoint}"
        res = requests.post(url, json=common_body, headers=get_naver_headers()).json()
        return res if 'results' in res else None

    # 기기별 (색상 대응을 위해 가공)
    res_dev = get_data("device")
    if res_dev:
        df = pd.DataFrame(res_dev['results'][0]['data']).rename(columns={'group': 'device', 'ratio': 'value'})
        df['device'] = df['device'].replace({'mo': '모바일', 'pc': 'PC'})
        result['device_ratio'] = df

    # 성별 (색상 대응을 위해 가공)
    res_gen = get_data("gender")
    if res_gen:
        df = pd.DataFrame(res_gen['results'][0]['data']).rename(columns={'group': 'gender', 'ratio': 'value'})
        df['gender'] = df['gender'].replace({'f': '여성', 'm': '남성'})
        result['gender_ratio'] = df

    # 연령별
    res_age = get_data("age")
    if res_age:
        result['age_ratio'] = pd.DataFrame(res_age['results'][0]['data']).rename(columns={'group': 'age', 'ratio': 'value'})

    # 카테고리 인기 검색어 랭킹
    res_rank = get_data("keywords")
    if res_rank:
        result['category_ranking'] = [item['name'] for item in res_rank['results'][0]['data'][:10]]

    return result