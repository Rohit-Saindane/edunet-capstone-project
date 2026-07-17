import streamlit as st
import os
import json
import pandas as pd
from utils.gemini_client import generate_study_plan
from database.db_manager import (
    get_weak_topics, 
    save_study_plan, 
    get_active_study_plan, 
    get_setting
)
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="Study Plan - EduAI", page_icon="📅", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">📅 Study plan scheduler</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Translate SQLite concept error frequencies into dynamic daily revision timetables.</p>
</div>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

api_key = st.session_state.get("api_key", "")
weak_topics = get_weak_topics()

if not api_key:
    st.warning("Please configure your Gemini API Key in Settings to generate a personalized study plan.")
elif not weak_topics:
    with st.container(border=True):
        st.markdown("### 🎉 Perfect Record!")
        st.markdown("""
        No weak topics are currently registered in the database. 
        To populate the planner:
        1. Take a quiz from **❓ Quiz Generator**.
        2. Submit answers on the **✏️ AI Evaluation** page.
        3. If any answer is graded incorrect or has concept gaps, it will automatically sync here!
        """)
else:
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container(border=True):
            st.markdown("### ⚠️ Highlighted Weak Topics")
            for topic in weak_topics:
                st.error(f"**{topic['topic_name']}** (Errors: {topic['incorrect_count']}/{topic['total_tested']})")
                
        st.write("")
        with st.container(border=True):
            st.markdown("### ⚙️ Time Allocation")
            st.write("Configure revision settings:")
            hours_available = st.slider("Weekly revision hours available:", min_value=1, max_value=40, value=10)
            
            if st.button("🔄 Generate/Update Study Plan", use_container_width=True):
                with st.spinner("AI is organizing your customized revision calendar..."):
                    try:
                        plan_data = generate_study_plan(weak_topics, api_key)
                        if plan_data:
                            save_study_plan(
                                daily_schedule=json.dumps(plan_data.get("daily_schedule", {})),
                                weekly_goals=json.dumps(plan_data.get("weekly_goals", [])),
                                recommended_revision=plan_data.get("recommended_revision", ""),
                                est_completion_hours=float(plan_data.get("est_completion_hours", 0.0))
                            )
                            st.success("Study plan updated successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error generating study plan: {str(e)}")
                    
    with col2:
        active_plan = get_active_study_plan()
        if active_plan:
            with st.container(border=True):
                st.markdown("### 📅 Active Study Plan")
                st.markdown(f"""
                <div class="stat-container" style="margin-bottom:15px;">
                    <div class="stat-box">
                        <div class="stat-val">{active_plan['est_completion_hours']:.1f} hrs</div>
                        <div class="stat-label">Estimated Revision Time</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-val">{len(weak_topics)}</div>
                        <div class="stat-label">Weak Topics Addressed</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 🎯 Weekly Goals")
                try:
                    goals = json.loads(active_plan["weekly_goals"])
                    for g in goals:
                        st.markdown(f"- {g}")
                except:
                    st.write(active_plan["weekly_goals"])
                    
                st.markdown("#### 🗓️ Daily Schedule")
                try:
                    schedule = json.loads(active_plan["daily_schedule"])
                    days = list(schedule.keys())
                    tasks = list(schedule.values())
                    df = pd.DataFrame({"Day": days, "Revision Task": tasks})
                    st.table(df)
                except:
                    st.write(active_plan["daily_schedule"])
                    
                st.markdown("#### 💡 Revision Resources & Meta-Strategy")
                st.info(active_plan["recommended_revision"])
        else:
            st.info("No study plan active. Click the generate button on the left to create your custom schedule.")

st.sidebar.markdown("---")
st.sidebar.markdown("🎓 **EduAI v1.0.0**")
st.sidebar.markdown("Supporting SDG 4 Quality Education")
