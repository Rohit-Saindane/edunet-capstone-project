import streamlit as st
import os
import pandas as pd
import plotly.express as px
from utils.gemini_client import evaluate_answer
from database.db_manager import (
    get_quiz_details, 
    save_student_answers, 
    get_quizzes, 
    get_setting
)
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="AI Evaluation - EduAI", page_icon="✏️", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">AI evaluation & quiz module</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Complete your generated tests and receive instant detailed grading feedback.</p>
</div>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

api_key = st.session_state.get("api_key", "")
active_quiz_id = st.session_state.get("active_quiz_id", None)

if "quiz_taking_started" not in st.session_state:
    st.session_state.quiz_taking_started = False
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "quiz_responses" not in st.session_state:
    st.session_state.quiz_responses = {}
if "quiz_evaluated_items" not in st.session_state:
    st.session_state.quiz_evaluated_items = []
if "current_q_answered" not in st.session_state:
    st.session_state.current_q_answered = False
if "current_q_evaluation" not in st.session_state:
    st.session_state.current_q_evaluation = None

if not active_quiz_id:
    st.info("No active quiz session found.")
    st.markdown("### Select a generated quiz to take:")
    quizzes = get_quizzes()
    if quizzes:
        for q in quizzes:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{q['topic']}** (`{q['file_name']}`)")
            with col2:
                st.write(f"Difficulty: {q['difficulty']}")
            with col3:
                if st.button("Start Quiz", key=f"start_take_{q['id']}", use_container_width=True):
                    st.session_state.active_quiz_id = q["id"]
                    st.session_state.quiz_taking_started = True
                    st.session_state.current_question_idx = 0
                    st.session_state.quiz_responses = {}
                    st.session_state.quiz_evaluated_items = []
                    st.session_state.current_q_answered = False
                    st.session_state.current_q_evaluation = None
                    st.rerun()
    else:
        st.warning("Please upload a file and generate a quiz first in the Quiz Generator.")
elif not api_key:
    st.warning("Please configure your Gemini API Key in the Settings page.")
