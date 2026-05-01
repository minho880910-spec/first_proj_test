import os
import json
import requests
import pandas as pd
import streamlit as st
from openai import OpenAI
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

def generate_ai_estimates(keyword, category):
    """데이터 부재 시 AI를 통해 논리적 예측 데이터 생성"""
    prompt = f"""
    키워드 '{keyword}'와 카테고리 '{category}'의 최근 대한민국 검색 트렌드를 분석해서 예상 데이터를 JSON으로 줘.
    형식은 반드시 다음을 지켜야 해:
    {{
        "device": {{"mo": 70, "pc": 30}},
        "gender": {{"f": 55, "m": 45}},
        "age": {{"10": 5, "20": 25, "30": 35, "40": 20, "50": 10, "60": 5}},
        "ranking": ["연관1", "연관2", "연관3", "연관4", "연관5", "연관6", "연관7", "연관8", "연관9", "연관10"]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

def fetch_naver_all_data(keyword, category_id, category_name):
    # 1. 초기화 및 검색 추이(시계열) 로드
    end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=32)).strftime('%Y-%m-%d')
    
    search_url = "https://openapi.naver.com/v1/datalab/search"
    search_body = {"startDate": start_date, "endDate": end_date, "timeUnit": "date",
                   "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]}
    
    result = {'time_series': pd.DataFrame(), 'top_queries': [], 'device_ratio': None, 
              'gender_ratio': None, 'age_ratio': None, 'category_ranking': [], 'is_ai_generated': False}

    try:
        res_search = requests.post(search_url, json=search_body, headers=get_naver_headers()).json()
        result['time_series'] = pd.DataFrame(res_search['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except: pass

    # 2. 실시간 쇼핑 데이터 탐색 (3~10일 전 루프)
    found_real_data = False
    if category_id:
        for delay in range(3, 11):
            t_date = (datetime.now() - timedelta(days=delay)).strftime('%Y-%m-%d')
            common_body = {"startDate": t_date, "endDate": t_date, "timeUnit": "date", "category": category_id}
            
            try:
                # 랭킹 데이터 시도
                r_res = requests.post("https://openapi.naver.com/v1/datalab/shopping/category/keywords", 
                                      json=common_body, headers=get_naver_headers()).json()
                items = r_res.get('results', [{}])[0].get('data', [])
                if items:
                    result['category_ranking'] = [i.get('name') for i in items][:10]
                    # 나머지 지표 로드
                    for ep in ["device", "gender", "age"]:
                        s_res = requests.post(f"https://openapi.naver.com/v1/datalab/shopping/category/{ep}", 
                                              json=common_body, headers=get_naver_headers()).json()
                        s_data = s_res.get('results', [{}])[0].get('data', [])
                        if s_data:
                            df = pd.DataFrame(s_data).rename(columns={'group': ep, 'ratio': 'value'})
                            if ep == "device": df['device'] = df['device'].replace({'mo': '모바일', 'pc': 'PC'})
                            if ep == "gender": df['gender'] = df['gender'].replace({'f': '여성', 'm': '남성'})
                            result[f'{ep}_ratio'] = df
                    found_real_data = True
                    break
            except: continue

    # 3. 데이터 부재 시 AI 예측값으로 보충
    if not found_real_data or not result['category_ranking']:
        ai_data = generate_ai_estimates(keyword, category_name)
        if ai_data:
            result['is_ai_generated'] = True
            if not result['category_ranking']: result['category_ranking'] = ai_data['ranking']
            if result['device_ratio'] is None:
                result['device_ratio'] = pd.DataFrame([{'device': '모바일', 'value': ai_data['device']['mo']},
                                                       {'device': 'PC', 'value': ai_data['device']['pc']}])
            if result['gender_ratio'] is None:
                result['gender_ratio'] = pd.DataFrame([{'gender': '여성', 'value': ai_data['gender']['f']},
                                                       {'gender': '남성', 'value': ai_data['gender']['m']}])
            if result['age_ratio'] is None:
                result['age_ratio'] = pd.DataFrame([{'age': f"{k}대", 'value': v} for k, v in ai_data['age'].items()])

    return result

def fetch_trend_data(tab_name, main_keyword, category_name=None):
    state_key = f"main_trend_data_{tab_name}"
    cid = get_naver_category_id(category_name)
    data = fetch_naver_all_data(main_keyword, cid, category_name)
    st.session_state[state_key] = data
    return data, data