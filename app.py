import json
import os
import re
from pathlib import Path

import streamlit as st
from groq import Groq

BASE_DIR = Path(__file__).parent
PROTOCOL_FILE = BASE_DIR / "emergency_protocols.json"
SERVICES_FILE = BASE_DIR / "emergency_services.json"

st.set_page_config(
    page_title="Healthify",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Theme and visual styling
# -----------------------------
st.markdown(
    """
    <style>
    :root {
        --offwhite: #FAFAFA;
        --charcoal: #1E293B;
        --burgundy: #881337;
        --warmgray: #F4F4F5;
    }

    .stApp {
        background: #FAFAFA;
        color: #1E293B;
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label, .stMarkdown {
        color: #1E293B;
    }

    .brand {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }

    .brand h1 {
        margin: 0;
        letter-spacing: 0.08em;
        font-size: 2.2rem;
        color: #1E293B;
    }

    .tagline {
        margin-top: 0.4rem;
        color: #475569;
        font-size: 1rem;
    }

    .card {
        background: #F4F4F5;
        border-radius: 14px;
        padding: 1.15rem;
        margin: 0.8rem 0;
        border: 1px solid #E4E4E7;
    }

    .emergency-card {
        background: #FFF7F8;
        border-left: 5px solid #881337;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin: 0.8rem 0;
    }

    .warning {
        background: #FFF1F2;
        border: 1px solid #FDA4AF;
        border-left: 5px solid #881337;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin: 0.8rem 0;
        color: #4C0519;
    }

    .question {
        font-weight: 700;
        color: #881337;
        margin-top: 1rem;
    }

    .small-note {
        color: #64748B;
        font-size: 0.86rem;
    }

    .disclaimer {
        color: #64748B;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 2rem;
        line-height: 1.5;
    }

    .step {
        font-size: 1.05rem;
        margin: 0.55rem 0;
        line-height: 1.45;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 3rem;
        font-weight: 650;
    }

    div.stButton > button[kind="primary"] {
        background: #881337;
        border-color: #881337;
        color: white;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }

    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 0.8rem 2rem 0.8rem;
        }
        .brand h1 {
            font-size: 1.8rem;
        }
        .step {
            font-size: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Load local knowledge
# -----------------------------
@st.cache_data
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


try:
    PROTOCOLS = load_json(PROTOCOL_FILE)
    SERVICES = load_json(SERVICES_FILE)
except Exception:
    st.error("Healthify could not load its local safety knowledge base.")
    st.stop()


# -----------------------------
# Session state
# -----------------------------
DEFAULT_STATE = {
    "mode": "home",
    "emergency_active": False,
    "emergency_type": None,
    "severity": None,
    "current_protocol": None,
    "current_step": 0,
    "user_answers": [],
    "patient_responsive": None,
    "breathing_status": None,
    "bleeding_status": None,
    "allergy_information": None,
    "medication_information": None,
    "emergency_services_called": False,
    "conversation_history": [],
    "last_question": None,
    "country": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------
# Groq configuration
# -----------------------------
def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")


def get_client():
    key = get_api_key()
    if not key:
        return None
    return Groq(api_key=key)


CHAT_MODEL = "openai/gpt-oss-120b"
TRANSCRIBE_MODEL = "whisper-large-v3-turbo"


# -----------------------------
# Deterministic safety helpers
# -----------------------------
def normalize(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def keyword_protocol(text):
    """Conservative fallback if the LLM is unavailable."""
    t = normalize(text)

    critical_patterns = [
        ("cpr", ["not breathing", "no breathing", "only gasping", "cardiac arrest"]),
        ("choking", ["choking", "can't breathe because", "cannot breathe because", "food stuck"]),
        ("severe_bleeding", ["bleeding heavily", "heavy bleeding", "blood is spurting", "blood pouring"]),
        ("stroke", ["face drooping", "arm weakness", "speech difficulty", "slurred speech", "stroke"]),
        ("anaphylaxis", ["swollen tongue", "swollen throat", "trouble breathing and hives", "anaphylaxis"]),
        ("electric_shock", ["electric shock", "electrocuted", "electrical shock"]),
        ("poisoning", ["poisoning", "swallowed poison", "overdose", "took too many pills"]),
    ]
    for name, patterns in critical_patterns:
        if any(p in t for p in patterns):
            return name

    ordered = sorted(
        PROTOCOLS.items(),
        key=lambda item: len(item[1].get("keywords", [])),
        reverse=True,
    )
    for name, data in ordered:
        if any(k in t for k in data.get("keywords", [])):
            return name
    return None


def extract_simple_flags(text):
    """Very small deterministic layer for critical facts."""
    t = normalize(text)
    facts = {}

    if any(x in t for x in ["not responding", "unresponsive", "won't wake", "cannot wake"]):
        facts["responsive"] = False
    elif any(x in t for x in ["awake", "responding", "responsive", "conscious"]):
        facts["responsive"] = True

    if any(x in t for x in ["not breathing", "no breathing", "only gasping", "can't breathe", "cannot breathe"]):
        facts["breathing"] = False
    elif any(x in t for x in ["breathing normally", "breathing fine"]):
        facts["breathing"] = True

    if any(x in t for x in ["heavy bleeding", "spurting", "blood pouring", "won't stop bleeding"]):
        facts["bleeding"] = "severe"

    if any(x in t for x in ["trouble breathing", "difficulty breathing", "shortness of breath"]):
        facts["breathing_difficulty"] = True

    if any(x in t for x in ["pregnant", "pregnancy"]):
        facts["pregnant"] = True

    if any(x in t for x in ["infant", "baby", "newborn"]):
        facts["age_group"] = "infant"
    elif any(x in t for x in ["child", "kid", "young child"]):
        facts["age_group"] = "child"
    elif any(x in t for x in ["adult", "grown man", "grown woman"]):
        facts["age_group"] = "adult"

    if any(x in t for x in ["yes, emergency services called", "called 1122", "called 911", "called emergency"]):
        facts["emergency_services_called"] = True

    return facts


def update_state_from_facts(facts):
    if "responsive" in facts:
        st.session_state.patient_responsive = facts["responsive"]
    if "breathing" in facts:
        st.session_state.breathing_status = facts["breathing"]
    if "bleeding" in facts:
        st.session_state.bleeding_status = facts["bleeding"]
    if "emergency_services_called" in facts:
        st.session_state.emergency_services_called = facts["emergency_services_called"]


# -----------------------------
# AI interpretation
# -----------------------------
def analyze_emergency(user_text):
    client = get_client()
    fallback = keyword_protocol(user_text)

    if client is None:
        return {
            "protocol": fallback,
            "facts": extract_simple_flags(user_text),
            "critical": bool(fallback in {
                "cpr", "choking", "severe_bleeding", "stroke",
                "anaphylaxis", "electric_shock", "poisoning",
                "unresponsive"
            }),
        }

    allowed = list(PROTOCOLS.keys())
    current = st.session_state.current_protocol or "none"
    prompt = f"""
You are the triage/classification component of Healthify.

You do NOT provide medical procedures. You only interpret the user's words
and select one protocol from this exact allow-list:
{json.dumps(allowed)}

Current protocol: {current}

Return JSON only:
{{
  "protocol": "<one allowed protocol name or null>",
  "facts": {{
    "responsive": true/false/null,
    "breathing": true/false/null,
    "bleeding": "severe"/"not_severe"/null,
    "breathing_difficulty": true/false/null,
    "age_group": "infant"/"child"/"adult"/"unknown",
    "pregnant": true/false/null,
    "emergency_services_called": true/false/null
  }},
  "critical": true/false
}}

Rules:
- Prefer the current protocol when the user is answering its question.
- Choose a protocol only when the text supports it.
- If the user describes a life-threatening situation, set critical=true.
- Never invent facts.
- Do not include treatment advice.
- No markdown.

User message:
{user_text}
"""
    try:
        result = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=350,
        )
        raw = result.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw).strip()
        data = json.loads(raw)

        if data.get("protocol") not in PROTOCOLS:
            data["protocol"] = fallback

        simple = extract_simple_flags(user_text)
        ai_facts = data.get("facts") if isinstance(data.get("facts"), dict) else {}
        facts = {k: v for k, v in ai_facts.items() if v is not None}
        facts.update(simple)
        data["facts"] = facts

        return data
    except Exception:
        return {
            "protocol": fallback,
            "facts": extract_simple_flags(user_text),
            "critical": bool(fallback in {
                "cpr", "choking", "severe_bleeding", "stroke",
                "anaphylaxis", "electric_shock", "poisoning",
                "unresponsive"
            }),
        }


# -----------------------------
# Protocol transitions
# -----------------------------
def transition_protocol(user_text, current):
    t = normalize(user_text)
    facts = extract_simple_flags(user_text)

    if current == "unresponsive":
        if facts.get("responsive") is False and facts.get("breathing") is False:
            return "cpr"
        if "not breathing" in t or "only gasping" in t:
            return "cpr"

    if current == "bee_sting":
        if any(x in t for x in [
            "trouble breathing", "difficulty breathing", "swollen tongue",
            "swollen throat", "swollen face", "swollen lips", "hives"
        ]):
            return "anaphylaxis"

    if current == "choking":
        # Keep choking state; age determines which instruction block is shown.
        return "choking"

    if current == "seizure":
        if "not breathing" in t or "only gasping" in t:
            return "cpr"

    return current


def protocol_actions(protocol_name):
    p = PROTOCOLS[protocol_name]
    actions = list(p["immediate_actions"])

    if protocol_name == "choking":
        # Avoid presenting infant technique as if it applies to everyone.
        age = st.session_state.get("user_answers", [])
        recent = normalize(" ".join(age[-3:]))
        if any(x in recent for x in ["infant", "baby", "newborn"]):
            actions = [
                "Call your local emergency service or send someone to call.",
                "For a choking infant who cannot cough, cry, or breathe: give 5 back blows.",
                "Turn the infant face-up and give 5 chest thrusts.",
                "Repeat 5 back blows and 5 chest thrusts until the object comes out or the infant becomes unresponsive."
            ]
        else:
            actions = [
                "If the person can cough forcefully, encourage coughing and watch closely.",
                "If they cannot cough, speak, cry, or breathe, call your local emergency service.",
                "For an adult or child with severe choking: give 5 back blows, then 5 abdominal thrusts.",
                "Repeat until the object is expelled or the person becomes unresponsive."
            ]
    return actions[:5]


def choose_next_question(protocol_name):
    p = PROTOCOLS[protocol_name]
    answers = st.session_state.user_answers
    joined = normalize(" ".join(answers[-5:]))

    if protocol_name == "cpr":
        if not st.session_state.emergency_services_called and not any(
            x in joined for x in ["called", "1122", "911", "emergency services"]
        ):
            return "Have emergency services been called?"
        if st.session_state.breathing_status is None:
            return "Is the person breathing normally?"
        return "Is an AED available nearby?"

    if protocol_name == "unresponsive":
        if st.session_state.patient_responsive is None:
            return "Are they responding to you?"
        if st.session_state.breathing_status is None:
            return "Are they breathing normally?"
        return None

    if protocol_name == "bee_sting":
        if not any(x in joined for x in ["breathing", "swelling", "swollen"]):
            return "Are you having trouble breathing or swelling of the face, lips, tongue, or throat?"
        return "Do you have a prescribed epinephrine auto-injector?"

    if protocol_name == "anaphylaxis":
        if st.session_state.breathing_status is None:
            return "Are they having trouble breathing or becoming less responsive?"
        return "Is a prescribed epinephrine auto-injector available?"

    if protocol_name == "choking":
        if not any(x in joined for x in ["adult", "child", "infant", "baby"]):
            return "Is the person an adult/child or an infant?"
        if not any(x in joined for x in ["cough", "speak", "breathe", "cry"]):
            return "Can they cough, speak, cry, or breathe?"
        return "Are they becoming unresponsive?"

    if protocol_name == "severe_bleeding":
        return "Is the bleeding still heavy or spurting?"

    if protocol_name == "burns":
        if not any(x in joined for x in ["chemical", "electric", "electricity", "heat", "fire", "hot"]):
            return "Was the burn caused by heat, a chemical, or electricity?"
        return "Is the burn on the face/airway or larger than the person's palm?"

    if protocol_name == "seizure":
        return "Has the seizure lasted 5 minutes or longer, or are seizures repeating without recovery?"

    if protocol_name == "stroke":
        return "When did the symptoms start, or when were they last known to be well?"

    if protocol_name == "chest_pain":
        return "Is the chest pain severe or associated with breathing difficulty, fainting, sweating, or pain spreading to the arm or jaw?"

    if protocol_name == "breathing_difficulty":
        return "Can they speak in full sentences?"

    if protocol_name == "fainting":
        return "Are they awake and responding normally now?"

    if protocol_name == "fracture_injury":
        return "Is there severe bleeding, deformity, numbness, or a blue/pale limb?"

    if protocol_name == "poisoning":
        return "What substance was involved, and roughly how much?"

    if protocol_name == "heat_illness":
        return "Are they confused, fainting, having a seizure, or difficult to wake?"

    if protocol_name == "electric_shock":
        return "Has the power source definitely been switched off?"

    if protocol_name == "nosebleed":
        return "Has the bleeding continued despite 15 minutes of firm pressure?"

    if protocol_name == "minor_cut":
        return "Is the bleeding heavy or still not stopping with direct pressure?"

    if protocol_name == "eye_injury":
        return "Was a chemical or sharp object involved?"

    if protocol_name == "sprain":
        return "Is the limb deformed, numb, blue/pale, or impossible to use?"

    return p["questions"][0] if p.get("questions") else None


# -----------------------------
# Voice transcription
# -----------------------------
def transcribe_audio(audio_file):
    client = get_client()
    if client is None:
        return None, "Voice transcription needs GROQ_API_KEY. Text input is still available."

    try:
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.getvalue()),
            model=TRANSCRIBE_MODEL,
        )
        text = getattr(transcription, "text", "").strip()
        if text:
            return text, None
        return None, "No speech was detected. Please try again or use text."
    except Exception:
        return None, "Voice input could not be transcribed. Please use text input."


# -----------------------------
# Rendering
# -----------------------------
def render_brand():
    st.markdown(
        """
        <div class="brand">
            <h1>HEALTHIFY</h1>
            <div class="tagline">Clear guidance when every second matters.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer():
    st.markdown(
        '<div class="disclaimer">Healthify provides general first-response information and does not replace emergency medical professionals, doctors, or local emergency services. In a life-threatening situation, contact emergency services immediately.</div>',
        unsafe_allow_html=True,
    )


def render_emergency_response(protocol_name):
    p = PROTOCOLS[protocol_name]
    st.markdown(f'<div class="emergency-card"><strong>{p["name"]}</strong></div>', unsafe_allow_html=True)

    for idx, action in enumerate(protocol_actions(protocol_name), start=1):
        st.markdown(f'<div class="step"><strong>{idx}.</strong> {action}</div>', unsafe_allow_html=True)

    # Escalation is always visible for critical protocols, but concise.
    if p["severity"] == "critical":
        st.markdown(
            '<div class="warning"><strong>Emergency:</strong> Contact your local emergency service now if this is happening or worsening.</div>',
            unsafe_allow_html=True,
        )

    q = choose_next_question(protocol_name)
    st.session_state.last_question = q
    if q:
        st.markdown(f'<div class="question">{q}</div>', unsafe_allow_html=True)


def render_voice_and_text(key_prefix):
    voice_text = None
    if hasattr(st, "audio_input"):
        audio = st.audio_input("Speak", key=f"{key_prefix}_voice")
        if audio is not None:
            voice_text, err = transcribe_audio(audio)
            if err:
                st.caption(err)

    typed = st.text_area(
        "Type",
        key=f"{key_prefix}_text",
        placeholder="Describe what is happening...",
        height=90,
        label_visibility="collapsed",
    )

    submitted = st.button(
        "Send",
        key=f"{key_prefix}_send",
        type="primary",
        use_container_width=True,
    )

    if not submitted:
        return None

    text = (voice_text or typed or "").strip()
    if not text:
        st.warning("Please speak or type what is happening.")
        return None

    return text


def start_emergency():
    st.session_state.mode = "emergency"
    st.session_state.emergency_active = True
    st.session_state.emergency_type = None
    st.session_state.severity = None
    st.session_state.current_protocol = None
    st.session_state.current_step = 0
    st.session_state.user_answers = []
    st.session_state.patient_responsive = None
    st.session_state.breathing_status = None
    st.session_state.bleeding_status = None
    st.session_state.allergy_information = None
    st.session_state.medication_information = None
    st.session_state.emergency_services_called = False
    st.session_state.conversation_history = []
    st.session_state.last_question = None


def reset_session():
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value


def handle_emergency_message(text):
    st.session_state.user_answers.append(text)
    st.session_state.conversation_history.append({"role": "user", "content": text})

    analysis = analyze_emergency(text)
    facts = analysis.get("facts", {})
    update_state_from_facts(facts)

    current = st.session_state.current_protocol
    chosen = analysis.get("protocol")

    if current is None:
        current = chosen or "unresponsive"
    elif chosen and current in {"unresponsive", "bee_sting"}:
        current = transition_protocol(text, current)
    else:
        current = transition_protocol(text, current)

    st.session_state.current_protocol = current
    st.session_state.emergency_type = PROTOCOLS[current]["name"]
    st.session_state.severity = PROTOCOLS[current]["severity"]

    if facts.get("emergency_services_called") is True:
        st.session_state.emergency_services_called = True

    st.session_state.conversation_history.append(
        {"role": "assistant", "content": f"[protocol:{current}]"}
    )


def general_health_answer(user_text):
    client = get_client()
    if client is None:
        return (
            "GROQ_API_KEY is not configured. Add it to Streamlit Secrets to use "
            "General Health Information. If this may be an emergency, use Emergency Assistance."
        )

    prompt = """
You are Healthify's general health information assistant.
Do not diagnose with certainty, prescribe, or replace a clinician.
Keep answers concise and easy to understand.
If the user's description suggests a potentially urgent or life-threatening
condition, say so clearly and direct them to Emergency Assistance or local
emergency services.
Do not invent medical facts.
No emojis.

Answer in 3 short sections when appropriate:
What it may mean
What to do now
When to seek urgent help
"""
    try:
        result = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=0.1,
            max_tokens=500,
        )
        return result.choices[0].message.content.strip()
    except Exception:
        return "The health information service is temporarily unavailable. If this may be an emergency, contact your local emergency service."


# -----------------------------
# Home
# -----------------------------
render_brand()

if st.session_state.mode == "home":
    st.markdown(
        '<div class="card"><strong>Emergency Assistance</strong><br>Describe what is happening. Healthify will keep the situation in one continuous conversation and give only the next important actions.</div>',
        unsafe_allow_html=True,
    )

    if st.button("START EMERGENCY ASSISTANCE", type="primary", use_container_width=True):
        start_emergency()
        st.rerun()

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Ask a Health Question", use_container_width=True):
            st.session_state.mode = "general"
            st.rerun()
    with c2:
        if st.button("First Aid Guide", use_container_width=True):
            st.session_state.mode = "guide"
            st.rerun()

    st.markdown(
        '<div class="small-note">Healthify provides general first-response guidance. It does not replace emergency medical professionals. In a life-threatening emergency, contact your local emergency service immediately.</div>',
        unsafe_allow_html=True,
    )

# -----------------------------
# Emergency mode
# -----------------------------
elif st.session_state.mode == "emergency":
    st.subheader("EMERGENCY ASSISTANCE")
    st.write("Tell me what is happening.")

    if st.session_state.current_protocol:
        render_emergency_response(st.session_state.current_protocol)

    text = render_voice_and_text("emergency")

    if text:
        handle_emergency_message(text)
        st.rerun()

    st.divider()
    if st.button("Reset Emergency Session", use_container_width=True):
        reset_session()
        st.rerun()

    render_disclaimer()

# -----------------------------
# General health mode
# -----------------------------
elif st.session_state.mode == "general":
    st.subheader("GENERAL HEALTH INFORMATION")
    st.write("Ask a general health question. If someone may be in immediate danger, use Emergency Assistance instead.")

    if "general_messages" not in st.session_state:
        st.session_state.general_messages = []

    for message in st.session_state.general_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Type a health question...")
    if prompt:
        st.session_state.general_messages.append({"role": "user", "content": prompt})
        answer = general_health_answer(prompt)
        st.session_state.general_messages.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.button("Emergency Assistance", type="primary", use_container_width=True):
        start_emergency()
        st.rerun()
    if st.button("First Aid Guide", use_container_width=True):
        st.session_state.mode = "guide"
        st.rerun()

    render_disclaimer()

# -----------------------------
# First aid guide
# -----------------------------
elif st.session_state.mode == "guide":
    st.subheader("FIRST AID GUIDE")
    st.write("Short reference guidance. For a life-threatening situation, use Emergency Assistance and contact local emergency services.")

    names = {
        "cpr": "CPR",
        "choking": "Choking",
        "severe_bleeding": "Severe bleeding",
        "burns": "Burns",
        "bee_sting": "Bee / insect stings",
        "anaphylaxis": "Severe allergic reaction",
        "seizure": "Seizure",
        "stroke": "Stroke",
        "fracture_injury": "Fractures / serious injury",
        "sprain": "Sprains / strains",
        "nosebleed": "Nosebleed",
        "electric_shock": "Electric shock",
        "heat_illness": "Heat illness",
        "eye_injury": "Eye injury",
        "minor_cut": "Minor cuts",
    }

    selected = st.selectbox("Choose a guide", list(names.keys()), format_func=lambda x: names[x])
    p = PROTOCOLS[selected]

    st.markdown(f'<div class="emergency-card"><strong>{p["name"]}</strong></div>', unsafe_allow_html=True)
    for idx, action in enumerate(protocol_actions(selected), start=1):
        st.markdown(f'<div class="step"><strong>{idx}.</strong> {action}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="warning"><strong>Get professional help:</strong> {p["escalation"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Avoid**")
    for item in p["avoid"]:
        st.write(f"- {item}")

    if st.button("Emergency Assistance", type="primary", use_container_width=True):
        start_emergency()
        st.rerun()
    if st.button("Home", use_container_width=True):
        st.session_state.mode = "home"
        st.rerun()

    render_disclaimer()
