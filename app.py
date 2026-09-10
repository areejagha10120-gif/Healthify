"""
app.py

Healthify - AI-powered emergency first-aid assistant.
Run with: streamlit run app.py
"""

import streamlit as st

from ai_engine import generate_response, AIEngineError, transcribe_audio
from emergency_protocols import (
    detect_situation,
    is_critical_text,
    get_cpr_guidance,
    get_emergency_numbers,
    EMERGENCY_NUMBERS,
    DEFAULT_COUNTRY,
)
from prompts import SAFETY_DISCLAIMER

# ----------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Healthify - Emergency First-Aid Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Global CSS - enforces the required color hierarchy & typography
# ----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Roboto', Helvetica, Arial, sans-serif !important;
}

.main {
    background-color: #FFFFFF;
}

h1, h2, h3, h4 {
    color: #1A1A1A !important;
    font-weight: 700 !important;
}

p, span, label, li {
    color: #2D3748;
}

.hf-tagline {
    color: #2D3748;
    font-size: 1.15rem;
    margin-top: -0.5rem;
}

.hf-card {
    background-color: #F7FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.hf-panel-title {
    color: #E53E3E;
    font-weight: 800;
    letter-spacing: 0.04em;
    font-size: 0.85rem;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.hf-bubble-user {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border-radius: 10px 10px 2px 10px;
    padding: 0.65rem 0.9rem;
    margin: 0.35rem 0;
    max-width: 80%;
    margin-left: auto;
    white-space: pre-wrap;
    font-size: 0.95rem;
}

.hf-bubble-ai {
    background-color: #F7FAFC;
    color: #1A1A1A;
    border: 1px solid #E2E8F0;
    border-radius: 10px 10px 10px 2px;
    padding: 0.65rem 0.9rem;
    margin: 0.35rem 0;
    max-width: 80%;
    margin-right: auto;
    white-space: pre-wrap;
    font-size: 0.95rem;
}

.hf-sender-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: #718096;
    margin-bottom: 0.15rem;
}

.hf-critical-banner {
    background-color: #FFF5F5;
    border: 1px solid #E53E3E;
    color: #9B2C2C;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
}

div.stButton > button[kind="primary"] {
    background-color: #E53E3E;
    border-color: #E53E3E;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #C53030;
    border-color: #C53030;
}

