"""
╔══════════════════════════════════════════════════════════════╗
║        HR RECRUITING AGENT — VOICE HUB (Main Page)          ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from utils.core import (
    load_resumes, transcribe_audio, text_to_speech,
    run_pipeline, score_cls, tags_html
)


def get_groq_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    return st.session_state.get("manual_groq_key", "")


st.set_page_config(
    page_title="ARIA · HR Agent",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --bg:#050B14; --bg2:#080F1C; --bg3:#0C1628;
    --border:#0F2338; --border2:#1A3A5C;
    --teal:#00D4B4; --teal2:#00897B;
    --text:#E2E8F0; --muted:#64748B; --muted2:#94A3B8;
    --red:#EF4444; --green:#10B981; --amber:#F59E0B;
}

html, body, [class*="css"] {
    font-family:'Space Grotesk',sans-serif;
    background:var(--bg) !important;
    color:var(--text) !important;
}
.main .block-container { padding-top:1.5rem; max-width:1200px; background:transparent !important; }

section[data-testid="stSidebar"] { background:var(--bg2) !important; border-right:1px solid var(--border) !important; }
section[data-testid="stSidebar"] * { color:var(--muted2) !important; }
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextArea textarea {
    background:var(--bg3) !important; border:1px solid var(--border2) !important;
    color:var(--text) !important; border-radius:8px !important;
    font-family:'JetBrains Mono',monospace !important; font-size:0.82rem !important;
}
section[data-testid="stSidebar"] label {
    font-size:0.65rem !important; letter-spacing:1.5px !important;
    text-transform:uppercase !important; color:var(--muted) !important;
    font-weight:600 !important; font-family:'Orbitron',monospace !important;
}

.stButton > button {
    background:linear-gradient(135deg,var(--teal2),var(--teal)) !important;
    color:var(--bg) !important; border:none !important; border-radius:8px !important;
    font-family:'Orbitron',monospace !important; font-weight:700 !important;
    font-size:0.75rem !important; letter-spacing:1px !important;
    padding:12px 24px !important; transition:all 0.3s ease !important;
}
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 25px rgba(0,212,180,0.35) !important; }
.stProgress > div > div { background:var(--teal) !important; }

.tag { display:inline-block; background:var(--bg3); color:var(--muted2); font-size:0.7rem; padding:3px 10px; border-radius:20px; margin:2px 3px 2px 0; border:1px solid var(--border); font-family:'JetBrains Mono',monospace; }
.tag-r { background:rgba(239,68,68,0.1); color:#FCA5A5; border-color:rgba(239,68,68,0.3); }
.tag-g { background:rgba(16,185,129,0.1); color:#6EE7B7; border-color:rgba(16,185,129,0.3); }
.lbl { font-size:0.6rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--muted); margin:12px 0 5px 0; font-family:'Orbitron',monospace; }
.verdict { font-size:0.87rem; color:var(--muted2); line-height:1.7; }
.s-high { color:var(--green); } .s-mid { color:var(--amber); } .s-low { color:var(--red); }

.pipeline { display:flex; align-items:center; gap:8px; margin:20px 0; flex-wrap:wrap; }
.pnode { background:var(--bg3); color:var(--muted); font-size:0.68rem; font-weight:600; padding:6px 14px; border-radius:20px; font-family:'Orbitron',monospace; letter-spacing:0.5px; border:1px solid var(--border); transition:all 0.4s; }
.pnode.active { background:rgba(0,212,180,0.15); color:var(--teal); border-color:var(--teal2); box-shadow:0 0 12px rgba(0,212,180,0.2); }
.parr { color:var(--border2); font-size:1rem; }
hr { border-color:var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:800;color:#00D4B4;letter-spacing:2px;margin-bottom:4px;">ARIA</div>
    <div style="font-size:0.65rem;color:#475569;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:20px;">HR Recruiting Agent · v2.0</div>
    """, unsafe_allow_html=True)

    st.markdown("##### 🔑 API Key")
    auto_key = get_groq_key()
    if auto_key:
        st.success("✅ Groq key loaded")
    else:
        manual = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        st.session_state["manual_groq_key"] = manual

    st.divider()
    st.markdown("##### 📁 Resumes")
    resumes = load_resumes()
    if resumes:
        st.success(f"✅ {len(resumes)} resume(s) detected")
        for r in resumes:
            st.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.75rem;color:#475569;'>→ {r['filename']}</span>", unsafe_allow_html=True)
    else:
        st.warning("No PDFs in `sample_resumes/`")

    st.divider()
    st.markdown("##### 📋 Job Description")
    jd_text = st.text_area("Paste JD", height=200, label_visibility="collapsed", placeholder="Senior Python Engineer with 5+ years experience...")

    st.divider()
    st.markdown("##### 🔊 Voice Settings")
    voice_enabled = st.toggle("Voice Output", value=True)
    st.caption("Agent speaks results aloud after screening.")

    st.divider()
    run_btn = st.button("⚡  ACTIVATE PIPELINE")

    st.divider()
    st.markdown('<div style="font-size:0.65rem;color:#1E3A5F;letter-spacing:1px;line-height:1.8;">GROQ · llama-3.3-70b<br>WHISPER · large-v3-turbo<br>gTTS · Google TTS</div>', unsafe_allow_html=True)


# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:28px;">
  <div style="font-family:'Orbitron',monospace;font-size:2.2rem;font-weight:900;letter-spacing:-1px;line-height:1.1;color:#E2E8F0;">
    ARIA <span style="color:#00D4B4;">RECRUITER</span>
  </div>
  <div style="font-size:0.8rem;color:#475569;letter-spacing:2px;text-transform:uppercase;margin-top:6px;font-family:'Orbitron',monospace;">
    Autonomous · Intelligent · Voice-Enabled · HR Agent
  </div>
</div>
""", unsafe_allow_html=True)


# ── WAVEFORM ──────────────────────────────────────────────────────────────────
is_running = st.session_state.get("pipeline_running", False)
waveform_color = "#00D4B4" if not is_running else "#F59E0B"
status_word    = "READY" if not is_running else "ACTIVE"
label_word     = "LISTENING" if not is_running else "PROCESSING"

bars_html = "".join([
    f'<div id="bar{i}" style="width:4px;border-radius:4px;background:{waveform_color};opacity:0.85;height:20px;"></div>'
    for i in range(32)
])

base_h = [12,18,28,38,48,52,56,60,56,52,44,36,44,52,56,60,56,48,40,36,44,52,56,60,52,44,36,28,20,16,12,10]

st.components.v1.html(f"""
<div style="display:flex;flex-direction:column;align-items:center;padding:20px 0 10px 0;">
  <div style="font-family:monospace;font-size:0.55rem;letter-spacing:3px;color:#1E3A5F;margin-bottom:14px;text-transform:uppercase;">{label_word}</div>
  <div style="display:flex;align-items:center;gap:4px;height:64px;">
    {bars_html}
  </div>
  <div style="display:flex;gap:30px;margin-top:18px;">
    <div style="text-align:center;">
      <div style="font-family:monospace;font-size:0.55rem;letter-spacing:2px;color:#1E3A5F;">STATUS</div>
      <div style="font-family:monospace;font-size:0.75rem;font-weight:700;color:{'#00D4B4' if not is_running else '#F59E0B'};">{status_word}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-family:monospace;font-size:0.55rem;letter-spacing:2px;color:#1E3A5F;">RESUMES</div>
      <div style="font-family:monospace;font-size:0.75rem;font-weight:700;color:#E2E8F0;">{len(resumes):02d}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-family:monospace;font-size:0.55rem;letter-spacing:2px;color:#1E3A5F;">ENGINE</div>
      <div style="font-family:monospace;font-size:0.75rem;font-weight:700;color:#E2E8F0;">GROQ</div>
    </div>
  </div>