else:
    quiz_meta, questions = get_quiz_details(active_quiz_id)
    if not quiz_meta or not questions:
        st.error("Quiz content unavailable.")
        st.session_state.active_quiz_id = None
        st.rerun()
        
    total_q = len(questions)
    current_idx = st.session_state.current_question_idx
    
    if current_idx < total_q:
        q = questions[current_idx]
        progress_val = float(current_idx) / float(total_q)
        
        st.progress(progress_val, text=f"Question {current_idx + 1} of {total_q}")
        st.write("")
        
        with st.container(border=True):
            st.markdown(f"### Question {current_idx + 1}")
            st.write(q["question_text"])
            st.write("")
            
            q_type = q["question_type"]
            input_key = f"taking_{q['id']}"
            
            user_ans = ""
            if not st.session_state.current_q_answered:
                if q_type == "MCQ":
                    user_ans = st.radio("Choose the correct option:", q["options"], index=None, key=input_key)
                elif q_type == "TF":
                    user_ans = st.radio("Choose True/False:", ["True", "False"], index=None, key=input_key)
                else:
                    user_ans = st.text_area("Write your answer explanation:", key=input_key)
                
                submit_disabled = (user_ans is None or user_ans == "")
                if st.button("📤 Submit Answer", disabled=submit_disabled, use_container_width=True):
                    with st.spinner("AI is grading your response..."):
                        evaluation = evaluate_answer(
                            question_text=q["question_text"],
                            correct_answer=q["correct_answer"],
                            question_type=q_type,
                            student_response=user_ans,
                            api_key=api_key
                        )
                        evaluation["question_id"] = q["id"]
                        evaluation["student_response"] = user_ans
                        st.session_state.current_q_evaluation = evaluation
                        st.session_state.current_q_answered = True
                        st.rerun()
            else:
                eval_item = st.session_state.current_q_evaluation
                st.info(f"Your submitted answer: {eval_item['student_response']}")
                
                status_color = "#10b981" if eval_item["is_correct"] else "#ef4444"
                status_sym = "✔️ Correct" if eval_item["is_correct"] else "❌ Incorrect"
                
                st.markdown(f"<p style='font-size:16px;color:{status_color};font-weight:bold;margin:0;'>{status_sym} · Score: {eval_item['marks_obtained']:.1f}/5.0</p>", unsafe_allow_html=True)
                st.write("")
                st.markdown(f"**Expected Answer:** `{q['correct_answer']}`")
                st.write("")
                st.markdown(f"**AI Explanation:** {eval_item['explanation']}")
                if eval_item.get("suggestions"):
                    st.markdown(f"**Improvement Suggestion:** {eval_item['suggestions']}")
                if eval_item.get("weak_concept_flag"):
                    st.markdown(f"<span style='background: rgba(239, 68, 68, 0.15); color: #f87171; padding: 4px 10px; border-radius: 12px; font-size: 0.85rem;'>Gaps identified: <b>{eval_item['weak_concept_flag']}</b></span>", unsafe_allow_html=True)
                
                st.write("")
                if st.button("➡️ Next Question", use_container_width=True):
                    st.session_state.quiz_evaluated_items.append(eval_item)
                    st.session_state.current_q_answered = False
                    st.session_state.current_q_evaluation = None
                    st.session_state.current_question_idx += 1
                    st.rerun()
    else:
        st.success("🎉 Quiz Completed!")
        eval_items = st.session_state.quiz_evaluated_items
        
        if len(eval_items) == total_q:
            save_student_answers(active_quiz_id, eval_items)
            st.session_state.quiz_evaluated_items = []
            
        total_obtained = sum(item["marks_obtained"] for item in eval_items)
        max_possible = len(eval_items) * 5.0
        pct = (total_obtained / max_possible) * 100 if max_possible > 0 else 0
        correct_count = sum(1 for item in eval_items if item["is_correct"])
        wrong_count = len(eval_items) - correct_count
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            with st.container(border=True):
                st.metric(label="Total Score", value=f"{total_obtained:.1f} / {max_possible:.1f}")
        with col_m2:
            with st.container(border=True):
                st.metric(label="Accuracy", value=f"{pct:.1f}%")
        with col_m3:
            with st.container(border=True):
                st.metric(label="Correct / Wrong", value=f"{correct_count} / {wrong_count}")
                
        st.write("")
        
        col_res, col_chart = st.columns([1.2, 1])
        with col_res:
            with st.container(border=True):
                st.markdown("### Weak Concepts Identified")
                gaps = [item["weak_concept_flag"] for item in eval_items if item.get("weak_concept_flag")]
                if gaps:
                    for g in set(gaps):
                        st.error(f"⚠️ {g}")
                    st.info("Head to the **Weak Topics** page to see details and suggestions.")
                else:
                    st.success("No critical conceptual gaps identified!")
        with col_chart:
            with st.container(border=True):
                st.markdown("### Answer Breakdown")
                df_break = pd.DataFrame({
                    "Status": ["Correct", "Incorrect"],
                    "Count": [correct_count, wrong_count]
                })
                fig = px.pie(
                    df_break, 
                    names="Status", 
                    values="Count", 
                    color="Status",
                    color_discrete_map={"Correct": "#10b981", "Incorrect": "#ef4444"}
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
        st.write("")
        if st.button("📋 Select Another Quiz", use_container_width=True):
            st.session_state.active_quiz_id = None
            st.session_state.quiz_taking_started = False
            st.session_state.current_question_idx = 0
            st.session_state.quiz_responses = {}
            st.session_state.quiz_evaluated_items = []
            st.session_state.current_q_answered = False
            st.session_state.current_q_evaluation = None
            st.rerun()
stream_meta = st.sidebar
stream_meta.markdown("---")
stream_meta.markdown("🎓 **EduAI v1.0.0**")
stream_meta.markdown("Supporting SDG 4 Quality Education")
