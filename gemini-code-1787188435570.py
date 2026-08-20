import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="우리 반 친퀴즈!", page_icon="🧩", layout="centered")

st.title("🧩 우리 반 친퀴즈!")
st.caption("질문들에 대해 이렇게 답변한 주인공은 누구일까요?")

# 세션 상태 초기화
if "filtered_quiz" not in st.session_state:
    st.session_state.filtered_quiz = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# 사이드바: 엑셀 파일 업로드 및 반 선택
with st.sidebar:
    st.header("⚙️ 퀴즈 데이터 설정")
    uploaded_file = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(uploaded_file)
            
            # '반'과 '이름' 컬럼 유연하게 찾기
            class_col = None
            name_col = None
            
            for col in df.columns:
                col_str = str(col).strip()
                if "반" in col_str and class_col is None:
                    class_col = col
                if ("이름" in col_str or "성명" in col_str) and name_col is None:
                    name_col = col

            if name_col is None:
                st.error("❌ '이름' 또는 '성명'이 포함된 열을 찾을 수 없습니다. 엑셀의 열 이름을 확인해 주세요.")
            else:
                # '반' 컬럼이 있는 경우 학급 선택 필터 제공
                if class_col:
                    classes = sorted(df[class_col].dropna().unique())
                    selected_class = st.selectbox("🎯 학급 선택", classes)
                    filtered_df = df[df[class_col] == selected_class].copy()
                else:
                    filtered_df = df.copy()
                
                # 메인 로직에서 쉽게 쓰기 위해 컬럼명 표준화
                st.session_state.class_col = class_col
                st.session_state.name_col = name_col
                st.session_state.filtered_quiz = filtered_df.to_dict("records")
                st.success(f"총 {len(st.session_state.filtered_quiz)}명의 학생 데이터를 불러왔습니다!")
            
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    st.divider()
    if st.button("🔀 순서 섞기", use_container_width=True):
        if st.session_state.filtered_quiz:
            random.shuffle(st.session_state.filtered_quiz)
            st.session_state.current_index = 0
            st.session_state.show_answer = False
            st.rerun()

# 메인 화면 영역
if st.session_state.filtered_quiz:
    current_student = st.session_state.filtered_quiz[st.session_state.current_index]

    # 진행 상황 표시
    total_students = len(st.session_state.filtered_quiz)
    st.progress((st.session_state.current_index + 1) / total_students)
    st.write(f"**학생 {st.session_state.current_index + 1} / {total_students}**")

    # '반', '이름', '타임스탬프' 등을 제외한 실제 질문들만 추출
    name_col = st.session_state.get("name_col")
    class_col = st.session_state.get("class_col")
    
    ignore_keywords = ["타임스탬프", "Timestamp", "시간"]
    
    questions = []
    for col in current_student.keys():
        col_str = str(col).strip()
        # 반, 이름, 타임스탬프 컬럼 제외
        if col == name_col or col == class_col:
            continue
        if any(kw in col_str for kw in ignore_keywords):
            continue
        if pd.notna(current_student[col]):  # 답변이 비어있지 않은 질문만 추가
            questions.append(col)

    # 퀴즈 카드 표시
    with st.container(border=True):
        st.subheader("💡 이 학생의 힌트 목록")
        st.write("")
        
        # 질문과 답변 출력
        for idx, q in enumerate(questions, 1):
            answer = current_student[q]
            st.markdown(f"**Q{idx}. {q}**")
            st.info(f"💬 \"{answer}\"")
        
        st.divider()
        
        # 정답 공개 상태 확인
        if st.session_state.show_answer:
            student_name = current_student.get(name_col, "이름 없음")
            st.success(f"🎉 **정답: {student_name}**")
        else:
            st.warning("❓ **이 모든 답변의 주인공은 누구일까요?**")

    # 버튼 제어 영역
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👀 정답 공개", use_container_width=True, type="primary"):
            st.session_state.show_answer = True
            st.balloons()
            st.rerun()

    with col2:
        if st.button("➡️ 다음 학생", use_container_width=True):
            if st.session_state.current_index < len(st.session_state.filtered_quiz) - 1:
                st.session_state.current_index += 1
            else:
                st.session_state.current_index = 0
            st.session_state.show_answer = False
            st.rerun()

    with col3:
        if st.button("🔄 처음부터 다시", use_container_width=True):
            st.session_state.current_index = 0
            st.session_state.show_answer = False
            st.rerun()

else:
    st.info("👈 왼쪽 사이드바에서 엑셀(.xlsx) 파일을 업로드해 주세요!")