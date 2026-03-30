"""
╔══════════════════════════════════════════════════════════════╗
║        HR RECRUITING AGENT — SETTINGS PAGE                   ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.core import load_resumes, RESUME_FOLDER

st.set_page_config(
    page_title="Settings · ARIA",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;600;700;800;900&family=JetBrains+Mono:wght@300;400;500&display=swap');
:root {
    --bg:#050B14; --bg2:#080F1C; --bg3:#0C1628;
    --border:#0F2338; --border2:#1A3A5C;
    --teal:#00D4B4; --teal2:#00897B;
    --text:#E2E8F0; --muted:#64748B; --muted2:#94A3B8;
}
html, body, [class*="css"] {
    font-family:'Space Grotesk',sans-serif;
    background:var(--bg) !important;
    color:var(--text) !important;
}
.main .block-container { padding-top:1.5rem; max-width:900px; background:transparent !important; }
.stTextInput input {
    background:var(--bg3) !important; border:1px solid var(--border2) !important;
    color:var(--text) !important; border-radius:8px !important;
    font-family:'JetBrains Mono',monospace !important; font-size:0.85rem !important;
}
label { font-size:0.65rem !important; letter-spacing:1.5px !important;
text-transform:uppercase !important; color:var(--muted) !important;
font-family:'Orbitron',monospace !important; font-weight:600 !important; }
.stButton > button {
    background:linear-gradient(135deg,var(--teal2),var(--teal)) !important;
    color:var(--bg) !important; border:none !important; border-radius:8px !important;
    font-family:'Orbitron',monospace !important; font-weight:700 !important;
    font-size:0.7rem !important; letter-spacing:1px !important;
    padding:10px 20px !important;
}
hr { border-color:var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:28px;">
  <div style="font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;
  letter-spacing:-0.5px;color:#E2E8F0;">
    SYSTEM <span style="color:#00D4B4;">SETTINGS</span>
  </div>
  <div style="font-size:0.7rem;color:#475569;letter-spacing:2px;text-transform:uppercase;
  margin-top:4px;font-family:'Orbitron',monospace;">
    API Configuration · Resume Management · Agent Preferences
  </div>
</div>
""", unsafe_allow_html=True)


col_left, col_right = st.columns([1.2, 1])

# ─────────────────────────────────────────────────────────────────────────────
# LEFT COLUMN — API + Settings
# ─────────────────────────────────────────────────────────────────────────────
with col_left:

    # ── API KEY ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#080F1C;border:1px solid #0F2338;border-radius:12px;
    padding:20px 24px;margin-bottom:16px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;
      color:#00D4B4;margin-bottom:14px;">🔑 API CONFIGURATION</div>
    """, unsafe_allow_html=True)

    # Auto-detect key
    auto_key = ""
    try:
        auto_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    if not auto_key:
        auto_key = os.getenv("GROQ_API_KEY", "")

    if auto_key:
        st.success("✅ Groq API key auto-detected")
        st.markdown(f"""
        <div style="background:#0C1628;border:1px solid #1A3A5C;border-radius:8px;
        padding:10px 14px;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#475569;">
        {auto_key[:8]}{'•' * 20}
        </div>
        """, unsafe_allow_html=True)
    else:
        manual = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            value=st.session_state.get("manual_groq_key", ""),
            help="Get your free key at console.groq.com"
        )
        if manual:
            st.session_state["manual_groq_key"] = manual
            st.success("✅ Key saved for this session")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── MODEL INFO ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#080F1C;border:1px solid #0F2338;border-radius:12px;
    padding:20px 24px;margin-bottom:16px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;
      color:#00D4B4;margin-bottom:14px;">🧠 MODEL STACK</div>
    """, unsafe_allow_html=True)

    stack = [
        ("LLM", "llama-3.3-70b-versatile", "Groq", "Free tier"),
        ("STT", "whisper-large-v3-turbo", "Groq", "Free tier"),
        ("TTS", "Google TTS (gTTS)", "Google", "100% Free"),
        ("Vector", "FAISS", "Local", "No API needed"),
    ]

    for label, model, provider, cost in stack:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
        padding:8px 0;border-bottom:1px solid #0C1628;">
          <div>
            <span style="font-family:'Orbitron',monospace;font-size:0.55rem;letter-spacing:2px;
            color:#475569;">{label}</span>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;
            color:#94A3B8;margin-top:2px;">{model}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:0.72rem;color:#475569;">{provider}</div>
            <div style="font-size:0.65rem;color:#10B981;">{cost}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── SESSION CONTROLS ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#080F1C;border:1px solid #0F2338;border-radius:12px;
    padding:20px 24px;margin-bottom:16px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;
      color:#00D4B4;margin-bottom:14px;">⚡ SESSION CONTROLS</div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear Results"):
            for key in ["results", "active_jd", "chat_history", "voice_transcript", "use_voice_as_jd"]:
                st.session_state.pop(key, None)
            st.success("Session cleared!")
    with c2:
        if st.button("🔄 Reset Chat"):
            st.session_state["chat_history"] = []
            st.success("Chat reset!")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN — Resume Folder
# ─────────────────────────────────────────────────────────────────────────────
with col_right:

    # ── RESUME FOLDER STATUS ──────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#080F1C;border:1px solid #0F2338;border-radius:12px;
    padding:20px 24px;margin-bottom:16px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;
      color:#00D4B4;margin-bottom:14px;">📁 RESUME FOLDER</div>
    """, unsafe_allow_html=True)

    resumes = load_resumes()
    folder_exists = RESUME_FOLDER.exists()

    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;
    color:#475569;margin-bottom:10px;">
    Path: <span style="color:#00897B;">sample_resumes/</span><br>
    Status: <span style="color:{'#10B981' if folder_exists else '#EF4444'};">
    {'✅ Found' if folder_exists else '❌ Missing'}</span><br>
    Count: <span style="color:#E2E8F0;">{len(resumes)} PDF(s)</span>
    </div>
    """, unsafe_allow_html=True)

    if resumes:
        for r in resumes:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
            padding:7px 10px;background:#0C1628;border-radius:6px;margin-bottom:4px;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.73rem;
              color:#64748B;">📄 {r['filename']}</span>
              <span style="font-family:'Orbitron',monospace;font-size:0.55rem;
              color:#00897B;letter-spacing:1px;">PDF</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No PDFs detected. Add resumes to `sample_resumes/` folder.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── INSTRUCTIONS ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#080F1C;border:1px solid #0F2338;border-radius:12px;
    padding:20px 24px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;
      color:#00D4B4;margin-bottom:14px;">📖 QUICK GUIDE</div>
      <div style="font-size:0.82rem;color:#475569;line-height:2;">
        <strong style="color:#64748B;">01</strong> &nbsp;Add PDF resumes to <code style="color:#00897B;font-size:0.75rem;">sample_resumes/</code><br>
        <strong style="color:#64748B;">02</strong> &nbsp;Set Groq API key above or in <code style="color:#00897B;font-size:0.75rem;">.env</code><br>
        <strong style="color:#64748B;">03</strong> &nbsp;Go to Voice Hub → paste or speak JD<br>
        <strong style="color:#64748B;">04</strong> &nbsp;Click ACTIVATE PIPELINE<br>
        <strong style="color:#64748B;">05</strong> &nbsp;View results → Chat with ARIA<br>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;font-family:'Orbitron',monospace;font-size:0.55rem;
letter-spacing:2px;color:#0F2338;">
ARIA HR AGENT · BUILT WITH GROQ · WHISPER · gTTS · STREAMLIT
</div>
""", unsafe_allow_html=True)
