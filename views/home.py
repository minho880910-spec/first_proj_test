import streamlit as st

def render_home():
    st.markdown("""
        <style>
            .home-card {display: flex; justify-content: center; align-items: center; gap: 30px; flex-wrap: wrap;}
            .home-cat {width: 340px; max-width: 100%; filter: drop-shadow(0 20px 30px rgba(0,0,0,0.12));}
            .home-text-box {max-width: 520px;}
            .home-text-box h1 {margin: 0; white-space: nowrap; display: inline-block;}
            .home-text-box h4 {margin: 20px 0 30px; color: #4f4f4f;}
            .home-bubble {font-family: 'Arial Black', sans-serif; color: #8b2180; font-size: 18px; margin-bottom: 20px;}
           
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div id='home-right-bg'>", unsafe_allow_html=True)
        st.markdown("<div class='home-card'>", unsafe_allow_html=True)
        st.markdown("""
            <svg class='home-cat' viewBox='0 0 320 320' xmlns='http://www.w3.org/2000/svg'>
                <rect x='0' y='0' width='320' height='320' rx='32' fill='#f3fff2'/>
                <ellipse cx='160' cy='190' rx='92' ry='86' fill='#101010' stroke='#000000' stroke-width='10'/>
                <path d='M66 176 Q90 138 118 124 Q110 102 132 88 Q154 74 168 104 Q182 74 204 88 Q226 104 218 124 Q246 138 270 176' fill='#101010' stroke='#000000' stroke-width='10'/>
                <path d='M90 126 Q102 90 128 98' fill='#101010' stroke='#000000' stroke-width='10' stroke-linecap='round'/>
                <path d='M230 126 Q238 90 214 98' fill='#101010' stroke='#000000' stroke-width='10' stroke-linecap='round'/>
                <ellipse cx='118' cy='170' rx='18' ry='24' fill='#ffffff'/>
                <ellipse cx='202' cy='170' rx='18' ry='24' fill='#ffffff'/>
                <circle cx='118' cy='176' r='8' fill='#000000'/>
                <circle cx='202' cy='176' r='8' fill='#000000'/>
                <path d='M137 210 Q160 226 183 210' stroke='#ffffff' stroke-width='10' fill='none' stroke-linecap='round'/>
                <path d='M160 210 C150 240 140 240 120 210' stroke='#ffffff' stroke-width='10' fill='none' stroke-linecap='round'/>
                <path d='M90 154 Q80 180 92 198 Q102 216 118 210' fill='#101010' stroke='#000000' stroke-width='10' stroke-linecap='round'/>
                <path d='M230 154 Q240 180 228 198 Q218 216 202 210' fill='#101010' stroke='#000000' stroke-width='10' stroke-linecap='round'/>
                <path d='M136 64 C128 24 152 12 168 44 C174 62 166 84 146 84 Q134 84 136 64 Z' fill='#101010' stroke='#000000' stroke-width='8'/>
                <path d='M196 64 C204 24 180 12 164 44 C158 62 166 84 186 84 Q198 84 196 64 Z' fill='#101010' stroke='#000000' stroke-width='8'/>
                <path d='M110 218 Q150 270 190 218' stroke='#000000' stroke-width='10' fill='none' stroke-linecap='round'/>
            </svg>
        """, unsafe_allow_html=True)
        st.markdown("<div class='home-text-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='white-space: nowrap; display: inline-block;'>지피지기면 백전백승</h1>", unsafe_allow_html=True)
        st.markdown("<h4>당신의 제품을 가장 빛나게 할 포스팅을 생성합니다.</h4>", unsafe_allow_html=True)
        st.info("👈 좌측 사이드바에서 프롬프트를 입력하고 콘텐츠 제작을 시작해보세요!")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)