</div>
<style>body{{background:transparent!important;margin:0;}}</style>
<script>
const bh = {base_h};
const bars = bh.map((_,i)=>document.getElementById('bar'+i));
function animate(){{
  const t = Date.now()/1000;
  bars.forEach((b,i)=>{{
    if(!b)return;
    const w  = Math.sin(t*2.5+i*0.4)*0.5+0.5;
    const w2 = Math.sin(t*1.8+i*0.6+1)*0.3+0.3;
    b.style.height = (bh[i]*(0.3+(w+w2)/1.3*0.85))+'px';
  }});
  requestAnimationFrame(animate);
}}
animate();
</script>
""", height=145)


# ── VOICE INPUT ───────────────────────────────────────────────────────────────
col_v, col_sep, col_t = st.columns([3, 0.2, 3])

with col_v:
    st.markdown('<div style="font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:2px;color:#00D4B4;margin-bottom:10px;text-transform:uppercase;">🎙️ Voice Input</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.82rem;color:#475569;margin-bottom:10px;">Describe the role and candidate requirements verbally.</div>', unsafe_allow_html=True)

    audio_input = st.audio_input("Record your JD")
    if audio_input is not None:
        groq_key = get_groq_key()
        if not groq_key:
            st.error("Enter Groq API key in the sidebar.")
        else:
            with st.spinner("Transcribing with Whisper..."):
                try:
                    transcript = transcribe_audio(groq_key, audio_input.read(), "recording.wav")
                    st.session_state["voice_transcript"] = transcript
                    st.success("✅ Transcribed")
                except Exception as e:
                    st.error(f"STT error: {e}")

    if st.session_state.get("voice_transcript"):
        st.markdown(f'<div style="background:#080F1C;border:1px solid #1A3A5C;border-radius:10px;padding:14px;font-size:0.85rem;color:#94A3B8;font-style:italic;margin-top:10px;">🗣️ <strong style="color:#00D4B4;">Transcript:</strong><br>{st.session_state["voice_transcript"]}</div>', unsafe_allow_html=True)
        if st.button("📋 Use as JD"):
            st.session_state["use_voice_as_jd"] = True
            st.rerun()

with col_sep:
    st.markdown("<div style='text-align:center;color:#1A3A5C;padding-top:80px;font-size:1.4rem;'>⋮</div>", unsafe_allow_html=True)

with col_t:
    st.markdown('<div style="font-family:Orbitron,monospace;font-size:0.65rem;letter-spacing:2px;color:#00D4B4;margin-bottom:10px;text-transform:uppercase;">📋 Text Input</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.82rem;color:#475569;">Or paste your full job description in the sidebar text area on the left.</div>', unsafe_allow_html=True)
    st.markdown('<div style="background:#080F1C;border:1px dashed #0F2338;border-radius:10px;padding:24px;color:#1E3A5F;font-size:0.82rem;margin-top:10px;line-height:1.9;">← Open sidebar<br>→ Paste JD in text area<br>→ Click ACTIVATE PIPELINE</div>', unsafe_allow_html=True)

st.divider()

# ── PIPELINE NODES ────────────────────────────────────────────────────────────
active_node = st.session_state.get("active_node", -1)
def nc(i): return "active" if i == active_node else ""

st.markdown(f"""
<div class="pipeline">
  <span class="pnode {nc(0)}">📝 JD ANALYZER</span><span class="parr">→</span>
  <span class="pnode {nc(1)}">👤 RESUME PARSER</span><span class="parr">→</span>
  <span class="pnode {nc(2)}">🚩 REDFLAG DETECTOR</span><span class="parr">→</span>
  <span class="pnode {nc(3)}">🎯 RECRUITER AGENT</span>
