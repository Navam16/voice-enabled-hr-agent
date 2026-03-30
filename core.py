"""
╔══════════════════════════════════════════════════════════════╗
║           HR RECRUITING AGENT — CORE UTILITIES               ║
║        Groq (LLM) + Whisper (STT) + gTTS (TTS)              ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import re
import tempfile
import io
from pathlib import Path

import PyPDF2
from groq import Groq
from gtts import gTTS

RESUME_FOLDER = Path("sample_resumes")


# ─────────────────────────────────────────────────────────────────────────────
# PDF & RESUME LOADING
# ─────────────────────────────────────────────────────────────────────────────

def read_pdf(path: Path) -> str:
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception as e:
        return f"[PDF parse error: {e}]"


def load_resumes() -> list[dict]:
    if not RESUME_FOLDER.exists():
        return []
    resumes = []
    for pdf in sorted(RESUME_FOLDER.glob("*.pdf")):
        name = pdf.stem.replace("_", " ").replace("-", " ").title()
        resumes.append({
            "name": name,
            "filename": pdf.name,
            "text": read_pdf(pdf)
        })
    return resumes


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def safe_json(raw: str) -> dict:
    clean = re.sub(r"^```(?:json)?", "", raw.strip()).strip()
    clean = re.sub(r"```$", "", clean).strip()
    try:
        return json.loads(clean)
    except Exception:
        return {}


def score_cls(s: int) -> str:
    return "s-high" if s >= 70 else ("s-mid" if s >= 45 else "s-low")


def tags_html(items: list, cls: str = "") -> str:
    if not items:
        return '<span style="color:#94A3B8;font-size:0.8rem;">—</span>'
    return " ".join(f'<span class="tag {cls}">{i}</span>' for i in items[:8])


# ─────────────────────────────────────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────────────────────────────────────

def llm(api_key: str, prompt: str, max_tokens: int = 700) -> str:
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def llm_chat(api_key: str, messages: list[dict], max_tokens: int = 800) -> str:
    """Multi-turn chat with conversation history."""
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# STT & TTS
# ─────────────────────────────────────────────────────────────────────────────

def transcribe_audio(api_key: str, audio_bytes: bytes, filename: str = "audio.wav") -> str:
    client = Groq(api_key=api_key)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=(filename, f, "audio/wav"),
                language="en"
            )
        return result.text.strip()
    finally:
        os.unlink(tmp_path)


def text_to_speech(text: str) -> bytes:
    tts = gTTS(text=text[:500], lang="en", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────────────────────────────────────
# 4-AGENT PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def agent1_jd(api_key: str, jd: str) -> dict:
    prompt = f"""You are an expert HR analyst. Extract requirements from this job description.
Return ONLY valid JSON — no markdown, no extra text.

JD:
{jd[:2500]}

JSON schema:
{{
  "role_title": "...",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "min_experience_years": <number or null>,
  "must_have": ["requirement 1", "requirement 2"]
}}"""
    return safe_json(llm(api_key, prompt, 500)) or {"role_title": "Role", "required_skills": [], "must_have": []}


def agent2_resume(api_key: str, text: str, name: str) -> dict:
    prompt = f"""You are a resume parser. Extract candidate information.
Return ONLY valid JSON — no markdown, no extra text.

RESUME ({name}):
{text[:3000]}

JSON schema:
{{
  "candidate_name": "...",
  "total_experience_years": <number or null>,
  "current_role": "...",
  "skills": ["skill1", "skill2"],
  "education": ["degree1"],
  "certifications": []
}}"""
    result = safe_json(llm(api_key, prompt, 500))
    if not result.get("candidate_name"):
        result["candidate_name"] = name
    return result


def agent3_redflag(api_key: str, text: str, profile: dict) -> dict:
    prompt = f"""You are a critical HR risk analyst. Find red flags in this resume.
Return ONLY valid JSON — no markdown, no extra text.

PROFILE:
{json.dumps(profile, indent=2)[:1000]}

