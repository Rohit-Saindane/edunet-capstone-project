import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from database.db_manager import (
    get_setting, 
    get_student_evaluation_history, 
    get_weak_topics,
    get_quizzes
)
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(
    page_title="EduAI - Personalized Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_theme()
load_branding()

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

if "current_file" not in st.session_state:
    st.session_state.current_file = get_setting("current_file", "")

st.markdown("""
<div class="sdg-banner">
    <div>
        <p class="sdg-banner-title">SDG 4 — Quality education</p>
        <p class="sdg-banner-text">Personalized learning for every student</p>
    </div>
    <div style="font-size:32px;">🎓</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='font-size:14px;margin:0 0 20px;opacity:0.8;'>Welcome back. Here is your current academic progress overview.</p>", unsafe_allow_html=True)

uploads_dir = "uploads"
materials_count = 0
if os.path.exists(uploads_dir):
    materials_count = len([f for f in os.listdir(uploads_dir) if f.endswith("_extracted.txt")])

eval_history = get_student_evaluation_history()
quizzes_taken = 0
avg_score_pct = 0
if eval_history:
    unique_quiz_attempts = set()
    total_obtained = 0
    total_possible = 0
    for row in eval_history:
        unique_quiz_attempts.add(row["quiz_id"])
        total_obtained += row["marks_obtained"]
        total_possible += row["total_marks"]
    quizzes_taken = len(unique_quiz_attempts)
    if total_possible > 0:
        avg_score_pct = int((total_obtained / total_possible) * 100)

weak_topics_list = get_weak_topics()
weak_topics_count = len(weak_topics_list)

col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.metric(label="Materials uploaded", value=str(materials_count))
with col2:
    with st.container(border=True):
        st.metric(label="Quizzes taken", value=str(quizzes_taken))
with col3:
    with st.container(border=True):
        st.metric(label="Avg. score", value=f"{avg_score_pct}%")
with col4:
    with st.container(border=True):
        st.metric(label="Weak topics", value=str(weak_topics_count))

st.write("")

col_left, col_right = st.columns([1.3, 1])

with col_left:
    with st.container(border=True):
        st.markdown("### Project objectives")
        st.write("")
        st.write("✔️ **Deliver AI-personalized study support:** Custom content summarization and contextual analogies based on student documents.")
        st.write("✔️ **Detect weak areas automatically:** Dynamically parses response errors and tags conceptual blindspots in SQLite.")
        st.write("✔️ **Generate adaptive study plans:** Creates customized daily tasks and hourly benchmarks matching logged weaknesses.")
        
    st.write("")
    
    with st.container(border=True):
        st.markdown("### Recent Activity")
        st.write("")
        if eval_history:
            for item in eval_history[-3:]:
                is_correct_sym = "✔️" if item["is_correct"] else "❌"
                st.markdown(f"**{item['topic']}** · Score: `{item['marks_obtained']:.1f}/{item['total_marks']:.1f}` · Status: {is_correct_sym} · *{item['evaluated_at'].split('T')[0]}*")
        else:
            st.info("No study history logged. Upload files and take a quiz to get started.")

with col_right:
    with st.container(border=True):
        st.markdown("### Continue learning")
        st.write("")
        all_quizzes = get_quizzes()
        resume_topic = "Algorithms"
        if all_quizzes:
            resume_topic = all_quizzes[0]["topic"]
        if st.button(f"Resume quiz: {resume_topic}", use_container_width=True):
            if all_quizzes:
                st.session_state.active_quiz_id = all_quizzes[0]["id"]
            st.switch_page("pages/4_AI_Evaluation.py")
        st.write("")
        if st.button("Ask the AI tutor", use_container_width=True):
            st.switch_page("pages/7_AI_Tutor.py")
            
    st.write("")
    
    with st.container(border=True):
        st.markdown("### Quick Actions")
        st.write("")
        col_qa1, col_qa2 = st.columns(2)
        with col_qa1:
            if st.button("📂 Upload notes", use_container_width=True):
                st.switch_page("pages/1_Study_Material.py")
        with col_qa2:
            if st.button("📊 Progress", use_container_width=True):
                st.switch_page("pages/8_Progress_Dashboard.py")
        
        st.write("")
        if st.button("⚙️ Manage settings", use_container_width=True):
            st.switch_page("pages/10_Settings.py")

st.sidebar.markdown("---")
st.sidebar.markdown("🎓 **EduAI v1.0.0**")
st.sidebar.markdown("Supporting SDG 4 Quality Education")
