import streamlit as st
from modules.trend_analyzer import get_trend_summary

def fetch_trend_data(tab_name: str, main_keyword: str, category: str = None, selected_period: str = "now 7-d"):
    """
    Fetches and caches trend data in Streamlit's session state.
    Returns (main_data, cat_data).
    """
    state_last_main = f"last_main_keyword_{tab_name}"
    state_last_period = f"last_period_{tab_name}"
    state_main_data = f"main_trend_data_{tab_name}"
    
    if (state_last_main not in st.session_state) or \
       (st.session_state[state_last_main] != main_keyword) or \
       (st.session_state.get(state_last_period) != selected_period) or \
       not st.session_state.get(state_main_data):
        with st.spinner(f"'{main_keyword}' {tab_name} 트렌드 분석 중..."):
            main_trend_data = get_trend_summary(main_keyword, period=selected_period, platform=tab_name)
            st.session_state[state_main_data] = main_trend_data
            st.session_state[state_last_main] = main_keyword
            st.session_state[state_last_period] = selected_period

    state_last_cat = f"last_trend_category_{tab_name}"
    state_last_cat_period = f"last_cat_period_{tab_name}"
    state_cat_data = f"category_trend_data_{tab_name}"

    if category:
        if (state_last_cat not in st.session_state) or \
           (st.session_state[state_last_cat] != category) or \
           (st.session_state.get(state_last_cat_period) != selected_period) or \
           not st.session_state.get(state_cat_data):
            with st.spinner(f"'{category}' {tab_name} 인기검색어 가져오는 중..."):
                category_trend_data = get_trend_summary(category, period=selected_period, platform=tab_name)
                st.session_state[state_cat_data] = category_trend_data
                st.session_state[state_last_cat] = category
                st.session_state[state_last_cat_period] = selected_period

    return st.session_state.get(state_main_data), st.session_state.get(state_cat_data) if category else None
