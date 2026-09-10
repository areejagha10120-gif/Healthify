import time
from datetime import datetime

import streamlit as st

from ai_engine import classify_emergency, transcribe_audio
from protocols import (
    CATEGORY_LABELS,
    EMERGENCY_NUMBERS,
    EMERGENCY_PROTOCOLS,
    get_protocol,
)

try:
    from streamlit_mic_recorder import mic_recorder
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False


st.set_page_config(
    page_title="EmergencyGuide AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------

st.markdown(
    """
<style>
:root {
    --navy: #10233f;
    --navy2: #17345d;
    --soft: #f4f7fb;
    --gray: #667085;
    --red: #c62828;
    --green: #18794e;
    --border: #dce3ec;
}

.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef3f8 100%);
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(135deg, #10233f, #17345d);
    color: white;
    padding: 2.2rem;
    border-radius: 22px;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px rgba(16,35,63,.14);
}

.hero h1 {
    margin: 0 0 .35rem 0;
    font-size: 2.5rem;
}

.hero p {
    margin: 0;
    font-size: 1.1rem;
    opacity: .92;
}

.card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.25rem;
    margin: .5rem 0 1rem 0;
    box-shadow: 0 5px 18px rgba(16,35,63,.06);
}

.emergency-card {
    background: #fff5f5;
    border: 2px solid #d32f2f;
    border-radius: 18px;
    padding: 1.35rem;
    margin-bottom: 1rem;
}

.safe-card {
    background: #f3fbf7;
    border: 1px solid #b7e2cd;
    border-radius: 16px;
    padding: 1rem;
}

.small-muted {
    color: #667085;
    font-size: .9rem;
}

.big-number {
    font-size: 1.15rem;
    font-weight: 700;
}

button[kind="primary"] {
    min-height: 3rem;
}

div[data-testid="stSidebar"] {
    background: #10233f;
}

div[data-testid="stSidebar"] * {
    color: white;
}

.urgent-title {
    color: #b71c1c;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Session state ----------

defaults = {
    "page": "Home",
    "analysis": None,
    "transcript": "",
    "emergency_started": None,
    "timer_running": False,
    "profile": {
        "name": "",
        "blood_group": "",
        "allergies": "",
        "medications": "",
        "important_info": "",
    },
    "contact": {"name": "", "phone": ""},
    "country": "Pakistan",
    "selected_quick": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Helpers ----------

def start_emergency_timer():
    st.session_state.emergency_started = time.time()
    st.session_state.timer_running = True


def stop_emergency_timer():
    st.session_state.timer_running = False


def emergency_link():
    number = EMERGENCY_NUMBERS.get(st.session_state.country)
    return f"tel:{number}" if number else None


def render_timer():
    if st.session_state.emergency_started is None:
        return

    elapsed = int(time.time() - st.session_state.emergency_started)
    minutes, seconds = divmod(elapsed, 60)
    hours, minutes = divmod(minutes, 60)
    formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    st.markdown(
        f"""
        <div class="card">
            <div class="small-muted">Emergency started</div>
            <div class="big-number">
                {datetime.fromtimestamp(st.session_state.emergency_started).strftime("%I:%M:%S %p")}
            </div>
            <div class="small-muted">Elapsed</div>
            <div style="font-size:2rem;font-weight:800;">{formatted}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.timer_running:
        time.sleep(1)
        st.rerun()


def set_analysis(result):
    st.session_state.analysis = result
    st.session_state.page = "Emergency Mode"
    if result.get("urgency") == "critical" and st.session_state.emergency_started is None:
        start_emergency_timer()


def analyze_text(text):
    text = (text or "").strip()
    if not text:
        st.warning("Please describe what is happening first.")
        return

    with st.spinner("Routing the situation..."):
        result = classify_emergency(text)
    set_analysis(result)


def quick_category(category):
    result = {
        "category": category,
        "urgency": get_protocol(category)["urgency"],
        "confidence": 1.0,
        "needs_question": bool(get_protocol(category)["questions"]),
        "question": (
            get_protocol(category)["questions"][0]
            if get_protocol(category)["questions"]
            else None
        ),
        "reason": "Selected directly from the emergency quick-access option.",
    }
    set_analysis(result)


# ---------- Sidebar ----------

with st.sidebar:
    st.markdown("## 🚨 EmergencyGuide AI")
    st.caption("Stay calm. Take the right next step.")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"

    if st.button("🚨 Emergency Mode", use_container_width=True):
        st.session_state.page = "Emergency Mode"

    if st.button("🪪 Emergency Profile", use_container_width=True):
        st.session_state.page = "Emergency Profile"

    if st.button("📞 Emergency Contacts", use_container_width=True):
        st.session_state.page = "Emergency Contacts"

    if st.button("ℹ️ Safety & Sources", use_container_width=True):
        st.session_state.page = "Safety & Sources"

    st.divider()
    st.markdown("### Emergency location")
    st.session_state.country = st.selectbox(
        "Country",
        list(EMERGENCY_NUMBERS.keys()),
        index=list(EMERGENCY_NUMBERS.keys()).index(st.session_state.country),
    )

    number = EMERGENCY_NUMBERS.get(st.session_state.country)
    if number:
        st.markdown(f"**Local emergency number:** `{number}`")
    else:
        st.caption("Use your local emergency medical service number.")

    st.divider()
    st.caption(
        "This MVP provides informational first-aid guidance. It does not diagnose "
        "medical conditions or replace emergency professionals."
    )


# ---------- Home ----------

if st.session_state.page == "Home":
    st.markdown(
        """
        <div class="hero">
            <h1>🚨 EmergencyGuide AI</h1>
            <p>Stay calm. Take the right next step.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card">
            <h3>What is happening?</h3>
            <p>Describe the situation in your own words. You can type or speak.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_speak, tab_type = st.tabs(["🎙️ Speak", "⌨️ Type"])

    with tab_speak:
        st.subheader("Speak what is happening")
        st.caption('Example: "My father suddenly collapsed. He is not responding."')

        if not MIC_AVAILABLE:
            st.info(
                "Microphone input is unavailable in this deployment. "
                "Use the Type tab, or install the optional microphone package."
            )
        else:
            audio = mic_recorder(
                start_prompt="🎙️ Record",
                stop_prompt="⏹️ Stop",
                just_once=False,
                use_container_width=False,
                format="wav",
                key="emergency_mic",
            )
            if audio and audio.get("bytes"):
                audio_id = audio.get("id", str(len(audio["bytes"])))
                if st.session_state.get("last_audio_id") != audio_id:
                    st.session_state.last_audio_id = audio_id
                    try:
                        with st.spinner("Transcribing..."):
                            transcript = transcribe_audio(audio["bytes"])
                        st.session_state.transcript = transcript
                    except Exception as exc:
                        st.error(str(exc))

        if st.session_state.transcript:
            st.markdown("**Here's what we heard:**")
            st.info(st.session_state.transcript)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Use this", type="primary", use_container_width=True):
                    analyze_text(st.session_state.transcript)
            with c2:
                if st.button("Record again", use_container_width=True):
                    st.session_state.transcript = ""
                    st.session_state.last_audio_id = None
                    st.rerun()

    with tab_type:
        st.subheader("Type what is happening")
        text = st.text_area(
            "What is happening?",
            height=160,
            placeholder="Example: My brother suddenly collapsed and is not responding.",
            label_visibility="collapsed",
        )
        if st.button("🚨 Analyze Emergency", type="primary", use_container_width=True):
            analyze_text(text)

    st.markdown("### Quick emergency pathways")
    cols = st.columns(3)
    quick_buttons = [
        ("❤️ Chest / Heart", "cardiac_emergency"),
        ("🫁 Breathing", "breathing_difficulty"),
        ("🩸 Severe Bleeding", "severe_bleeding"),
        ("😵 Unconscious", "unconsciousness"),
        ("🧠 Possible Stroke", "stroke"),
        ("😣 Choking", "choking"),
        ("⚡ Seizure", "seizure"),
        ("🔥 Burn", "burn"),
        ("☠️ Poisoning", "poisoning"),
    ]
    for i, (label, category) in enumerate(quick_buttons):
        with cols[i % 3]:
            if st.button(label, use_container_width=True):
                quick_category(category)

    st.markdown(
        """
        <div class="safe-card">
        <strong>Emergency first:</strong> If someone may be in immediate danger,
        contact local emergency medical services. Do not wait for the AI.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Emergency Mode ----------

elif st.session_state.page == "Emergency Mode":
    analysis = st.session_state.analysis

    if not analysis:
        st.info("No emergency scenario is active yet.")
        if st.button("Go to Home"):
            st.session_state.page = "Home"
            st.rerun()
    else:
        category = analysis.get("category", "unknown")
        protocol = get_protocol(category)

        if analysis.get("urgency") == "critical":
            st.markdown(
                f"""
                <div class="emergency-card">
                    <h1>🚨 {protocol["title"]}</h1>
                    <h3 class="urgent-title">THIS MAY BE A LIFE-THREATENING EMERGENCY</h3>
                    <p>{protocol["message"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="card">
                    <h1>⚠️ {protocol["title"]}</h1>
                    <p>{protocol["message"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if protocol["urgency"] in {"critical", "urgent"}:
            number = EMERGENCY_NUMBERS.get(st.session_state.country)
            if number:
                st.link_button(
                    f"📞 GET EMERGENCY HELP — {number}",
                    f"tel:{number}",
                    type="primary",
                    use_container_width=True,
                )
            else:
                st.error(
                    "If this may be life-threatening, contact your local emergency "
                    "medical service immediately."
                )

        if analysis.get("reason"):
            with st.expander("Why this pathway was selected"):
                st.write(analysis["reason"])
                st.caption(
                    "This is a routing explanation, not a medical diagnosis."
                )

        if protocol["questions"]:
            st.markdown("### One important question")
            st.info(protocol["questions"][0])

        st.markdown("### Immediate actions")
        for idx, step in enumerate(protocol["steps"], 1):
            st.markdown(f"**{idx}.** {step}")

        for warning in protocol["warnings"]:
            st.warning(warning)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⏱ Start / Restart Timer", use_container_width=True):
                start_emergency_timer()
                st.rerun()
        with c2:
            if st.button("⏹ Stop Timer", use_container_width=True):
                stop_emergency_timer()
                st.rerun()
        with c3:
            if st.button("👤 Emergency Contact", use_container_width=True):
                st.session_state.page = "Emergency Contacts"
                st.rerun()

        render_timer()

        st.divider()
        if st.button("🔄 Exit / Start New Situation", use_container_width=True):
            st.session_state.analysis = None
            st.session_state.transcript = ""
            st.session_state.emergency_started = None
            st.session_state.timer_running = False
            st.session_state.page = "Home"
            st.rerun()


# ---------- Profile ----------

elif st.session_state.page == "Emergency Profile":
    st.title("🪪 Emergency Profile")
    st.caption(
        "Optional. This MVP keeps the profile only in the current Streamlit session."
    )

    p = st.session_state.profile
    p["name"] = st.text_input("Name", value=p["name"])
    p["blood_group"] = st.text_input("Blood group", value=p["blood_group"])
    p["allergies"] = st.text_area("Known allergies", value=p["allergies"])
    p["medications"] = st.text_area("Current medications", value=p["medications"])
    p["important_info"] = st.text_area(
        "Important medical information", value=p["important_info"]
    )

    st.warning(
        "Only add information you are comfortable storing in this application. "
        "Do not use this MVP as the sole source of medical information."
    )

    if st.button("💾 Save in Current Session", type="primary"):
        st.session_state.profile = p
        st.success("Emergency profile saved for this session.")

    st.divider()
    st.subheader("Emergency card")
    card = st.session_state.profile
    if any(card.values()):
        st.markdown(
            f"""
            <div class="card">
                <h2>🪪 Emergency Card</h2>
                <p><strong>Name:</strong> {card["name"] or "Not provided"}</p>
                <p><strong>Blood group:</strong> {card["blood_group"] or "Not provided"}</p>
                <p><strong>Allergies:</strong> {card["allergies"] or "Not provided"}</p>
                <p><strong>Medications:</strong> {card["medications"] or "Not provided"}</p>
                <p><strong>Important information:</strong> {card["important_info"] or "Not provided"}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Your emergency card is empty.")


# ---------- Contacts ----------

elif st.session_state.page == "Emergency Contacts":
    st.title("📞 Emergency Contacts")
    c = st.session_state.contact

    c["name"] = st.text_input("Contact name", value=c["name"])
    c["phone"] = st.text_input("Phone number", value=c["phone"])

    st.warning(
        "The MVP does not send SMS messages. It only provides a contact action. "
        "Never claim that a message was sent unless a real messaging service is implemented."
    )

    if st.button("💾 Save Contact", type="primary"):
        st.session_state.contact = c
        st.success("Contact saved for this session.")

    if c["phone"]:
        st.link_button(
            f"📞 Call {c['name'] or 'Emergency Contact'}",
            f"tel:{c['phone']}",
            use_container_width=True,
        )
    else:
        st.info("Add a phone number to enable the call action.")


# ---------- Safety ----------

elif st.session_state.page == "Safety & Sources":
    st.title("ℹ️ Safety & Sources")

    st.markdown(
        """
        ### What EmergencyGuide AI is

        EmergencyGuide AI is an informational emergency-guidance tool. It does
        **not diagnose medical conditions** and does not replace emergency
        medical services or professional medical care.

        ### Safety architecture

        The AI is used only to understand natural-language input and select a
        predefined emergency pathway. The actual first-aid steps are stored in
        `protocols.py` and are not generated by the model.

        If AI analysis fails, the application falls back to an unknown-emergency
        pathway and tells the user to seek professional emergency help.

        ### Privacy

        This MVP uses Streamlit session state for optional profile/contact data.
        It does not intentionally persist medical information in an external
        database and does not print user medical descriptions to the console.

        ### Important limitation

        This is a hackathon/MVP implementation. Medical protocols should be
        reviewed by qualified clinicians and updated against current authoritative
        guidance before any real-world clinical deployment.
        """
    )

    st.markdown("### Authoritative guidance reviewed for this MVP")
    st.markdown(
        """
        - American Heart Association — 2025 Guidelines for CPR and Emergency
          Cardiovascular Care.
        - American Heart Association + American Red Cross — 2024 First Aid
          Guidelines.
        """
    )

    st.caption(
        "The web links in the project README point to the official AHA guidance pages."
    )
