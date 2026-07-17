import streamlit as st
import os
from database.db_manager import get_all_topics_performance, get_setting
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="Weak Topics - EduAI", page_icon="🎯", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">🎯 Weak topics diagnostics</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Understand where your conceptual understanding stands based on automated error tracking.</p>
</div>
""", unsafe_allow_html=True)

topics = get_all_topics_performance()

if not topics:
    st.info("No topic records found in the database. Complete some quizzes on the AI Evaluation page to populate these diagnostics.")
else:
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.markdown("### Conceptual Gaps Analysis")
        st.write("")
        for t in topics:
            tot = t["total_tested"]
            inc = t["incorrect_count"]
            corr = tot - inc
            pct = int((corr / tot) * 100) if tot > 0 else 0
            
            if pct < 50:
                card_class = "custom-alert-danger"
                status_label = "🔴 Critical Gaps (High Revision Priority)"
                border_color = "#ef4444"
            elif pct < 75:
                card_class = "custom-alert-warning"
                status_label = "🟡 Medium Gaps (Moderate Revision Priority)"
                border_color = "#fbbf24"
            else:
                card_class = "custom-alert-success"
                status_label = "🟢 Solid Understanding (Low Revision Priority)"
                border_color = "#10b981"
                
            with st.container(border=True):
                st.markdown(f"#### **{t['topic_name']}**")
                st.write(status_label)
                st.write(f"Accuracy: **{pct}%** ({corr} correct, {inc} incorrect out of {tot} questions)")
                if t["concept_notes"]:
                    st.markdown(f"**AI Concept Notes:** *{t['concept_notes']}*")
                
    with col_r:
        with st.container(border=True):
            st.markdown("### Revision Strategies")
            st.write("")
            st.write("📋 **For High Priority (Red):**")
            st.write("Go back to the Summarizer page, open the 'ELI10' and 'Key Concepts' tabs. Re-read the chapters slowly, then ask the AI tutor to give you simpler real-world examples.")
            st.write("")
            st.write("📋 **For Moderate Priority (Orange):**")
            st.write("Try creating a quiz focused specifically on this topic with 5 questions on Easy/Medium settings. Review the explanations for any mistakes immediately.")
            st.write("")
            st.write("📋 **For Low Priority (Green):**")
            st.write("These concepts are well understood. Focus on maintainence via quick revision plans.")

st.sidebar.markdown("---")
st.sidebar.markdown("🎓 **EduAI v1.0.0**")
st.sidebar.markdown("Supporting SDG 4 Quality Education")
