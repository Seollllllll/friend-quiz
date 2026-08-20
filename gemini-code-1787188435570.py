import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="우리 반 친퀴즈!", page_icon="🧩", layout="centered")

st.title("🧩 우리 반 친퀴즈!")
st.caption("선택한 질문에 대한 아이들의 답변을 보고 주인공을 맞춰보세요!")

# 세션 상태 초기화
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# 사이드바: 엑셀 파일 업로드, 반 선택, 질문 선택
with st.sidebar:
    st.header("⚙️ 퀴즈 데이터 설정")
    uploaded_file = st.file_uploader("엑셀 파일 업로드 (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, dtype=str)
            
            class_col = None
            name_col = None
            
            for col in df.columns:
                col_str = str(col).strip()
                if "반" in col_str and class_col is None:
                    class_col = col
                if ("이름" in col_str or "성명" in col_str) and name_col is None:
                    name_col = col

            if name_col is None:
                st.error("❌ '이름' 또는 '성명'이 포함된 열을 찾을 수 없습니다.")
            else:
                # 1. 학급 선택
                if class_col:
                    classes = sorted(df[class_col].dropna().unique())
                    selected_class = st.selectbox("🎯 학급 선택", classes, key="class_select")
                    filtered_df = df[df[class_col] == selected_class].copy()
                else:
                    filtered_df = df.copy()
                
                # 2. 질문 컬럼들만 추출 (반, 이름, 타임스탬프 제외)
                ignore_keywords = ["타임스탬프", "Timestamp", "시간"]
                question_cols = []
                for col in df.columns:
                    col_str = str(col).strip()
                    if col == name_col or col == class_col:
                        continue
                    if any(kw in col_str for kw in ignore_keywords):
                        continue
                    question_cols.append(col)
                
                # 3. 질문 선택
                selected_question = st.selectbox("❓ 질문 선택", question_cols, key="question_select")
                
                # 상태 변경 감지 및 데이터 갱신
                state_key = f"{selected_class}_{selected_question}"
                if "last_state" not in st.session_state or st.session_state.last_state != state_key:
                    st.session_state.last_state = state_key
                    st.session_state.class_col = class_col
                    st.session_state.name_col = name_col
                    st.session_state.selected_question = selected_question
                    
                    # 해당 질문에 답변이 있는 학생 데이터만 추출 후 랜덤 섞기
                    valid_quiz = []
                    for row in filtered_df.to_dict("records"):
                        ans = str(row.get(selected_question, "")).strip()
                        if pd.notna(row.get(selected_question)) and ans != "" and ans.lower() != "nan":
                            valid_quiz.append(row)
                    
                    random.shuffle(valid_quiz)
                    st.session_state.filtered_quiz = valid_quiz
                    st.session_state.current_index = 0
                    st.session_state.show_answer = False

                st.success(f"총 {len(st.session_state.get('filtered_quiz', []))}명의 답변 (랜덤 섞기 완료!)")
            
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    st.divider()
    if st.button("🔀 학생 순서 다시 섞기", use_container_width=True):
        if "filtered_quiz" in st.session_state and st.session_state.filtered_quiz:
            random.shuffle(st.session_state.filtered_quiz)
            st.session_state.current_index = 0
            st.session_state.show_answer = False
            st.success("순서를 다시 섞었습니다!")
            st.rerun()

# 메인 화면 영역
if "filtered_quiz" in st.session_state and st.session_state.filtered_quiz:
    quiz_data = st.session_state.filtered_quiz
    current_student = quiz_data[st.session_state.current_index]
    
    name_col = st.session_state.get("name_col")
    selected_question = st.session_state.get("selected_question")

    # 진행 상황 표시
    total_students = len(quiz_data)
    st.progress((st.session_state.current_index + 1) / total_students)
    st.write(f"**학생 {st.session_state.current_index + 1} / {total_students}**")

    # 퀴즈 카드 표시
    with st.container(border=True):
        st.subheader(f"Q. {selected_question}")
        st.write("")
        
        answer = current_student.get(selected_question, "")
        st.info(f"💬 \"{answer}\"")
        
        st.divider()
        
        if st.session_state.show_answer:
            student_name = current_student.get(name_col, "이름 없음")
            st.success(f"🎉 **정답: {student_name}**")
        else:
            st.warning("❓ **이 답변의 주인공은 누구일까요?**")

    # 제어 버튼 (3개)
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👀 정답 공개", use_container_width=True, type="primary"):
            st.session_state.show_answer = True
            st.balloons()
            st.rerun()

    with col2:
        if st.button("➡️ 다음 학생", use_container_width=True):
            if st.session_state.current_index < len(quiz_data) - 1:
                st.session_state.current_index += 1
            else:
                st.session_state.current_index = 0
            st.session_state.show_answer = False
            st.rerun()

    with col3:
        if st.button("🔄 처음부터", use_container_width=True):
            st.session_state.current_index = 0
            st.session_state.show_answer = False
            st.rerun()

else:
    st.info("👈 왼쪽 사이드바에서 엑셀(.xlsx) 파일을 업로드해 주세요!")
