import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. API 키 및 설정 로드
load_dotenv()
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# 분석할 핵심 키워드 데이터베이스 (5개 이상 등록 가능)
TOP_KEYWORDS = {
    "패션의류": ["원피스", "가디건", "바람막이", "맨투맨", "슬랙스"],
    "디지털/가전": ["아이폰", "갤럭시", "에어팟", "모니터", "키보드"],
    "화장품/미용": ["앰플", "수분크림", "선크림", "쿠션파운데이션", "립스틱"]
}

CAT_IDS = {
    "패션의류": "50000000",
    "디지털/가전": "50000003",
    "화장품/미용": "50000002"
}

def get_shopping_data(cat_name, date):
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }
    
    all_keywords = TOP_KEYWORDS.get(cat_name, [])
    final_rank_results = []

    # [핵심 로직] 네이버 제약사항(키워드 최대 5개)을 해결하기 위해 5개씩 나눠서 호출

        
    body = {
        "startDate": date,
        "endDate": date,
        "timeUnit": "date",
        "category": CAT_IDS[cat_name],
        "keyword": [{"name": cat_name+"/"+kw, "param": [kw]} for kw in all_keywords],
        "device": "", "gender": "", "ages": []
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            res_json = response.json()
            print(res_json)
            print("="*50)
            for item in res_json['results']:
                data = item.get('data', [])
                # 데이터가 있으면 ratio 추출, 없으면 0
                ratio = data[0].get('ratio', 0) if data else 0
                final_rank_results.append({"title": item['title'], "ratio": ratio})
        else:
            # 400 에러 등이 날 경우 상세 원인 파악용
            st.error(f"API 에러 ({response.status_code}): {response.text}")
    except Exception as e:
        st.error(f"연결 오류: {str(e)}")

    # 모든 호출이 끝난 후 ratio(클릭 비중)가 높은 순서대로 전체 정렬
    if final_rank_results:
        sorted_ranks = sorted(final_rank_results, key=lambda x: x['ratio'], reverse=True)
        # 화면에 표시할 수 있도록 문자열 리스트로 변환
        return [f"{item['title']} ({item['ratio']:.1f})" for item in sorted_ranks]
    
    return ["데이터 없음"] * 10

# --- UI 레이아웃 설정 ---
st.markdown("""
    <style>
    .kwd-card { background-color: white; border: 1px solid #dee2e6; border-radius: 4px; padding: 15px; min-height: 450px; }
    .kwd-date { font-size: 16px; font-weight: bold; text-align: center; margin-bottom: 10px; border-bottom: 2px solid #333; padding-bottom: 8px; }
    .kwd-item { font-size: 13px; margin: 6px 0; display: flex; align-items: center; }
    .rank-num { font-weight: bold; color: #00c73c; width: 20px; margin-right: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("쇼핑인사이트 (키워드 랭킹 분석)")
st.caption("5개 이상의 키워드도 자동으로 분할 호출하여 전체 순위를 산출합니다.")

selected_cat = st.selectbox("분야 선택", list(TOP_KEYWORDS.keys()))

# 날짜 설정 (데이터가 확실한 4일 전부터 조회)
base_date = datetime.now() - timedelta(days=4)
dates = [(base_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(4)]
dates.reverse()

cols = st.columns(4)

for i, date_str in enumerate(dates):
    with cols[i]:
        ranked_keywords = get_shopping_data(selected_cat, date_str)
        
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        display_date = dt.strftime('%Y.%m.%d.') + f"({['월','화','수','목','금','토','일'][dt.weekday()]})"
        
        card_html = f'<div class="kwd-card"><div class="kwd-date">{display_date}</div>'
        for rank, kw_info in enumerate(ranked_keywords, 1):
            card_html += f'<div class="kwd-item"><span class="rank-num">{rank}</span>{kw_info}</div>'
        card_html += '</div>'
        
        st.markdown(card_html, unsafe_allow_html=True)