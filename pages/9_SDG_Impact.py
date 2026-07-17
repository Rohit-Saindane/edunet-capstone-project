import streamlit as st
import os
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="SDG Impact - EduAI", page_icon="🌍", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">🌍 SDG 4 Quality Education Impact</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Bridging learning gaps and scaling personalized tutoring worldwide cost-effectively.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("### ⚠️ The Problem: Educational Bottlenecks")
        st.write("Quality education is the foundation of sustainable global development, yet modern systems face deep limitations:")
        st.write("1. **High Tutoring Costs:** 1-to-1 personalized teaching is highly effective but expensive. Lower-income students are often left behind.")
        st.write("2. **One-Size-Fits-All Pace:** Standard classrooms require instructors to teach at an average speed. Advanced students get bored, while struggling students fall behind.")
        st.write("3. **Lack of Actionable Evaluation:** Traditional grading notes if an answer is wrong but rarely reviews the student's explanation to explain the conceptual gap.")
        st.write("4. **Under-resourced Classrooms:** High student-to-teacher ratios make it impossible for teachers to track individual conceptual weak points across large classes.")

with col2:
    with st.container(border=True):
        st.markdown("### 💡 How AI Bridges the Gap")
        st.write("EduAI utilizes generative AI not to replace teachers, but to scale quality tutoring:")
        st.write("• **Costless 1-to-1 Tutoring:** Active 24/7. Any student with internet can upload their school textbook and receive grounded guidance.")
        st.write("• **RAG-Grounded Context:** Unlike standard chatbots that hallucinate, EduAI reads and queries specific course materials uploaded by the student.")
        st.write("• **Automated Concept Diagnostics:** By evaluating short answers and tagging mistake categories (e.g. 'Binary Search Base Case'), it identifies gaps early.")
        st.write("• **Individualized Schedules:** Translates detected weak points into custom weekly goals and revision hours automatically.")

st.write("")

with st.container(border=True):
    st.markdown("### 🚀 Project Integration with SDG 4 Targets")
    st.write("EduAI aligns with specific UN SDG 4 sub-targets:")
    st.write("- **Target 4.3 (Equal Access to Education):** Democratizes premium tools, making personalized summaries, tests, and detailed assessments free.")
    st.write("- **Target 4.4 (Increase Relevant Skills):** Helps students master complex concepts in fields like computing, math, and sciences through simple analogies and structured schedules.")
    st.write("- **Target 4.c (Educator Support):** Acts as an assistant tool for teachers, letting them see students' conceptual weaknesses and assign auto-generated quizzes.")

st.write("")

with st.container(border=True):
    st.markdown("### 🔮 Future Scope and Innovations")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("#### 🗣️ Voice-to-Voice Tutoring")
        st.write("Implement speech-to-text models to support students with reading difficulties or visual impairments, letting them talk to the tutor.")
    with col_s2:
        st.markdown("#### 🔗 LMS Integration")
        st.write("Sync student performance logs with Learning Management Systems (Canvas/Moodle), alerting teachers to specific classroom trends.")
    with col_s3:
        st.markdown("#### 🌐 Localized Offline Sync")
        st.write("Deploy small, quantized language models locally on budget laptops or mobile devices, resolving internet dependency in remote areas.")
