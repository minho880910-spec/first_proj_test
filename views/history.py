import streamlit as st
from modules.database import get_all_history, delete_history, clear_all_history

def render_history():
    st.header("포스팅 생성 내역")
    
    # 1. 데이터베이스에서 내역 로드
    df = get_all_history()

    if df.empty:
        st.info("저장된 내역이 없습니다.")
    else:
        # 상단 영역: 전체 삭제 (이 부분은 상단에 고정되어 있어 팝오버를 유지해도 안전합니다)
        col1, col2 = st.columns([8, 2])
        with col2:
            with st.popover("전체 내역 삭제", use_container_width=True):
                st.write("⚠️ **모든 기록을 삭제할까요?**")
                if st.button("전체 삭제 확정", type="primary", use_container_width=True):
                    clear_all_history()
                    st.rerun()

        st.divider()

        # 2. 개별 히스토리 출력 루프
        for index, row in df.iterrows():
            with st.expander(f"[{row['created_at']}] {row['category']} - {row['title']}"):
                
                # 콘텐츠 영역
                st.markdown("#### 📸 Instagram")
                st.code(row['instagram_content'], language=None)
                st.markdown("#### 🧵 Threads")
                st.code(row['threads_content'], language=None)
                st.markdown("#### 🐦 X (Twitter)")
                st.code(row['x_content'], language=None)

                st.divider()
                
                # 3. [개선] 팝오버 대신 세션 상태를 활용한 삭제 확인 로직
                # 버튼을 누르면 해당 행의 삭제 확인 모드가 활성화됩니다.
                del_confirm_key = f"del_confirm_{row['id']}"
                
                if del_confirm_key not in st.session_state:
                    st.session_state[del_confirm_key] = False

                if not st.session_state[del_confirm_key]:
                    # 처음 보이는 '삭제' 버튼
                    if st.button("🗑️ 이 기록 삭제하기", key=f"btn_del_{row['id']}", use_container_width=True):
                        st.session_state[del_confirm_key] = True
                        st.rerun()
                else:
                    # '삭제하기'를 눌렀을 때 나타나는 최종 확인 화면
                    st.warning("⚠️ **정말 삭제하시겠습니까?** 삭제 후에는 복구가 불가능합니다.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ 네, 삭제합니다", key=f"yes_{row['id']}", type="primary", use_container_width=True):
                            delete_history(row['id'])
                            # 삭제 성공 시 해당 세션 상태 제거 후 리셋
                            del st.session_state[del_confirm_key]
                            st.toast("삭제가 완료되었습니다.")
                            st.rerun()
                    with c2:
                        if st.button("❌ 취소", key=f"no_{row['id']}", use_container_width=True):
                            st.session_state[del_confirm_key] = False
                            st.rerun()