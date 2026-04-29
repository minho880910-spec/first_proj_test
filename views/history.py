import streamlit as st
from modules.database import get_all_history, delete_history, clear_all_history

def render_history():
    """톤앤매너 정보를 포함하여 생성 내역을 렌더링합니다."""
    
    st.header("포스팅 생성 내역")
    
    # 1. 데이터베이스에서 전체 내역 로드
    df = get_all_history()

    if df.empty:
        st.info("저장된 내역이 없습니다. 새로운 콘텐츠를 제작해 보세요.")
    else:
        # 상단 영역: 전체 삭제 버튼
        col1, col2 = st.columns([8, 2])
        with col2:
            with st.popover("전체 내역 삭제", use_container_width=True):
                st.write("⚠️ **전체 삭제**")
                st.write("모든 기록을 삭제하시겠습니까?")
                if st.button("확인", type="primary", use_container_width=True):
                    clear_all_history()
                    st.rerun()

        st.divider()

        # 2. 개별 히스토리 출력 루프
        for index, row in df.iterrows():
            # [수정 포인트] 생성 시간 뒤에 [톤앤매너] 정보를 추가하여 제목(프롬프트)과 구분
            # 예: [2026-04-29 11:46:04] [전문적인] 쿠우쿠우 다녀온 후기...
            header_text = f"[{row['created_at']}] [{row['tone']}] {row['title']}"
            
            with st.expander(header_text):
                
                # 플랫폼별 콘텐츠 영역
                st.markdown("#### 📸 Instagram")
                st.code(row['instagram_content'], language=None)

                st.divider()

                st.markdown("#### 🧵 Threads")
                st.code(row['threads_content'], language=None)

                st.divider()

                st.markdown("#### 🐦 X (Twitter)")
                st.code(row['x_content'], language=None)

                st.divider()
                
                # 3. 안전 삭제 확인 로직 (세션 상태 활용)
                del_confirm_key = f"del_confirm_{row['id']}"
                
                if del_confirm_key not in st.session_state:
                    st.session_state[del_confirm_key] = False

                if not st.session_state[del_confirm_key]:
                    if st.button("🗑️ 이 기록 삭제하기", key=f"btn_del_{row['id']}", use_container_width=True):
                        st.session_state[del_confirm_key] = True
                        st.rerun()
                else:
                    st.warning("⚠️ **정말 삭제하시겠습니까?**")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ 확정", key=f"yes_{row['id']}", type="primary", use_container_width=True):
                            delete_history(row['id'])
                            if del_confirm_key in st.session_state:
                                del st.session_state[del_confirm_key]
                            st.toast("기록이 삭제되었습니다.")
                            st.rerun()
                    with c2:
                        if st.button("❌ 취소", key=f"no_{row['id']}", use_container_width=True):
                            st.session_state[del_confirm_key] = False
                            st.rerun()