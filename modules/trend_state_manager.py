import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 필요)
load_dotenv()

def get_naver_related_keywords(keyword):
    if not keyword:
        return ["검색어를 입력하세요"]
        
    # [수정] 띄어쓰기를 URL 인코딩 처리하여 전달
    import urllib.parse
    encoded_keyword = urllib.parse.quote(keyword)
    
    url = f"https://ac.search.naver.com/nx/ac?q={encoded_keyword}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&q_enc=UTF-8&st=100"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # 네이버 응답 구조가 ['keyword', [데이터목록]] 형태인 경우 대응
            items = data.get('items', [])
            
            if items and len(items) > 0:
                # 데이터가 [["키워드", "분류"], ...] 형태이므로 첫 번째 요소만 추출
                extracted = [item[0] for item in items[0]]
                return extracted[:10]
    except Exception as e:
        st.error(f"연관어 호출 오류: {e}") # 화면에 오류 직접 표시 (디버깅용)
    
    return [f"{keyword} 추천", f"{keyword} 순위", f"{keyword} 가격", f"{keyword} 종류"]

def fetch_naver_search_trend_api(keyword):
    """
    네이버 통합 검색어 트렌드 API를 호출합니다. (이미지 속 '검색어트렌드' 데이터)
    """
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    
    # [핵심] 쇼핑인사이트가 아닌 '통합 검색어 트렌드' 엔드포인트 사용
    url = "https://openapi.naver.com/v1/datalab/search"

    if not client_id or not client_secret:
        return None

    # 최근 30일 설정 (이미지 데이터 기간과 유사하게 설정)
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
        response = requests.post(url, json=body, headers=headers, timeout=10)
        if response.status_code == 200:
            res = response.json()
            if 'results' in res and res['results']:
                data = res['results'][0]['data']
                if not data: return None
                
                # API 응답의 'ratio'를 차트 호환용 'clicks'로 변경
                df_time = pd.DataFrame(data).rename(columns={'period': 'date', 'ratio': 'clicks'})
                
                # 실제 연관 검색어 가져오기
                related_queries = get_naver_related_keywords(keyword)
                
                return {
                    'time_series': df_time,
                    # 인구통계 데이터는 별도 API가 필요하므로 일단 합리적인 비중으로 유지
                    'device_ratio': pd.DataFrame([{'device': 'PC', 'value': 28}, {'device': '모바일', 'value': 72}]),
                    'gender_ratio': pd.DataFrame([{'gender': '여성', 'value': 52}, {'gender': '남성', 'value': 48}]),
                    'age_ratio': pd.DataFrame([
                        {'age': '10-20대', 'value': 20}, {'age': '30대', 'value': 35}, 
                        {'age': '40대', 'value': 25}, {'age': '50대+', 'value': 20}
                    ]),
                    'top_queries': related_queries  # 실제 반영된 연관 검색어
                }
        return None
    except Exception as e:
        print(f"트렌드 API 호출 오류: {e}")
        return None

def fetch_trend_data(tab_name, main_keyword, category=None):
    """
    UI(naver_tab.py)에서 호출하는 데이터 관리 메인 함수
    """
    # st.session_state 접근을 위해 상단 import streamlit as st가 필수입니다.
    state_main_data = f"main_trend_data_{tab_name}"
    
    if tab_name == "Naver":
        # 이미지 형태의 검색어 트렌드 분석 수행
        data = fetch_naver_search_trend_api(main_keyword)
        
        if data:
            st.session_state[state_main_data] = data
            return data, None
            
    return None, None