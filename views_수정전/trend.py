import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time

def get_realtime_trend(keyword):
    # Google RSS / 검색 트렌드를 흉내낸 시뮬레이션 함수
    np.random.seed(sum(ord(c) for c in keyword))
    base_val = np.random.randint(100, 1000)
    trend_data = base_val + np.cumsum(np.random.randn(30) * 10)
    return trend_data


st.header("📊 실시간 마케팅 트렌드 분석")

col_input, col_btn = st.columns([4, 1])
with col_input:
    search_query = st.text_input("분석할 타겟 키워드 (예: 카페 인테리어, 1인 창업)", value=st.session_state['search_keyword'])
with col_btn:
    st.write(" ")
    analyze_btn = st.button("실시간 분석", use_container_width=True)

if analyze_btn:
    st.session_state['search_keyword'] = search_query
    with st.spinner('실시간 데이터를 분석 중입니다...'):
        time.sleep(1)

keyword = st.session_state['search_keyword']
current_trend = get_realtime_trend(keyword)

m1, m2, m3, m4 = st.columns(4)
m1.metric("검색량 지수", f"{int(current_trend[-1]):,}", f"{int(current_trend[-1] - current_trend[-2])}%")
m2.metric("경쟁 강도", "높음", "-2%", delta_color="inverse")
m3.metric("인스타 언급량", f"{len(keyword)*120}건", "NEW")
m4.metric("AI 소재 추천", "5건", "TOP")

st.divider()

l_col, r_col = st.columns([2, 1])
with l_col:
    st.subheader(f"📈 '{keyword}' 트렌드 추이")
    chart_df = pd.DataFrame({
        '날짜': pd.date_range(end=datetime.date.today(), periods=30),
        '관심도': current_trend
    }).set_index('날짜')
    st.area_chart(chart_df)

with r_col:
    st.subheader("🔗 연관 급상승 키워드")
    rel_df = pd.DataFrame({
        "키워드": [f"{keyword} 추천", "인공지능 마케팅", "SNS 자동화", "카드뉴스 디자인", "트렌드 분석"],
        "매칭점수": ["98점", "85점", "72점", "64점", "51점"]
    })
    st.table(rel_df)

# API가 연결되어 있다면 AI 인사이트 제공
client = st.session_state.get('openai_client')
if client:
    st.subheader("💡 AI 마케터 인사이트 (GPT-4o-mini)")
    try:
        insight_prompt = f"키워드 '{keyword}'의 검색량이 상승 중이야. 이 키워드로 마케팅을 하려는 소상공인에게 50자 이내의 짧고 강렬한 전략 한 줄을 제안해줘."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": insight_prompt}]
        )
        st.success(response.choices[0].message.content)
    except Exception as e:
        st.error(f"인사이트 생성 중 오류: {e}")