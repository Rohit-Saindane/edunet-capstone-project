import streamlit as st
import os
import shutil
from database.db_manager import save_setting, reset_database, get_setting
from utils.slide_generator import generate_presentation
from utils.report_generator import generate_report
from utils.vector_store import chunk_text, create_index
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="Settings - EduAI", page_icon="⚙️", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = get_setting("theme", "Dark")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">⚙️ Platform settings</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Manage API authorization keys, rebuild local index files, and export deliverables.</p>
</div>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

api_key = st.session_state.get("api_key", "")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("### 🎨 Theme Customization")
        theme_options = ["Light", "Dark"]
        current_theme = st.session_state.get("theme", "Dark")
        selected_theme = st.radio("Select Application Theme Mode:", theme_options, index=theme_options.index(current_theme))
        
        if selected_theme != current_theme:
            st.session_state.theme = selected_theme
            save_setting("theme", selected_theme)
            st.success(f"Theme switched to {selected_theme}!")
            st.rerun()
            
    st.write("")
    
    with st.container(border=True):
        st.markdown("### 🔑 API Authentication")
        current_key = st.session_state.get("api_key", "")
        mask_key = f"{current_key[:6]}...{current_key[-4:]}" if len(current_key) > 10 else ""
        st.write(f"Active Key Status: **{'🟢 Set' if current_key else '🔴 Not Configured'}** {f'({mask_key})' if mask_key else ''}")
        api_key_input = st.text_input("Enter Google Gemini API Key:", type="password")
        if st.button("Save API Key", use_container_width=True):
            if api_key_input.strip():
                st.session_state.api_key = api_key_input.strip()
                save_setting("api_key", api_key_input.strip())
                st.success("API Key saved!")
                st.rerun()
            else:
                st.error("Please enter a valid key.")
                
    st.write("")
    
    with st.container(border=True):
        st.markdown("### 🛠️ Rebuild Vector Store")
        st.write("Re-chunk and generate embeddings for all processed notes in the repository.")
        if st.button("Rebuild Index Store", use_container_width=True):
            if not api_key:
                st.error("Gemini API key is required to rebuild embedding vectors.")
            else:
                with st.spinner("Rebuilding indices..."):
                    try:
                        uploads_dir = "uploads"
                        if os.path.exists(uploads_dir):
                            txt_files = [f for f in os.listdir(uploads_dir) if f.endswith("_extracted.txt")]
                            for f in txt_files:
                                orig_name = f.replace("_extracted.txt", "")
                                with open(os.path.join(uploads_dir, f), "r", encoding="utf-8") as tf:
                                    text = tf.read()
                                chunks = chunk_text(text)
                                create_index(chunks, orig_name, api_key)
                            st.success(f"Indices rebuilt for {len(txt_files)} files!")
                        else:
                            st.info("No documents found to index.")
                    except Exception as e:
                        st.error(f"Rebuild failed: {str(e)}")

with col2:
    with st.container(border=True):
        st.markdown("### 📥 Project Deliverables Generator")
        st.write("Generate PowerPoint presentation slides or PDF reports for college exhibitions:")
        
        if st.button("📊 Generate PPT presentation", use_container_width=True):
            with st.spinner("Compiling slides..."):
                try:
                    generate_presentation()
                    st.success("Slides successfully compiled under `report/presentation.pptx`!")
                except Exception as e:
                    st.error(f"Failed: {str(e)}")
                    
        if st.button("📄 Generate academic PDF report", use_container_width=True):
            with st.spinner("Compiling PDF report..."):
                try:
                    generate_report()
                    st.success("PDF report successfully compiled under `report/report.pdf`!")
                except Exception as e:
                    st.error(f"Failed: {str(e)}")
                    
        st.write("")
        st.caption("Deliverables paths:")
        st.caption("- Slides: `report/presentation.pptx`")
        st.caption("- Report: `report/report.pdf`")
        
    st.write("")
    
    with st.container(border=True):
        st.markdown("### 🗑️ Wipe cached database data")
        st.warning("Warning: Resetting the database will delete all uploaded files, quiz histories, evaluations, and personalized calendars. This action cannot be undone.")
        if st.button("Reset Database & Uploads", use_container_width=True):
            try:
                reset_database()
                if os.path.exists("uploads"):
                    shutil.rmtree("uploads")
                    os.makedirs("uploads", exist_ok=True)
                st.session_state.current_file = ""
                st.session_state.active_quiz_id = None
                st.session_state.chat_history = []
                st.session_state.cached_summaries = {}
                st.session_state.student_responses = {}
                st.session_state.quiz_evaluated_items = []
                st.session_state.current_question_idx = 0
                st.session_state.quiz_taking_started = False
                save_setting("current_file", "")
                st.success("System data reset completed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Reset failed: {str(e)}")
