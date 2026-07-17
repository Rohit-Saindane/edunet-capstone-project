import streamlit as st
import os
import pandas as pd
import plotly.express as px
from database.db_manager import (
    get_student_evaluation_history, 
    get_all_topics_performance,
    get_setting,
    get_quizzes
)
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="Progress Dashboard - EduAI", page_icon="📊", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">📊 Progress analytics</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Analyze score fluctuations, master metrics, and conceptual weak distributions.</p>
</div>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

history = get_student_evaluation_history()
topics_perf = get_all_topics_performance()

if not history:
    with st.container(border=True):
        st.markdown("### Progress Analytics Empty")
        st.write("Complete a quiz evaluation first to compile diagnostic analytics plots.")
        st.info("Head to the **📁 Study Material** page, upload a file, generate a quiz, and take it on the **✏️ AI Evaluation** page.")
else:
    df_hist = pd.DataFrame(history)
    df_hist["evaluated_at"] = pd.to_datetime(df_hist["evaluated_at"])
    
    quiz_scores = df_hist.groupby(["quiz_id", "topic", "evaluated_at"]).agg(
        obtained=('marks_obtained', 'sum'),
        total=('total_marks', 'sum')
    ).reset_index()
    quiz_scores["percentage"] = (quiz_scores["obtained"] / quiz_scores["total"]) * 100
    quiz_scores = quiz_scores.sort_values(by="evaluated_at")
    
    latest_score = int(quiz_scores.iloc[-1]["percentage"]) if not quiz_scores.empty else 0
    total_obtained = sum(quiz_scores["obtained"])
    total_possible = sum(quiz_scores["total"])
    avg_score_pct = int((total_obtained / total_possible) * 100) if total_possible > 0 else 0
    
    passed_count = sum(1 for p in quiz_scores["percentage"] if p >= 50)
    completion_pct = int((passed_count / len(quiz_scores)) * 100) if not quiz_scores.empty else 0
    
    unique_days = len(quiz_scores["evaluated_at"].dt.date.unique())
    streak_val = min(unique_days, 5)
    if streak_val == 0:
        streak_val = 1
        
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container(border=True):
            st.metric(label="Latest score", value=f"{latest_score}%")
    with col2:
        with st.container(border=True):
            st.metric(label="Average score", value=f"{avg_score_pct}%")
    with col3:
        with st.container(border=True):
            st.metric(label="Completion %", value=f"{completion_pct}%")
    with col4:
        with st.container(border=True):
            st.metric(label="Study streak", value=f"{streak_val} days")
            
    st.write("")
    
    col_chart, col_topics = st.columns([1.3, 1])
    
    with col_chart:
        with st.container(border=True):
            st.markdown("### Score trend over time")
            fig_score = px.line(
                quiz_scores,
                x="evaluated_at",
                y="percentage",
                hover_data=["topic"],
                markers=True,
                labels={"percentage": "Score (%)", "evaluated_at": "Attempt Date"}
            )
            theme = st.session_state.get("theme", "Dark")
            font_color = "#ffffff" if theme == "Dark" else "#0f172a"
            grid_color = "rgba(128,128,128,0.2)"
            
            fig_score.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color=font_color,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor=grid_color),
                yaxis=dict(showgrid=True, gridcolor=grid_color, range=[0, 105])
            )
            st.plotly_chart(fig_score, use_container_width=True)
            
        st.write("")
        with st.container(border=True):
            st.markdown("### Topic mastery")
            df_perf = pd.DataFrame(topics_perf)
            df_perf["correct"] = df_perf["total_tested"] - df_perf["incorrect_count"]
            df_perf["accuracy"] = (df_perf["correct"] / df_perf["total_tested"]) * 100
            
            fig_mastery = px.bar(
                df_perf,
                x="accuracy",
                y="topic_name",
                orientation="h",
                labels={"accuracy": "Accuracy %", "topic_name": "Subject/Topic"},
                color="accuracy",
                color_continuous_scale="Viridis"
            )
            fig_mastery.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color=font_color,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor=grid_color, range=[0, 105]),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_mastery, use_container_width=True)
            
    with col_topics:
        with st.container(border=True):
            st.markdown("### Weak topic error distribution")
            df_err = pd.DataFrame(topics_perf)
            df_err_filtered = df_err[df_err["incorrect_count"] > 0]
            if not df_err_filtered.empty:
                fig_err = px.pie(
                    df_err_filtered,
                    names="topic_name",
                    values="incorrect_count",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_err.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color=font_color,
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_err, use_container_width=True)
            else:
                st.info("No errors registered yet. Keep up the perfect scores!")
