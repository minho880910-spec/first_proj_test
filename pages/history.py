import streamlit as st
import pandas as pd


st.header("🗂️ 콘텐츠 발행 히스토리")

history_data = st.session_state.get('history', [])

if history_data:
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("아직 생성된 콘텐츠 기록이 없습니다. '콘텐츠 생성기'에서 멋진 글을 작성해보세요!")