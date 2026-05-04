import os
import requests
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from dotenv import load_dotenv

load_dotenv()

def get_naver_headers():
    return {
        "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
        "Content-Type": "application/json"
    }

def fetch_google_real_trend(keyword, period='today 1-m'):
    try:
        pytrend = TrendReq(hl='ko-KR', tz=540)
        pytrend.build_payload(kw_list=[keyword], timeframe=period, geo='KR')
        iot = pytrend.interest_over_time()
        if not iot.empty:
            iot = iot.reset_index()
            iot.rename(columns={'date': 'date', keyword: 'clicks'}, inplace=True)
            iot['date'] = iot['date'].dt.strftime('%Y-%m-%d')
            return iot[['date', 'clicks']]
    except:
        return None

def fetch_naver_search_trend(keyword):
    try:
        end_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=32)).strftime('%Y-%m-%d')
        headers = get_naver_headers()
        body = {
            "startDate": start_date, "endDate": end_date, "timeUnit": "date",
            "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
        }
        res = requests.post("https://openapi.naver.com/v1/datalab/search", json=body, headers=headers).json()
        return pd.DataFrame(res['results'][0]['data']).rename(columns={'period': 'date', 'ratio': 'clicks'})
    except:
        return None

def fetch_naver_autocomplete(keyword):
    try:
        encoded = urllib.parse.quote(keyword)
        url = f"https://ac.search.naver.com/nx/ac?q={encoded}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&t_koreng=1&rev=4&q_enc=UTF-8&st=100"
        res = requests.get(url, timeout=5).json()
        return [item[0] for item in res.get('items', [[]])[0]][:10]
    except:
        return []