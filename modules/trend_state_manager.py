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
    mapping = {
        "패션/의류": "50000000", "화장품/뷰티": "50000002", "IT/가전": "50000003",
        "식품/건강": "50000006", "인테리어/가구": "50000004", "여행/숙박": "50000009",
        "게임/엔터": "50000005", "교육/도서": "50000008", "출산/육아": "50000001",
        "반려동물 용품": "50000007", "취미/스포츠": "50000005"
    }
    return mapping.get(category_name, "50000000")

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
    return [f"{keyword} 추천", f"{keyword} 인기", f"{keyword} 순위"]

def fetch_shopping_insight_data(endpoint, body):
    url = f"https://openapi.naver.com/v1/datalab/shopping/category/{endpoint}"
    try:
        response = requests.post(url, json=body, headers=get_naver_headers(), timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def fetch_naver_all_data(keyword, category_id):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    common_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date", "category": category_id}

    # 1. 시계열 검색 추이
    search_url = "https://openapi.naver.com/v1/datalab/search"
    search_body = {
        "startDate": start_date, "endDate": end_date, "timeUnit": "date",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
    }
    res_search = requests.post(search_url, json=search_body, headers=get_naver_headers()).json()
    df_time = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})

    # 2. 기기별 비중 (mo -> 모바일, pc -> PC 변환)
    res_device = fetch_shopping_insight_data("device", common_body)
    if res_device:
        df_device = pd.DataFrame(res_device['results'][0]['data']).rename(columns={'group': 'device', 'ratio': 'value'})
        df_device['device'] = df_device['device'].map({'mo': '모바일', 'pc': 'PC'})
    else:
        df_device = None

    # 3. 성별 비중 (f -> 여성, m -> 남성 변환)
    res_gender = fetch_shopping_insight_data("gender", common_body)
    if res_gender:
        df_gender = pd.DataFrame(res_gender['results'][0]['data']).rename(columns={'group': 'gender', 'ratio': 'value'})
        df_gender['gender'] = df_gender['gender'].map({'f': '여성', 'm': '남성'})
    else:
        df_gender = None

    # 4. 연령별 비중
    res_age = fetch_shopping_insight_data("age", common_body)
    df_age = pd.DataFrame(res_age['results'][0]['data']).rename(columns={'group': 'age', 'ratio': 'value'}) if res_age else None

    # 5. 연관어 및 랭킹
    related = get_naver_related_keywords(keyword)
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