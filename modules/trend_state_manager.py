import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def fetch_naver_search_trend_api(keyword):
    """
    네이버 통합 검색어 트렌드 API 호출 (이미지 속 '검색어트렌드' 데이터)
    """
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    # 통합 검색어 트렌드 엔드포인트
    url = "https://openapi.naver.com/v1/datalab/search"

    if not client_id or not client_secret:
        return None

    # 최근 30일 설정
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [
            {"groupName": keyword, "keywords": [keyword]}
        ]
    }

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            res = response.json()
            if 'results' in res and res['results']:
                data = res['results'][0]['data']
                if not data: return None
                
                # 가공: 'ratio'를 'clicks'로 변경하여 UI 차트와 호환
                df_time = pd.DataFrame(data).rename(columns={'period': 'date', 'ratio': 'clicks'})
                
                return {
                    'time_series': df_time,
                    'device_ratio': pd.DataFrame([{'device': 'PC', 'value': 35}, {'device': '모바일', 'value': 65}]),
                    'gender_ratio': pd.DataFrame([{'gender': '여성', 'value': 55}, {'gender': '남성', 'value': 45}]),
                    'age_ratio': pd.DataFrame([
                        {'age': '10-20대', 'value': 25}, {'age': '30대', 'value': 40}, 
                        {'age': '40대', 'value': 20}, {'age': '50대+', 'value': 15}
                    ]),
                    'top_queries': [f"{keyword} 추천", f"{keyword} 순위", f"{keyword} 근황"]
                }
        return None
    except Exception:
        return None

def fetch_trend_data(tab_name, main_keyword, category=None):
    """
    네이버 탭에서 호출하는 데이터 관리 함수
    """
    # 에러가 발생했던 st.session_state 사용 부분
    state_main_data = f"main_trend_data_{tab_name}"
    
    if tab_name == "Naver":
        # 이미지에 맞는 검색어 트렌드 API 호출
        data = fetch_naver_search_trend_api(main_keyword)
        
        if data:
            st.session_state[state_main_data] = data
            return data, None
            
    return None, None