import streamlit as st
import os
import json
from utils.vector_store import retrieve_context
from utils.gemini_client import ask_tutor
from database.db_manager import get_setting
from utils.theme_manager import inject_theme, load_branding

st.set_page_config(page_title="AI Tutor - EduAI", page_icon="💬", layout="wide")

inject_theme()
load_branding()

if "api_key" not in st.session_state or not st.session_state.api_key:
    db_key = get_setting("api_key", "")
    if db_key:
        st.session_state.api_key = db_key
    else:
        st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

active_file = st.session_state.get("current_file", "")
api_key = st.session_state.get("api_key", "")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if not active_file:
    st.warning("Please upload a study material PDF/TXT file first in the Study Material page to tutor from context.")
else:
    st.sidebar.markdown("### 🎭 Tutor Persona")
    tutor_persona = st.sidebar.radio(
        "Select Tutoring Style:",
        ["Standard", "Simple Words", "Age 10", "Give another example"]
    )
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.success("Cleared.")
        st.rerun()

    col1, col2 = st.columns([3, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### ⚡ Quick Prompts")
            quick_prompts = [
                "Explain in simple terms.",
                "Give another real-world example.",
                "Explain like I'm 10 years old.",
                "What is the core takeaway of this text?"
            ]
            selected_prompt = None
            for p in quick_prompts:
                if st.button(p, use_container_width=True):
                    selected_prompt = p
                    
    with col1:
        with st.container(border=True):
            st.markdown("""
            <div style="display:flex;align-items:center;gap:8px;border-bottom:1.5px solid rgba(128,128,128,0.15);padding-bottom:10px;margin-bottom:15px;">
              <div style="font-size:20px;">💬</div>
              <div>
                <p style="font-size:14px;font-weight:600;margin:0">AI tutor</p>
                <p style="font-size:11px;color:var(--text-muted);margin:0">Grounded in your uploaded material</p>
              </div>
            </div>
            """, unsafe_allow_html=True)
            
            chat_container = st.container(height=350)
            with chat_container:
                for msg in st.session_state.chat_history:
                    role = msg["role"]
                    if role == "user":
                        st.markdown(f"""
                        <div style="align-self:flex-end;background:#4f46e5;color:#ffffff;border-radius:12px 12px 2px 12px;padding:8px 12px;font-size:13px;max-width:75%;margin-left:auto;margin-bottom:12px;">
                          {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="align-self:flex-start;background:rgba(255,255,255,0.04);border:0.5px solid rgba(128,128,128,0.2);border-radius:12px 12px 12px 2px;padding:8px 12px;font-size:13px;max-width:80%;margin-right:auto;margin-bottom:12px;">
                          {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                        
            user_input = st.chat_input("Ask about your uploaded notes...")
            if selected_prompt:
                user_input = selected_prompt
                
            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                response_text = ""
                with st.spinner("Thinking..."):
                    rag_succeeded = False
                    if api_key:
                        try:
                            retrieved_context = retrieve_context(
                                query=user_input,
                                file_name=active_file,
                                api_key=api_key,
                                top_k=3
                            )
                            response_text = ask_tutor(
                                query=user_input,
                                context=retrieved_context,
                                chat_history=st.session_state.chat_history[:-1],
                                persona=tutor_persona,
                                api_key=api_key
                            )
                            if "Tutor is currently offline" not in response_text:
                                rag_succeeded = True
                        except Exception as e:
                            pass
                    
                    if not rag_succeeded:
                        st.warning("AI service temporarily unavailable. Running offline explanation mode.")
                        index_path = os.path.join("uploads", f"{active_file}_index.json")
                        matched_chunks = []
                        if os.path.exists(index_path):
                            try:
                                with open(index_path, "r", encoding="utf-8") as f:
                                    index_data = json.load(f)
                                chunks = index_data.get("chunks", [])
                                query_words = [w.lower() for w in user_input.split() if len(w) > 2]
                                chunk_scores = []
                                for idx, chunk in enumerate(chunks):
                                    score = sum(1 for w in query_words if w in chunk.lower())
                                    chunk_scores.append((score, chunk))
                                chunk_scores.sort(key=lambda x: x[0], reverse=True)
                                top_matches = [c for s, c in chunk_scores[:2] if s > 0]
                                if top_matches:
                                    matched_chunks = top_matches
                            except:
                                pass
                        
                        if matched_chunks:
                            response_text = "📚 **Offline Content Match Found:**\n\n"
                            for mc in matched_chunks:
                                response_text += f"> {mc}\n\n"
                            response_text += "\n*Note: The Gemini API is currently unavailable or quota limit is reached. Running local search.*"
                        else:
                            response_text = "⚠️ Gemini API connection is unavailable or quota is exceeded, and no matching offline context could be retrieved for this query. Please check your settings."

                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                st.rerun()
