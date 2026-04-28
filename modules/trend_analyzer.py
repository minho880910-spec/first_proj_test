from pytrends.request import TrendReq
import pandas as pd
import time

def get_trend_summary(keyword):
    """
    Fetches Google Trends related queries for the given keyword and returns a summary.
    """
    if not keyword:
        return "키워드를 입력해주세요."

    try:
        # Initialize pytrends
        pytrend = TrendReq(hl='ko-KR', tz=540) # Timezone for Korea is UTC+9 (540 mins)
        
        # Build payload
        pytrend.build_payload(kw_list=[keyword], timeframe='now 7-d', geo='KR')
        
        # Get related queries
        related_queries = pytrend.related_queries()
        
        if keyword in related_queries and related_queries[keyword]['top'] is not None:
            top_df = related_queries[keyword]['top']
            top_queries = top_df['query'].tolist()[:5]  # Get top 5 related queries
            
            if top_queries:
                summary = f"**'{keyword}'** 관련 구글 트렌드 최근 7일 인기 검색어:\n\n"
                for i, q in enumerate(top_queries):
                    summary += f"{i+1}. {q}\n"
                return summary
            else:
                return f"**'{keyword}'**에 대한 최근 관련 트렌드 데이터가 부족합니다."
        else:
             return f"**'{keyword}'**에 대한 최근 관련 트렌드 데이터가 부족합니다."
             
    except Exception as e:
        return f"트렌드 분석 중 오류가 발생했습니다: {e}\n(Pytrends API는 잦은 요청 시 차단될 수 있습니다.)"