JSON schema:
{{
  "job_hopping": true/false,
  "employment_gaps": true/false,
  "red_flags": ["flag1", "flag2"],
  "positive_signals": ["signal1", "signal2"]
}}"""
    return safe_json(llm(api_key, prompt, 400)) or {"red_flags": [], "positive_signals": []}


def agent4_recruiter(api_key: str, jd: str, jd_req: dict, profile: dict, flags: dict) -> dict:
    prompt = f"""You are a senior recruiter making a final hiring decision.
Return ONLY valid JSON — no markdown, no extra text.

JD REQUIREMENTS:
{json.dumps(jd_req, indent=2)[:800]}

CANDIDATE:
{json.dumps(profile, indent=2)[:800]}

RED FLAGS:
{json.dumps(flags, indent=2)[:400]}

JSON schema:
{{
  "score": <integer 0-100>,
  "match_level": "<Strong Match|Good Match|Partial Match|Weak Match>",
  "key_strengths": ["strength1", "strength2", "strength3"],
  "critical_gaps": ["gap1", "gap2"],
  "verdict": "<2-3 sentence hiring recommendation>",
  "interview_questions": ["q1", "q2", "q3"]
}}"""
    return safe_json(llm(api_key, prompt, 700)) or {"score": 0, "match_level": "Weak Match", "verdict": "Could not evaluate."}


def run_pipeline(api_key: str, jd: str, resumes: list[dict], progress_cb=None) -> list[dict]:
    jd_req = agent1_jd(api_key, jd)
    results = []
    total = len(resumes)

    for i, r in enumerate(resumes):
        name = r["name"]
        if progress_cb:
            progress_cb(i, total, name)

        profile = agent2_resume(api_key, r["text"], name)
        flags   = agent3_redflag(api_key, r["text"], profile)
        final   = agent4_recruiter(api_key, jd, jd_req, profile, flags)

        results.append({
            "name":     profile.get("candidate_name", name),
            "filename": r["filename"],
            "profile":  profile,
            "flags":    flags,
            "final":    final,
            "jd_req":   jd_req,
        })

    results.sort(key=lambda x: x["final"].get("score", 0), reverse=True)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATIONAL AGENT
# ─────────────────────────────────────────────────────────────────────────────

def build_system_prompt(results: list[dict], jd: str) -> str:
    """Build a rich system prompt with all pipeline results for the chat agent."""
    candidates_summary = []
    for i, r in enumerate(results, 1):
        f = r["final"]
        p = r["profile"]
        candidates_summary.append(f"""
Candidate #{i}: {r['name']}
  Score: {f.get('score', 0)}/100
  Match Level: {f.get('match_level', '—')}
  Current Role: {p.get('current_role', '—')}
  Experience: {p.get('total_experience_years', '—')} years
  Skills: {', '.join(p.get('skills', []))}
  Key Strengths: {', '.join(f.get('key_strengths', []))}
  Critical Gaps: {', '.join(f.get('critical_gaps', []))}
  Red Flags: {', '.join(r['flags'].get('red_flags', []))}
  Positive Signals: {', '.join(r['flags'].get('positive_signals', []))}
  Verdict: {f.get('verdict', '—')}
  Interview Questions: {'; '.join(f.get('interview_questions', []))}
""")

    return f"""You are ARIA — an advanced AI HR Recruiting Assistant with a confident, professional, and slightly futuristic personality.

You have just completed screening {len(results)} candidates for the following role:

JOB DESCRIPTION SUMMARY:
{jd[:1000]}

SCREENING RESULTS:
{''.join(candidates_summary)}

Your job is to answer recruiter questions conversationally and helpfully. You can:
- Compare candidates
- Explain scores and verdicts
- Suggest interview questions
- Identify the best fit for specific requirements
- Flag concerns or highlight positives
- Recommend next steps

Keep responses concise (2-4 sentences ideally), clear, and actionable.
Speak naturally as if you are a brilliant HR colleague, not a robot.
When asked to speak a summary aloud, keep it under 100 words.
"""


def chat_with_agent(api_key: str, user_message: str, chat_history: list[dict], results: list[dict], jd: str) -> str:
    """Send a message to the conversational agent with full context."""
    system_prompt = build_system_prompt(results, jd)

    messages = [{"role": "system", "content": system_prompt}]
    messages += chat_history
    messages.append({"role": "user", "content": user_message})

    return llm_chat(api_key, messages, max_tokens=600)
