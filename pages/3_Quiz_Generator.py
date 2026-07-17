import streamlit as st
import os
from utils.gemini_client import generate_quiz
from database.db_manager import save_quiz, get_quizzes, get_setting
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="Quiz Generator - EduAI", page_icon="❓", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">Quiz generator</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Generate multi-format tests with adjustable difficulty based on textbook context.</p>
</div>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

active_file = st.session_state.get("current_file", "")
api_key = st.session_state.get("api_key", "")

if not active_file:
    st.warning("Please upload study materials first in the Study Material page.")
elif not api_key:
    st.warning("Please configure your Gemini API Key in the Settings page.")
else:
    extracted_txt_path = os.path.join("uploads", f"{active_file}_extracted.txt")
    if not os.path.exists(extracted_txt_path):
        st.error("Extracted text not found. Please re-process your study material.")
    else:
        with open(extracted_txt_path, "r", encoding="utf-8") as f:
            document_text = f.read()
            
        with st.container(border=True):
            st.markdown("### Quiz Configuration")
            topic = st.text_input("Quiz Topic / Subject Name", value=active_file.split(".")[0])
            difficulty = st.selectbox("Select Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                mcq_count = st.slider("Multiple Choice Questions (MCQ)", min_value=0, max_value=10, value=3)
            with col2:
                sa_count = st.slider("Short Answer Questions", min_value=0, max_value=5, value=2)
            with col3:
                tf_count = st.slider("True / False Questions", min_value=0, max_value=10, value=3)
                
            total_questions = mcq_count + sa_count + tf_count
            generate_disabled = total_questions == 0 or total_questions > 10
            
            if total_questions > 10:
                st.error("Maximum 10 questions allowed per quiz.")
            elif total_questions == 0:
                st.info("Select at least 1 question to generate.")
                
            if st.button("🚀 Generate Quiz", disabled=generate_disabled, use_container_width=True):
                with st.spinner("Analyzing document content and writing custom questions..."):
                    try:
                        questions = generate_quiz(
                            text=document_text,
                            topic=topic,
                            difficulty=difficulty,
                            mcq_count=mcq_count,
                            sa_count=sa_count,
                            tf_count=tf_count,
                            api_key=api_key
                        )
                        if questions and "Error" not in questions[0].get("question_text", ""):
                            quiz_id = save_quiz(
                                file_name=active_file,
                                topic=topic,
                                difficulty=difficulty,
                                questions=questions
                            )
                            st.session_state.active_quiz_id = quiz_id
                            st.session_state.quiz_taking_started = True
                            st.session_state.current_question_idx = 0
                            st.session_state.quiz_responses = {}
                            st.session_state.quiz_evaluated_items = []
                            st.success(f"Quiz containing {len(questions)} questions generated successfully!")
                            if st.button("📝 Start Quiz Now", use_container_width=True):
                                st.switch_page("pages/4_AI_Evaluation.py")
                        else:
                            st.error(questions[0].get("question_text") if questions else "Failed to generate questions.")
                    except Exception as e:
                        st.error(f"Failed to generate quiz: {str(e)}")
                        
        st.write("")
        st.markdown("### Previously Generated Quizzes")
        quizzes = get_quizzes()
        if quizzes:
            for q in quizzes[:5]:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{q['topic']}** (Source: `{q['file_name']}`)")
                with col2:
                    st.write(f"Difficulty: *{q['difficulty']}*")
                with col3:
                    st.write(f"Questions: {q['question_count']}")
                with col4:
                    if st.button("Take Quiz", key=f"take_{q['id']}", use_container_width=True):
                        st.session_state.active_quiz_id = q["id"]
                        st.session_state.quiz_taking_started = True
                        st.session_state.current_question_idx = 0
                        st.session_state.quiz_responses = {}
                        st.session_state.quiz_evaluated_items = []
                        st.switch_page("pages/4_AI_Evaluation.py")
        else:
            st.write("No quizzes in database yet.")
