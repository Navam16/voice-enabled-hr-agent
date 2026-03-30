"""
╔══════════════════════════════════════════════════════════════╗
║        HR RECRUITING AGENT — RESULTS + CHAT PAGE            ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.core import text_to_speech, chat_with_agent, score_cls, tags_html

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
    page_title="Results · ARIA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Shared CSS (minimal, key styles) ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;600;700;800;900&family=JetBrains+Mono:wght@300;400;500&display=swap');

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
.stButton > button {
    background:linear-gradient(135deg,var(--teal2),var(--teal)) !important;
    color:var(--bg) !important; border:none !important; border-radius:8px !important;
    font-family:'Orbitron',monospace !important; font-weight:700 !important;
    font-size:0.7rem !important; letter-spacing:1px !important;
    padding:10px 18px !important; transition:all 0.3s ease !important;
}
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 25px rgba(0,212,180,0.35) !important; }
.tag { display:inline-block; background:var(--bg3); color:var(--muted2); font-size:0.7rem; padding:3px 10px; border-radius:20px; margin:2px 3px 2px 0; border:1px solid var(--border); font-family:'JetBrains Mono',monospace; }
.tag-r { background:rgba(239,68,68,0.1); color:#FCA5A5; border-color:rgba(239,68,68,0.3); }
.tag-g { background:rgba(16,185,129,0.1); color:#6EE7B7; border-color:rgba(16,185,129,0.3); }
.lbl { font-size:0.6rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--muted); margin:12px 0 5px 0; font-family:'Orbitron',monospace; }
.verdict { font-size:0.87rem; color:var(--muted2); line-height:1.7; }
.s-high { color:var(--green); }
.s-mid  { color:var(--amber); }
.s-low  { color:var(--red); }
hr { border-color:var(--border) !important; }
.stTextInput input {
    background:var(--bg3) !important; border:1px solid var(--border2) !important;
    color:var(--text) !important; border-radius:8px !important;
    font-family:'Space Grotesk',sans-serif !important;
}
.stTabs [data-baseweb="tab-list"] { background:var(--bg2) !important; border-bottom:1px solid var(--border) !important; gap:4px; }
.stTabs [data-baseweb="tab"] { font-family:'Orbitron',monospace !important; font-size:0.65rem !important; letter-spacing:1.5px !important; color:var(--muted) !important; background:transparent !important; }
.stTabs [aria-selected="true"] { color:var(--teal) !important; border-bottom:2px solid var(--teal) !important; }
.streamlit-expanderHeader { background:var(--bg3) !important; border:1px solid var(--border) !important; border-radius:8px !important; color:var(--muted2) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
  <div>
    <div style="font-family:'Orbitron',monospace;font-size:1.8rem;font-weight:900;
    letter-spacing:-0.5px;color:#E2E8F0;">
      SCREENING <span style="color:#00D4B4;">RESULTS</span>
    </div>
    <div style="font-size:0.7rem;color:#475569;letter-spacing:2px;text-transform:uppercase;
    margin-top:4px;font-family:'Orbitron',monospace;">
      Ranked Candidates · AI Analysis · Voice Chat
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# GUARD — no results yet
# ─────────────────────────────────────────────────────────────────────────────
if "results" not in st.session_state or not st.session_state["results"]:
    st.markdown("""
    <div style="text-align:center;padding:80px 20px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:3px;
      color:#1E3A5F;margin-bottom:16px;">NO DATA</div>
      <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#0F2338;margin-bottom:10px;">
        Pipeline Not Yet Run
      </div>
      <div style="font-size:0.85rem;color:#1E3A5F;">
        Go to the Voice Hub page, provide a JD, and activate the pipeline first.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
