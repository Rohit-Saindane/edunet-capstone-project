import streamlit as st
import os

def inject_theme():
    # Only keep the advanced UI layout and component styling (cards, animations)
    # Streamlit's native config.toml handles all base text/background contrasts now.
    css_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Polished Main Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0f172a 0%, #090a0f 100%) !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Highlighted active link */
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
        background-color: rgba(99, 102, 241, 0.2) !important;
        color: #818cf8 !important;
        border-radius: 6px;
    }

    /* Metric & Form Wrapper Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 24px !important;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5) !important;
        transition: border-color 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(99, 102, 241, 0.25) !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }

    /* Premium Buttons Micro-Animations */
    button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2), 0 2px 4px -1px rgba(79, 70, 229, 0.1) !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4), 0 4px 6px -2px rgba(79, 70, 229, 0.2) !important;
        opacity: 0.95 !important;
    }
    button[data-testid="baseButton-secondary"]:active {
        transform: translateY(0) !important;
    }
    
    /* SDG Banner */
    .sdg-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.2) 100%);
        border-radius: 12px;
        padding: 18px 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border: 0.5px solid rgba(52, 211, 153, 0.2);
    }
    .sdg-banner-title {
        font-size: 12px;
        font-weight: 600;
        color: #34d399 !important;
        margin: 0 0 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .sdg-banner-text {
        font-size: 15px;
        font-weight: 600;
        color: #ffffff !important;
        margin: 0;
    }

    /* Custom Custom Alerts Styling */
    .custom-alert-danger {
        background-color: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        color: #f87171 !important;
        margin-bottom: 12px;
    }
    .custom-alert-warning {
        background-color: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        color: #fbbf24 !important;
        margin-bottom: 12px;
    }
    .custom-alert-success {
        background-color: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        color: #34d399 !important;
        margin-bottom: 12px;
    }

    /* Upload box dashed border polish */
    .upload-dashed-box {
        border: 1.5px dashed rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 24px 16px;
        text-align: center;
        background-color: rgba(255, 255, 255, 0.02);
        transition: border-color 0.3s ease;
    }
    .upload-dashed-box:hover {
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    /* Stats grid */
    .stat-container {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .stat-box {
        flex: 1;
        min-width: 150px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stat-box:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    .stat-val {
        font-size: 24px;
        font-weight: 700;
        color: #818cf8 !important;
        margin-bottom: 4px;
    }
    .stat-label {
        font-size: 11px;
        color: #94a3b8 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* AI Chat Bubbles */
    .chat-bubble-tutor {
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px 12px 12px 2px;
        padding: 10px 14px;
        font-size: 13.5px;
        max-width: 80%;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .chat-bubble-user {
        background-color: #4f46e5;
        color: #ffffff !important;
        border-radius: 12px 12px 2px 12px;
        padding: 10px 14px;
        font-size: 13.5px;
        max-width: 75%;
        margin-left: auto;
        margin-bottom: 12px;
        line-height: 1.5;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25);
    }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

def load_branding():
    st.sidebar.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:12px 8px;border-bottom:1px solid rgba(255,255,255,0.15);margin-bottom:20px;">
      <div style="width:32px;height:32px;border-radius:8px;background:#4f46e5;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:16px;">🧠</div>
      <span style="font-weight:700;font-size:18px;color:#f1f5f9;letter-spacing:-0.03em;">EduAI</span>
    </div>
    """, unsafe_allow_html=True)
