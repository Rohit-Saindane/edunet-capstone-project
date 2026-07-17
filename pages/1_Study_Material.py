import streamlit as st
import os
import shutil
from utils.text_extractor import extract_text
from utils.vector_store import chunk_text, create_index
from database.db_manager import get_setting, save_setting
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="Study Material - EduAI", page_icon="📁", layout="wide")

inject_theme()
load_branding()

st.markdown("""
<div style='margin-bottom: 20px;'>
    <p style="font-size:18px;font-weight:600;margin:0 0 4px">Study material</p>
    <p style="font-size:13px;color:var(--text-secondary);margin:0">Upload a PDF or text file to generate notes, quizzes, and tutoring context.</p>
</div>
""", unsafe_allow_html=True)

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

col1, col2 = st.columns([1, 1.2])

with col1:
    with st.container(border=True):
        st.markdown("### Upload new files")
        uploaded_file = st.file_uploader("Drop PDF or TXT here (Max 25MB)", type=["pdf", "txt"])
        
        if uploaded_file is not None:
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Uploaded: {uploaded_file.name}")
            
            if st.button("Process Document", use_container_width=True):
                with st.spinner("Processing..."):
                    try:
                        text = extract_text(file_path)
                        if text.strip():
                            extracted_txt_path = os.path.join("uploads", f"{uploaded_file.name}_extracted.txt")
                            with open(extracted_txt_path, "w", encoding="utf-8") as tf:
                                tf.write(text)
                            api_key = st.session_state.get("api_key", "")
                            if api_key:
                                chunks = chunk_text(text)
                                create_index(chunks, uploaded_file.name, api_key)
                            st.session_state.current_file = uploaded_file.name
                            save_setting("current_file", uploaded_file.name)
                            st.success("Successfully processed!")
                            st.rerun()
                        else:
                            st.error("Text extraction returned empty content.")
                    except Exception as e:
                        st.error(f"Failed: {str(e)}")

with col2:
    with st.container(border=True):
        st.markdown("### Processed documents")
        
        uploads_dir = "uploads"
        files = []
        if os.path.exists(uploads_dir):
            files = [f for f in os.listdir(uploads_dir) if f.endswith("_extracted.txt")]
            
        if files:
            theme = st.session_state.get("theme", "Dark")
            text_color = "#ffffff" if theme == "Dark" else "#0f172a"
            card_bg = "rgba(255,255,255,0.06)" if theme == "Dark" else "#f8fafc"
            
            for f in files:
                orig_name = f.replace("_extracted.txt", "")
                size_kb = os.path.getsize(os.path.join(uploads_dir, f)) // 1024
                is_active = (orig_name == st.session_state.get("current_file", ""))
                
                border_color = "#4f46e5" if is_active else "rgba(128,128,128,0.2)"
                icon_emoji = "📕" if orig_name.lower().endswith(".pdf") else "📘"
                
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;border-radius:8px;padding:10px 12px;margin-bottom:8px;background:{card_bg};border:1px solid {border_color};">
                  <div style="font-size:18px;">{icon_emoji}</div>
                  <div style="flex:1">
                    <p style="font-size:12.5px;margin:0;font-weight:600;color:{text_color};">{orig_name}</p>
                    <p style="font-size:11px;color:#94a3b8;margin:0">{size_kb} KB · Processed</p>
                  </div>
                  <div style="color:#10b981;font-weight:bold;font-size:14px;">✓</div>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if not is_active:
                        if st.button(f"Activate", key=f"act_{orig_name}", use_container_width=True):
                            st.session_state.current_file = orig_name
                            save_setting("current_file", orig_name)
                            st.rerun()
                    else:
                        st.markdown("<p style='font-size:12px;color:#10b981;font-weight:bold;text-align:center;'>Active</p>", unsafe_allow_html=True)
                with col_btn2:
                    if st.button(f"Reprocess", key=f"rep_{orig_name}", use_container_width=True):
                        with st.spinner("Reprocessing..."):
                            try:
                                raw_path = os.path.join(uploads_dir, orig_name)
                                if os.path.exists(raw_path):
                                    text = extract_text(raw_path)
                                    extracted_txt_path = os.path.join(uploads_dir, f"{orig_name}_extracted.txt")
                                    with open(extracted_txt_path, "w", encoding="utf-8") as tf:
                                        tf.write(text)
                                    api_key = st.session_state.get("api_key", "")
                                    if api_key:
                                        chunks = chunk_text(text)
                                        create_index(chunks, orig_name, api_key)
                                    st.success("Reprocessed successfully!")
                                    st.rerun()
                                else:
                                    st.error("Source file not found.")
                            except Exception as e:
                                st.error(f"Failed: {str(e)}")
                with col_btn3:
                    if st.button(f"Delete", key=f"del_{orig_name}", use_container_width=True):
                        try:
                            paths_to_delete = [
                                os.path.join(uploads_dir, orig_name),
                                os.path.join(uploads_dir, f"{orig_name}_extracted.txt"),
                                os.path.join(uploads_dir, f"{orig_name}_index.json")
                            ]
                            for path in paths_to_delete:
                                if os.path.exists(path):
                                    os.remove(path)
                            if is_active:
                                st.session_state.current_file = ""
                                save_setting("current_file", "")
                            st.success(f"Deleted {orig_name}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {str(e)}")
                st.write("")
        else:
            st.info("No processed files found. Please upload a file to start.")