results  = st.session_state["results"]
active_jd = st.session_state.get("active_jd", "")
groq_key  = get_groq_key()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_results, tab_chat, tab_scorecard = st.tabs([
    "🏆  RANKED CANDIDATES",
    "💬  CHAT WITH ARIA",
    "📊  SCORECARD"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RANKED CANDIDATES
# ══════════════════════════════════════════════════════════════════════════════
with tab_results:
    voice_col, _ = st.columns([2, 5])
    with voice_col:
        voice_on = st.toggle("🔊 Voice Playback", value=True, key="voice_results")

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    for rank, r in enumerate(results, 1):
        f         = r["final"]
        score     = f.get("score", 0)
        sc        = score_cls(score)
        match     = f.get("match_level", "—")
        strengths = f.get("key_strengths", [])
        gaps      = f.get("critical_gaps", [])
        questions = f.get("interview_questions", [])
        verdict   = f.get("verdict", "")
        flags     = r["flags"]
        profile   = r["profile"]

        # Determine card accent color
        accent = "#10B981" if score >= 70 else ("#F59E0B" if score >= 45 else "#EF4444")

        st.markdown(f"""
        <div style="background:#080F1C;border:1px solid #0F2338;border-left:3px solid {accent};
        border-radius:14px;padding:22px 26px;margin-bottom:16px;">

          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
            <div>
              <div style="font-family:'Orbitron',monospace;font-size:0.6rem;font-weight:700;
              letter-spacing:2px;color:{accent};border:1px solid {accent}33;
              padding:2px 10px;border-radius:20px;display:inline-block;margin-bottom:8px;">
              #{rank} · {match.upper()}
              </div>
              <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;
              color:#E2E8F0;letter-spacing:0.5px;">{r['name']}</div>
              <div style="font-size:0.78rem;color:#475569;margin-top:3px;">
              {profile.get('current_role','—')} · {profile.get('total_experience_years','—')} yrs exp
              </div>
            </div>
            <div style="text-align:center;">
              <div style="font-family:'Orbitron',monospace;font-size:2.8rem;
              font-weight:900;line-height:1;color:{accent};">{score}</div>
              <div style="font-family:'Orbitron',monospace;font-size:0.55rem;
              letter-spacing:2px;color:#1E3A5F;">/100</div>
            </div>
          </div>

          <div class="lbl">Key Strengths</div>
          <div>{tags_html(strengths, 'tag-g')}</div>

          <div class="lbl">Critical Gaps</div>
          <div>{tags_html(gaps, 'tag-r')}</div>

          <div class="lbl">Red Flags</div>
          <div>{tags_html(flags.get('red_flags', []), 'tag-r')}</div>

          <div class="lbl">Positive Signals</div>
          <div>{tags_html(flags.get('positive_signals', []))}</div>

          <div class="lbl">Recruiter Verdict</div>
          <div class="verdict">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1.2, 1.2, 4])
        with c1:
            if voice_on and st.button(f"🔊 Hear #{rank}", key=f"speak_{rank}"):
                speak_text = (
                    f"Candidate {r['name']}. "
                    f"Score {score} out of 100. {match}. "
                    f"{verdict}"
                )
                try:
                    ab = text_to_speech(speak_text)
                    st.audio(ab, format="audio/mp3", autoplay=True)
                except Exception:
                    st.warning("TTS unavailable")
        with c2:
            with st.expander(f"💬 Interview Qs"):
                for q in questions:
                    st.markdown(f"<div style='font-size:0.85rem;color:#94A3B8;padding:4px 0;border-bottom:1px solid #0F2338;'>{q}</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONVERSATIONAL CHAT WITH ARIA
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:

    # ── Chat header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:rgba(0,212,180,0.05);border:1px solid rgba(0,212,180,0.15);
    border-radius:12px;padding:16px 20px;margin-bottom:20px;">
      <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;
      color:#00D4B4;margin-bottom:6px;">ARIA · CONVERSATIONAL MODE</div>
      <div style="font-size:0.83rem;color:#64748B;line-height:1.6;">
        Ask ARIA anything about the screening results. Compare candidates, get interview
        questions, understand scores, or explore specific requirements. Voice input supported.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Suggested prompts ────────────────────────────────────────────────────
    suggestions = [
        "Who is the best candidate?",
        "Compare top 2 candidates",
        "Who has Python experience?",
        "What are the red flags?",
        "Interview questions for #1",
    ]

    st.markdown("<div style='font-family:Orbitron,monospace;font-size:0.6rem;letter-spacing:2px;color:#1E3A5F;margin-bottom:8px;'>QUICK PROMPTS</div>", unsafe_allow_html=True)
    sug_cols = st.columns(len(suggestions))
    clicked_suggestion = None
    for idx, (col, sug) in enumerate(zip(sug_cols, suggestions)):
        with col:
            if st.button(sug, key=f"sug_{idx}"):
                clicked_suggestion = sug

    st.divider()

    # ── Chat history display ──────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not st.session_state["chat_history"]:
            st.markdown("""
            <div style="text-align:center;padding:30px;color:#1E3A5F;
            font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;">
            ARIA IS READY — ASK YOUR FIRST QUESTION
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state["chat_history"]:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-end;margin:6px 0;">
                      <div>
                        <div style="font-family:'Orbitron',monospace;font-size:0.5rem;
                        letter-spacing:2px;color:#475569;text-align:right;margin-bottom:3px;">YOU</div>
                        <div style="background:linear-gradient(135deg,#00897B,#00D4B4);
                        color:#050B14;border-radius:14px 14px 4px 14px;
                        padding:12px 16px;font-size:0.88rem;font-weight:500;
                        max-width:480px;">{msg['content']}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-start;margin:6px 0;">
                      <div>
                        <div style="font-family:'Orbitron',monospace;font-size:0.5rem;
                        letter-spacing:2px;color:#00D4B4;margin-bottom:3px;">ARIA</div>
                        <div style="background:#0C1628;border:1px solid #1A3A5C;
                        color:#E2E8F0;border-radius:14px 14px 14px 4px;
                        padding:12px 16px;font-size:0.88rem;line-height:1.65;
                        max-width:540px;">{msg['content']}</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)

    # ── Voice input for chat ──────────────────────────────────────────────────
    chat_voice_col, chat_text_col = st.columns([1, 3])

    with chat_voice_col:
        st.markdown("<div style='font-family:Orbitron,monospace;font-size:0.6rem;letter-spacing:2px;color:#1E3A5F;margin-bottom:6px;'>VOICE INPUT</div>", unsafe_allow_html=True)
        chat_audio = st.audio_input("Ask ARIA by voice", key="chat_audio_input")
        voice_chat_text = ""
        if chat_audio is not None:
            if not groq_key:
                st.error("Add Groq key in sidebar.")
            else:
                with st.spinner("Transcribing..."):
                    try:
                        from utils.core import transcribe_audio
                        voice_chat_text = transcribe_audio(groq_key, chat_audio.read(), "chat.wav")
                        st.success(f"✅ '{voice_chat_text[:50]}...' " if len(voice_chat_text) > 50 else f"✅ '{voice_chat_text}'")
                    except Exception as e:
                        st.error(f"STT error: {e}")

    with chat_text_col:
        st.markdown("<div style='font-family:Orbitron,monospace;font-size:0.6rem;letter-spacing:2px;color:#1E3A5F;margin-bottom:6px;'>TEXT INPUT</div>", unsafe_allow_html=True)
        user_input = st.text_input(
            "Ask ARIA",
            label_visibility="collapsed",
            placeholder="e.g. Who is the strongest candidate for a Python role?",
            key="chat_text_input"
        )

        chat_voice_reply = st.toggle("🔊 Speak ARIA's reply", value=True, key="chat_voice_toggle")

        send_btn = st.button("⚡ SEND", key="send_chat")

    # ── Determine final message to send ──────────────────────────────────────
    final_message = ""
    if send_btn and user_input.strip():
        final_message = user_input.strip()
    elif voice_chat_text:
        final_message = voice_chat_text
    elif clicked_suggestion:
        final_message = clicked_suggestion

    # ── Process message ───────────────────────────────────────────────────────
    if final_message:
        if not groq_key:
            st.error("❌ Add your Groq API key via the sidebar.")
        else:
            # Add user message to history
            st.session_state["chat_history"].append({
                "role": "user",
                "content": final_message
            })

            with st.spinner("ARIA is thinking..."):
                try:
                    response = chat_with_agent(
                        api_key=groq_key,
                        user_message=final_message,
                        chat_history=st.session_state["chat_history"][:-1],  # exclude last user msg (already sent)
                        results=results,
                        jd=active_jd
                    )
                except Exception as e:
                    response = f"I encountered an error: {e}"

            # Add agent response to history
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": response
            })

            # Voice reply
            if chat_voice_reply:
                try:
                    ab = text_to_speech(response)
                    st.audio(ab, format="audio/mp3", autoplay=True)
                except Exception:
                    pass

            st.rerun()

    # ── Clear chat ────────────────────────────────────────────────────────────
    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state["chat_history"] = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SCORECARD
# ══════════════════════════════════════════════════════════════════════════════
with tab_scorecard:
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;
    color:#00D4B4;margin-bottom:16px;">FULL SCORECARD SUMMARY</div>
    """, unsafe_allow_html=True)

    st.dataframe(
        {
            "Rank":        list(range(1, len(results) + 1)),
            "Candidate":   [r["name"] for r in results],
            "Score":       [r["final"].get("score", 0) for r in results],
            "Match":       [r["final"].get("match_level", "—") for r in results],
            "Experience":  [f"{r['profile'].get('total_experience_years', '—')} yrs" for r in results],
            "Role":        [r["profile"].get("current_role", "—") for r in results],
            "Red Flags":   [len(r["flags"].get("red_flags", [])) for r in results],
            "File":        [r["filename"] for r in results],
        },
        use_container_width=True,
        hide_index=True,
    )

    # ── Top candidate highlight ───────────────────────────────────────────────
    if results:
        top = results[0]
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.2);
        border-radius:12px;padding:20px;margin-top:20px;">
          <div style="font-family:'Orbitron',monospace;font-size:0.6rem;letter-spacing:2px;
          color:#10B981;margin-bottom:8px;">⭐ RECOMMENDED HIRE</div>
          <div style="font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:800;
          color:#E2E8F0;">{top['name']}</div>
          <div style="font-size:0.85rem;color:#64748B;margin-top:4px;">
          Score: {top['final'].get('score',0)}/100 · {top['final'].get('match_level','—')}
          </div>
          <div style="font-size:0.85rem;color:#94A3B8;margin-top:10px;line-height:1.6;">
          {top['final'].get('verdict','—')}
          </div>
        </div>
        """, unsafe_allow_html=True)
