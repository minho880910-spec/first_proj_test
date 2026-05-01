import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def get_naver_headers():
    return {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
        "Content-Type": "application/json"
    }

def get_naver_category_id(category_name):
    """
    네이버 쇼핑인사이트 표준 카테고리 매핑
    매핑되지 않은 경우 None을 반환합니다.
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
    return mapping.get(category_name) # 매핑 없으면 None 반환

def get_naver_related_keywords(keyword):
    import urllib.parse
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://ac.search.naver.com/nx/ac?q={encoded_keyword}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&q_enc=UTF-8&st=100"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                return [item[0] for item in items[0]][:10]
    except:
        pass
    return []

def fetch_shopping_insight_data(endpoint, body):
    url = f"https://openapi.naver.com/v1/datalab/shopping/category/{endpoint}"
    try:
        response = requests.post(url, json=body, headers=get_naver_headers(), timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def fetch_naver_all_data(keyword, category_id):
    """카테고리 ID가 없으면 빈 데이터를 반환합니다."""
    # 1. 연관 검색어는 카테고리와 무관하게 먼저 추출
    related = get_naver_related_keywords(keyword)

    # 2. 카테고리 ID가 없는 경우(매핑 실패) 조기 종료
    if not category_id:
        return {
            'time_series': pd.DataFrame(),
            'device_ratio': None,
            'gender_ratio': None,
            'age_ratio': None,
            'top_queries': related,
            'category_ranking': []
        }

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    common_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date", "category": category_id}

    # 시계열 검색 추이
    search_url = "https://openapi.naver.com/v1/datalab/search"
    search_body = {
        "startDate": start_date, "endDate": end_date, "timeUnit": "date",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
    }
    try:
        res_search = requests.post(search_url, json=search_body, headers=get_naver_headers()).json()
        df_time = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except:
        df_time = pd.DataFrame()

    # 인구통계 및 랭킹 데이터 호출
    res_device = fetch_shopping_insight_data("device", common_body)
    df_device = pd.DataFrame(res_device['results'][0]['data']).rename(columns={'group': 'device', 'ratio': 'value'}) if res_device else None
    if df_device is not None:
        df_device['device'] = df_device['device'].replace({'mo': '모바일', 'pc': 'PC'})

    res_gender = fetch_shopping_insight_data("gender", common_body)
    df_gender = pd.DataFrame(res_gender['results'][0]['data']).rename(columns={'group': 'gender', 'ratio': 'value'}) if res_gender else None
    if df_gender is not None:
        df_gender['gender'] = df_gender['gender'].replace({'f': '여성', 'm': '남성'})

    res_age = fetch_shopping_insight_data("age", common_body)
    df_age = pd.DataFrame(res_age['results'][0]['data']).rename(columns={'group': 'age', 'ratio': 'value'}) if res_age else None

    res_rank = fetch_shopping_insight_data("keywords", common_body)
    top_rank = [item['name'] for item in res_rank['results'][0]['data'][:10]] if res_rank else []

    return {
        'time_series': df_time, 'device_ratio': df_device, 'gender_ratio': df_gender,
        'age_ratio': df_age, 'top_queries': related, 'category_ranking': top_rank
    }

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_main_data = f"main_trend_data_{tab_name}"
    if tab_name == "Naver":
        category_id = get_naver_category_id(category_name)
        data = fetch_naver_all_data(main_keyword, category_id)
        if data:
            st.session_state[state_main_data] = data
            return data, data
    return None, None