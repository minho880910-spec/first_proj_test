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

def fetch_shopping_insight_data(endpoint, body):
    """네이버 쇼핑인사이트 공통 호출 함수"""
    url = f"https://openapi.naver.com/v1/datalab/shopping/category/{endpoint}"
    try:
        response = requests.post(url, json=body, headers=get_naver_headers(), timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Shopping Insight API Error ({endpoint}): {e}")
    return None

def fetch_naver_all_data(keyword, category_id):
    """검색어 트렌드 + 쇼핑인사이트 인구통계 + 카테고리 랭킹 통합 호출"""
    
    # 기본 설정
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    common_body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "category": category_id
    }

    # 1. 시계열 검색어 트렌드 (통합 검색어 API)
    search_url = "https://openapi.naver.com/v1/datalab/search"
    search_body = {
        "startDate": start_date, "endDate": end_date, "timeUnit": "date",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
    }
    
    res_search = requests.post(search_url, json=search_body, headers=get_naver_headers()).json()
    df_time = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})

    # 2. 기기별 비중 API
    res_device = fetch_shopping_insight_data("device", common_body)
    df_device = pd.DataFrame(res_device['results'][0]['data']).rename(columns={'group': 'device', 'ratio': 'value'}) if res_device else None

    # 3. 성별 비중 API
    res_gender = fetch_shopping_insight_data("gender", common_body)
    df_gender = pd.DataFrame(res_gender['results'][0]['data']).rename(columns={'group': 'gender', 'ratio': 'value'}) if res_gender else None

    # 4. 연령별 비중 API
    res_age = fetch_shopping_insight_data("age", common_body)
    df_age = pd.DataFrame(res_age['results'][0]['data']).rename(columns={'group': 'age', 'ratio': 'value'}) if res_age else None

    # 5. 연관 검색어 (자동완성 활용)
    from modules.trend_state_manager import get_naver_related_keywords
    related_queries = get_naver_related_keywords(keyword)

    # 6. 카테고리 내 인기 검색어 랭킹 (키워드 응답 구조 활용)
    res_rank = fetch_shopping_insight_data("keywords", common_body)
    top_rank = [item['name'] for item in res_rank['results'][0]['data'][:10]] if res_rank else []

    return {
        'time_series': df_time,
        'device_ratio': df_device,
        'gender_ratio': df_gender,
        'age_ratio': df_age,
        'top_queries': related_queries,
        'category_ranking': top_rank
    }

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_main_data = f"main_trend_data_{tab_name}"
    
    # 카테고리 이름으로 ID 매핑 (기존 get_naver_category_id 함수 활용)
    from modules.trend_state_manager import get_naver_category_id
    category_id = get_naver_category_id(category_name)

    if tab_name == "Naver":
        data = fetch_naver_all_data(main_keyword, category_id)
        if data:
            st.session_state[state_main_data] = data
            return data, data # 두 번째 인자는 카테고리 랭킹용 데이터
    return None, None