hr {
    border-top: 1px solid #E2E8F0;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------
def init_state():
    defaults = {
        "nav": "HOME",
        "messages": [],  # conversation history: [{"role", "content"}]
        "emergency_mode": False,
        "current_situation": None,  # dict from detect_situation
        "profile": {
            "name": "", "age": "", "blood_group": "", "allergies": "",
            "conditions": "", "medications": "", "notes": "",
        },
        "contacts": [],  # list of {"name","relationship","phone"}
        "country": DEFAULT_COUNTRY,
        "input_mode": "TYPE",
        "pending_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def go_to(page_name, start_emergency=False):
    st.session_state.nav = page_name
    if start_emergency:
        st.session_state.emergency_mode = True
    st.rerun()


def situation_context_summary():
    """Short bullet summary of what's known so far, fed to the AI so it
    does not re-ask already-answered questions."""
    user_turns = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    if not user_turns:
        return None
    bullets = "\n".join(f"- {t}" for t in user_turns[-8:])
    situation_label = ""
    if st.session_state.current_situation:
        situation_label = f"Likely situation: {st.session_state.current_situation['label']}\n"
    return f"{situation_label}User has said, in order:\n{bullets}"


def update_situation_tracking(user_text):
    detected = detect_situation(user_text)
    if detected:
        st.session_state.current_situation = detected
        if detected.get("critical"):
            st.session_state.emergency_mode = True


def append_user_message_and_respond(user_text):
    user_text = (user_text or "").strip()
    if not user_text:
        return
    st.session_state.messages.append({"role": "user", "content": user_text})
    update_situation_tracking(user_text)

    try:
        with st.spinner("Healthify is responding..."):
            reply = generate_response(
                st.session_state.messages,
                situation_context=situation_context_summary(),
            )
        st.session_state.messages.append({"role": "assistant", "content": reply})
        if is_critical_text(user_text) or is_critical_text(reply):
            st.session_state.emergency_mode = True
    except AIEngineError as exc:
        st.session_state.pending_error = str(exc)


def render_message_bubble(role, content):
    if role == "user":
        st.markdown(
            f'<div class="hf-sender-label" style="text-align:right;">You</div>'
            f'<div class="hf-bubble-user">{content}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="hf-sender-label">Healthify</div>'
            f'<div class="hf-bubble-ai">{content}</div>',
            unsafe_allow_html=True,
        )


def last_ai_message_is_question():
    if not st.session_state.messages:
        return False
    last = st.session_state.messages[-1]
    return last["role"] == "assistant" and "?" in last["content"]


# ----------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### HEALTHIFY")
    st.caption("Clear guidance when every second matters.")
    st.markdown("---")
    nav_options = [
        "HOME",
        "EMERGENCY CHAT",
        "EMERGENCY PROFILE",
        "EMERGENCY CONTACTS",
        "EMERGENCY NUMBERS",
        "SAFETY & ABOUT",
    ]
    current_index = nav_options.index(st.session_state.nav) if st.session_state.nav in nav_options else 0
    selected = st.radio("Navigate", nav_options, index=current_index, label_visibility="collapsed")
    if selected != st.session_state.nav:
        st.session_state.nav = selected
        st.rerun()

    st.markdown("---")
    if st.session_state.emergency_mode:
        st.error("EMERGENCY MODE ACTIVE")
        if st.button("End Emergency Mode", use_container_width=True):
            st.session_state.emergency_mode = False
            st.rerun()


# ----------------------------------------------------------------------
# PAGE: HOME
# ----------------------------------------------------------------------
def page_home():
    st.markdown("# HEALTHIFY")
    st.markdown('<p class="hf-tagline">Clear guidance when every second matters.</p>', unsafe_allow_html=True)
    st.write("Get concise, step-by-step first-aid guidance during an emergency.")
    st.write("")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("START EMERGENCY", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_situation = None
            go_to("EMERGENCY CHAT", start_emergency=True)
    with col2:
        if st.button("OPEN EMERGENCY CHAT", use_container_width=True):
            go_to("EMERGENCY CHAT")

    st.write("")
    st.markdown("---")
    st.markdown("#### Quick access")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Emergency Profile", use_container_width=True):
            go_to("EMERGENCY PROFILE")
    with c2:
        if st.button("Emergency Contacts", use_container_width=True):
            go_to("EMERGENCY CONTACTS")
    with c3:
        if st.button("Emergency Numbers", use_container_width=True):
            go_to("EMERGENCY NUMBERS")

    st.markdown("---")
    st.caption(SAFETY_DISCLAIMER)


# ----------------------------------------------------------------------
# PAGE: EMERGENCY CHAT
# ----------------------------------------------------------------------
def render_emergency_panel():
    st.markdown('<div class="hf-panel-title">Emergency Mode</div>', unsafe_allow_html=True)

    situation_label = "Not yet determined"
    if st.session_state.current_situation:
        situation_label = st.session_state.current_situation["label"]
    st.markdown(f"**Situation**\n\n{situation_label}")

    st.markdown("**Immediate action**")
    if st.session_state.current_situation and st.session_state.current_situation["key"] == "cardiac_arrest":
        st.markdown(get_cpr_guidance("adult"))
    else:
        st.markdown("Follow Healthify's latest instruction in the chat. Call emergency services if unsure.")

    st.markdown("---")
    numbers = get_emergency_numbers(st.session_state.country)
    st.markdown("**Emergency Services**")
    for service, number in numbers.items():
        st.markdown(f"{service}: `{number}`")
        st.markdown(f"[CALL {service.upper()}](tel:{number})")

    st.markdown("---")
    st.markdown("**Emergency Contact**")
    if st.session_state.contacts:
        top_contact = st.session_state.contacts[0]
        st.markdown(f"{top_contact['name']} ({top_contact['relationship']})")
        st.markdown(f"[CALL {top_contact['name'].upper()}](tel:{top_contact['phone']})")
    else:
        st.caption("No saved contact yet. Add one in Emergency Contacts.")

    st.markdown("---")
    st.markdown("**Patient**")
    profile = st.session_state.profile
    if profile.get("name"):
        st.markdown(f"Name: {profile.get('name') or '-'}")
        st.markdown(f"Age: {profile.get('age') or '-'}")
        st.markdown(f"Blood Group: {profile.get('blood_group') or '-'}")
        st.markdown(f"Allergies: {profile.get('allergies') or 'None listed'}")
    else:
        st.caption("No profile saved yet. Add one in Emergency Profile.")


def page_emergency_chat():
    st.markdown("## EMERGENCY CHAT")

    if st.session_state.pending_error:
        st.warning(st.session_state.pending_error)
        st.session_state.pending_error = None

    if st.session_state.emergency_mode:
        chat_col, panel_col = st.columns([2, 1])
    else:
        chat_col = st.container()
        panel_col = None
        if st.button("START EMERGENCY", type="primary"):
            st.session_state.emergency_mode = True
            st.rerun()

    with chat_col:
        if not st.session_state.messages:
            st.info(
                "Describe what happened in a few words, for example: "
                "\"My friend was stung by a bee\" or \"My brother has "
                "collapsed and isn't responding.\""
            )

        for msg in st.session_state.messages:
            render_message_bubble(msg["role"], msg["content"])

        # Quick response buttons if the last AI message asked a question
        if last_ai_message_is_question():
            situation = st.session_state.current_situation
            options = situation["quick_responses"] if situation else ["YES", "NO", "NOT SURE"]
            st.write("")
            btn_cols = st.columns(len(options))
            for i, opt in enumerate(options):
                with btn_cols[i]:
                    if st.button(opt, key=f"quick_{opt}_{len(st.session_state.messages)}", use_container_width=True):
                        append_user_message_and_respond(opt.capitalize())
                        st.rerun()

        st.write("")
        mode_cols = st.columns([1, 1, 4])
        with mode_cols[0]:
            if st.button("TYPE", use_container_width=True,
                         type="primary" if st.session_state.input_mode == "TYPE" else "secondary"):
                st.session_state.input_mode = "TYPE"
                st.rerun()
        with mode_cols[1]:
            if st.button("SPEAK", use_container_width=True,
                         type="primary" if st.session_state.input_mode == "SPEAK" else "secondary"):
                st.session_state.input_mode = "SPEAK"
                st.rerun()

        if st.session_state.input_mode == "TYPE":
            user_text = st.chat_input("Type your answer here...")
            if user_text:
                append_user_message_and_respond(user_text)
                st.rerun()
        else:
            audio_value = st.audio_input("Record your answer")
            if audio_value is not None:
                if st.button("Send recorded answer", type="primary"):
                    try:
                        with st.spinner("Transcribing..."):
                            transcript = transcribe_audio(audio_value)
                        if transcript:
                            append_user_message_and_respond(transcript)
                            st.rerun()
                        else:
                            st.warning("Could not hear anything. Please try again or switch to TYPE.")
                    except AIEngineError as exc:
                        st.warning(str(exc))
                        st.caption("You can switch to TYPE mode instead.")

    if panel_col is not None:
        with panel_col:
            with st.container(border=True):
                render_emergency_panel()


# ----------------------------------------------------------------------
# PAGE: EMERGENCY PROFILE
# ----------------------------------------------------------------------
def page_profile():
    st.markdown("## EMERGENCY PROFILE")
    st.caption("Optional. This information can help responders and Healthify give faster, safer guidance.")

    profile = st.session_state.profile
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full name", value=profile.get("name", ""))
            age = st.text_input("Age", value=profile.get("age", ""))
            blood_group = st.selectbox(
                "Blood group",
                ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                index=(["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(profile.get("blood_group", ""))
                       if profile.get("blood_group", "") in ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] else 0),
            )
        with col2:
            allergies = st.text_area("Allergies", value=profile.get("allergies", ""), height=80)
            conditions = st.text_area("Medical conditions", value=profile.get("conditions", ""), height=80)
            medications = st.text_area("Current medications", value=profile.get("medications", ""), height=80)

        notes = st.text_area("Important medical notes", value=profile.get("notes", ""), height=80)

        submitted = st.form_submit_button("SAVE PROFILE", type="primary")
        if submitted:
            st.session_state.profile = {
                "name": name.strip(),
                "age": age.strip(),
                "blood_group": blood_group,
                "allergies": allergies.strip(),
                "conditions": conditions.strip(),
                "medications": medications.strip(),
                "notes": notes.strip(),
            }
            st.success("Profile saved for this session.")

    st.markdown("---")
    st.caption(
        "Profile data is kept only in this browser session and is not "
        "stored permanently by Healthify."
    )


# ----------------------------------------------------------------------
# PAGE: EMERGENCY CONTACTS
# ----------------------------------------------------------------------
def page_contacts():
    st.markdown("## EMERGENCY CONTACTS")
    st.caption("Add the people who should be reached first in an emergency.")

    with st.form("add_contact_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Contact name")
        with c2:
            relationship = st.text_input("Relationship", placeholder="Mother, Doctor, Guardian...")
        with c3:
            phone = st.text_input("Phone number")

        added = st.form_submit_button("ADD CONTACT", type="primary")
        if added:
            if name.strip() and phone.strip():
                st.session_state.contacts.append({
                    "name": name.strip(),
                    "relationship": relationship.strip() or "Contact",
                    "phone": phone.strip(),
                })
                st.success(f"Added {name.strip()}.")
            else:
                st.warning("Name and phone number are required.")

    st.markdown("---")

    if not st.session_state.contacts:
        st.info("No emergency contacts saved yet.")
    else:
        for idx, contact in enumerate(st.session_state.contacts):
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    st.markdown(f"**{contact['name']}**")
                    st.caption(contact["relationship"])
                    st.write(contact["phone"])
                with c2:
                    st.markdown(f"[CALL](tel:{contact['phone']})")
                with c3:
                    if st.button("REMOVE", key=f"remove_contact_{idx}"):
                        st.session_state.contacts.pop(idx)
                        st.rerun()


# ----------------------------------------------------------------------
# PAGE: EMERGENCY NUMBERS
# ----------------------------------------------------------------------
def page_numbers():
    st.markdown("## EMERGENCY NUMBERS")
    st.caption("Configure your country to see the correct local emergency numbers.")

    countries = list(EMERGENCY_NUMBERS.keys())
    current = st.session_state.country if st.session_state.country in countries else DEFAULT_COUNTRY
    country = st.selectbox("Country / Region", countries, index=countries.index(current))
    if country != st.session_state.country:
        st.session_state.country = country
        st.rerun()

    st.markdown("---")
    numbers = get_emergency_numbers(country)
    cols = st.columns(len(numbers))
    for col, (service, number) in zip(cols, numbers.items()):
        with col:
            with st.container(border=True):
                st.markdown(f"**{service}**")
                st.markdown(f"`{number}`")
                st.markdown(f"[CALL NOW](tel:{number})")

    st.markdown("---")
    st.caption(
        "Numbers are provided for convenience based on commonly published "
        "sources and may change. Verify local emergency numbers where you live."
    )


# ----------------------------------------------------------------------
# PAGE: SAFETY & ABOUT
# ----------------------------------------------------------------------
def page_about():
    st.markdown("## SAFETY & ABOUT")
    st.markdown('<div class="hf-critical-banner">' + SAFETY_DISCLAIMER + '</div>', unsafe_allow_html=True)

    st.markdown("#### What Healthify does")
    st.write(
        "Healthify offers short, step-by-step first-aid guidance during "
        "an emergency and helps you decide when professional emergency "
        "help is required."
    )

    st.markdown("#### What Healthify does not do")
    st.write(
        "Healthify does not diagnose conditions, replace medical "
        "professionals, or guarantee outcomes. Always contact your local "
        "emergency service for anything life-threatening."
    )

    st.markdown("#### Data")
    st.write(
        "Profile and contact information you enter are stored only for "
        "the current session and are not sent anywhere except as needed "
        "to generate AI responses to your messages."
    )


# ----------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------
PAGES = {
    "HOME": page_home,
    "EMERGENCY CHAT": page_emergency_chat,
    "EMERGENCY PROFILE": page_profile,
    "EMERGENCY CONTACTS": page_contacts,
    "EMERGENCY NUMBERS": page_numbers,
    "SAFETY & ABOUT": page_about,
}

PAGES.get(st.session_state.nav, page_home)()
