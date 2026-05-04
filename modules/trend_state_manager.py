import pandas as pd
import streamlit as st
import requests
from datetime import datetime, timedelta
from .api_clients import (
    fetch_google_real_trend, fetch_naver_search_trend, 
    fetch_naver_autocomplete, get_naver_headers
)
from .ai_generators import get_comprehensive_analysis

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
        "패션의류": ["원피스", "바람막이", "블라우스"],
        "디지털/가전": ["냉장고", "노트북", "모니터"],
        "면세점": [],
        # ... (이전 고정 데이터 리스트 유지)
    }
    return fixed_data.get(category_name, ["실시간 트렌드", "인기 키워드"])

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_key = f"main_trend_data_{tab_name}"
    
    # 1. 기본 구조 설정
    result = {
        'time_series': pd.DataFrame(), 'top_queries': fetch_naver_autocomplete(main_keyword),
        'device_ratio': None, 'gender_ratio': None, 'age_ratio': None,
        'category_ranking': [], 'region_ranking': pd.DataFrame(), 'faqs': [],
        'hot_discussions': [], 'top_influencers': [], 'x_sentiment': {}
    }

    # 2. 시계열 (구글 -> 네이버)
    iot = fetch_google_real_trend(main_keyword)
    if iot is None or iot.empty:
        iot = fetch_naver_search_trend(main_keyword)
    result['time_series'] = iot if iot is not None else pd.DataFrame()

    # 3. AI 분석 통합 호출
    ai_data = get_comprehensive_analysis(main_keyword, category_name)
    if ai_data:
        result['region_ranking'] = pd.DataFrame(ai_data.get('region_ranking', []))
        result['faqs'] = ai_data.get('faqs', [])
        result['hot_discussions'] = ai_data.get('hot_discussions', [])
        result['top_influencers'] = ai_data.get('top_influencers', [])
        result['x_sentiment'] = ai_res = ai_data.get('x_sentiment', {})
        
        # 비중 데이터 (AI 예측값 주입)
        demos = ai_data.get('demographics', {})
        result['device_ratio'] = pd.DataFrame([{'device': '모바일', 'value': demos['device']['mo']}, {'device': 'PC', 'value': demos['device']['pc']}])
        result['gender_ratio'] = pd.DataFrame([{'gender': '여성', 'value': demos['gender']['f']}, {'gender': '남성', 'value': demos['gender']['m']}])
        result['age_ratio'] = pd.DataFrame([{'age': f"{k}대", 'value': v} for k, v in demos['age'].items()])

    # 4. 네이버 쇼핑 실데이터 시도 (성공 시 위 AI 비중 데이터를 덮어씀)
    cid = get_naver_category_id(category_name)
    if cid:
        for delay in range(3, 7):
            t_date = (datetime.now() - timedelta(days=delay)).strftime('%Y-%m-%d')
            headers = get_naver_headers()
            body = {"startDate": t_date, "endDate": t_date, "timeUnit": "date", "category": cid}
            try:
                rk_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/keywords", json=body, headers=headers).json()
                items = rk_res.get('results', [{}])[0].get('data', [])
                if items:
                    result['category_ranking'] = [i.get('name') for i in items][:10]
                    break
            except: continue

    if not result['category_ranking']:
        result['category_ranking'] = get_fixed_category_ranking(category_name)

    st.session_state[state_key] = result
    return result, result