</div>
""", unsafe_allow_html=True)


# ── RUN PIPELINE ──────────────────────────────────────────────────────────────
if run_btn:
    groq_key  = get_groq_key()
    active_jd = jd_text.strip()
    if st.session_state.get("use_voice_as_jd") and st.session_state.get("voice_transcript"):
        active_jd = st.session_state["voice_transcript"]

    if not groq_key:
        st.error("❌ Enter your Groq API key in the sidebar.")
        st.stop()
    if not active_jd:
        st.error("❌ Provide a Job Description via voice or sidebar.")
        st.stop()
    if not resumes:
        st.error("❌ No resumes found in `sample_resumes/`.")
        st.stop()

    st.session_state["pipeline_running"] = True
    st.session_state["active_node"] = 0

    progress_bar = st.progress(0, text="Initializing ARIA pipeline...")
    status_text  = st.empty()

    def update_progress(i, total, name):
        progress_bar.progress(int(((i+1)/total)*100)/100, text=f"Analyzing {name} ({i+1}/{total})...")
        status_text.markdown(f"<span style='font-family:Orbitron,monospace;font-size:0.75rem;color:#00D4B4;'>⚡ Processing → {name}</span>", unsafe_allow_html=True)
        st.session_state["active_node"] = min(i+1, 3)

    try:
        status_text.markdown("<span style='font-family:Orbitron,monospace;font-size:0.75rem;color:#00D4B4;'>⚡ Agent 1 — Analyzing JD...</span>", unsafe_allow_html=True)
        progress_bar.progress(0.05, text="JD Analysis in progress...")

        results = run_pipeline(groq_key, active_jd, resumes, update_progress)

        progress_bar.progress(1.0, text="✅ Pipeline complete!")
        status_text.empty()

        st.session_state.update({
            "results": results,
            "active_jd": active_jd,
            "pipeline_running": False,
            "active_node": -1,
            "chat_history": []
        })

        if voice_enabled and results:
            top = results[0]
            voice_text = (
                f"Pipeline complete. {len(results)} candidates screened. "
                f"Top candidate is {top['name']} with a score of {top['final'].get('score',0)} out of 100. "
                f"Match level: {top['final'].get('match_level','')}. {top['final'].get('verdict','')}"
            )
            try:
                st.audio(text_to_speech(voice_text), format="audio/mp3", autoplay=True)
            except Exception:
                pass

        st.success(f"✅ {len(results)} candidates screened. Head to the **Results** page →")

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.session_state["pipeline_running"] = False
        st.error(f"Pipeline error: {e}")
        st.stop()


# ── EMPTY / DONE STATE ────────────────────────────────────────────────────────
if "results" not in st.session_state and not run_btn:
    st.markdown("""
    <div style="text-align:center;padding:50px 20px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:3px;color:#1E3A5F;margin-bottom:20px;">SYSTEM READY</div>
      <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;color:#0F2338;margin-bottom:12px;">Awaiting Input</div>
      <div style="font-size:0.85rem;color:#1E3A5F;line-height:2.2;">
        01 · Add candidate PDFs to <code style="color:#00897B;">sample_resumes/</code><br>
        02 · Speak or paste your Job Description<br>
        03 · Click ACTIVATE PIPELINE<br>
        04 · Chat with ARIA about results
      </div>
    </div>
    """, unsafe_allow_html=True)

elif "results" in st.session_state:
    results = st.session_state["results"]
    st.markdown(f'<div style="background:rgba(0,212,180,0.05);border:1px solid rgba(0,212,180,0.2);border-radius:10px;padding:14px 20px;margin-top:10px;"><span style="font-family:Orbitron,monospace;font-size:0.7rem;color:#00D4B4;letter-spacing:1.5px;">✅ LAST RUN COMPLETE — {len(results)} CANDIDATES · Navigate to Results page →</span></div>', unsafe_allow_html=True)
