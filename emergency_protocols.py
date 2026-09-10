"""
emergency_protocols.py

Static reference data used across the app:
- Keyword-based situation detection (used to label the current
  situation and to decide when to show quick-response buttons / flag
  life-threatening escalation).
- CPR guidance text.
- Emergency numbers by country.

This module does NOT call any AI. It is a lightweight, deterministic
support layer around the conversational AI in ai_engine.py.
"""

# ---------------------------------------------------------------------
# Situation keyword map
# ---------------------------------------------------------------------
# Each situation has: label, keywords to detect it, whether it is
# considered potentially life-threatening by default, and a short set
# of quick-response options relevant to the most common first
# follow-up question for that situation.

SITUATIONS = {
    "cardiac_arrest": {
        "label": "Possible cardiac arrest / unconscious, not breathing",
        "keywords": [
            "collapsed", "unconscious", "not breathing", "unresponsive",
            "cardiac arrest", "no pulse", "passed out and not waking",
        ],
        "critical": True,
        "quick_responses": ["YES", "NO", "NOT SURE"],
    },
    "choking": {
        "label": "Choking",
        "keywords": ["choking", "can't breathe", "food stuck", "swallowed wrong"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "severe_bleeding": {
        "label": "Severe bleeding",
        "keywords": ["bleeding", "blood everywhere", "cut badly", "hemorrhage", "bleeding badly"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "burns": {
        "label": "Burn injury",
        "keywords": ["burn", "burned", "scald", "fire injury"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "cuts": {
        "label": "Cut / wound",
        "keywords": ["cut", "wound", "gash"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "sting_allergy": {
        "label": "Insect sting / allergic reaction",
        "keywords": ["bee sting", "wasp", "sting", "allergic reaction", "hives", "anaphylaxis"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "fainting": {
        "label": "Fainting",
        "keywords": ["fainted", "fainting", "passed out", "dizzy and fell"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "seizure": {
        "label": "Seizure",
        "keywords": ["seizure", "convulsion", "shaking uncontrollably", "fitting"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "fracture": {
        "label": "Possible fracture",
        "keywords": ["broken bone", "fracture", "can't move arm", "can't move leg"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "sprain": {
        "label": "Sprain",
        "keywords": ["sprain", "twisted ankle", "twisted wrist"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "head_injury": {
        "label": "Head injury",
        "keywords": ["hit head", "head injury", "concussion", "head trauma"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "stroke": {
        "label": "Possible stroke",
        "keywords": ["stroke", "face drooping", "slurred speech", "can't speak", "one side weak"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "chest_pain": {
        "label": "Chest pain",
        "keywords": ["chest pain", "heart attack", "chest tightness", "chest pressure"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "breathing_difficulty": {
        "label": "Breathing difficulty",
        "keywords": ["can't breathe", "shortness of breath", "trouble breathing", "gasping"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "poisoning": {
        "label": "Poisoning",
        "keywords": ["poison", "swallowed chemical", "overdose", "ingested something toxic"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "electric_shock": {
        "label": "Electric shock",
        "keywords": ["electric shock", "electrocuted", "shocked by wire"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "heat_illness": {
        "label": "Heat exhaustion / heat stroke",
        "keywords": ["heat stroke", "heat exhaustion", "overheated", "too hot and dizzy"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "hypothermia": {
        "label": "Hypothermia",
        "keywords": ["hypothermia", "freezing cold", "extremely cold body"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "nosebleed": {
        "label": "Nosebleed",
        "keywords": ["nosebleed", "nose bleeding"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "eye_injury": {
        "label": "Eye injury",
        "keywords": ["eye injury", "something in eye", "eye hurt", "chemical in eye"],
        "critical": False,
        "quick_responses": ["YES", "NO"],
    },
    "drowning": {
        "label": "Drowning",
        "keywords": ["drowning", "pulled from water", "near drowning"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
    "road_accident": {
        "label": "Road accident",
        "keywords": ["car accident", "road accident", "hit by car", "motorbike accident"],
        "critical": True,
        "quick_responses": ["YES", "NO"],
    },
}


def detect_situation(text):
    """
    Very lightweight keyword matcher used to label the current
    situation for the emergency info panel and to flag potential
    life-threatening cases. This is a support signal only -- the AI
    itself decides the actual guidance and escalation language.
    """
    if not text:
        return None
    lowered = text.lower()
    for key, data in SITUATIONS.items():
        for kw in data["keywords"]:
            if kw in lowered:
                return {"key": key, **data}
    return None


def is_critical_text(text):
    """Return True if any known critical keyword appears in text."""
    situation = detect_situation(text)
    return bool(situation and situation.get("critical"))


# ---------------------------------------------------------------------
# CPR guidance (kept short, on purpose, per recognized first-aid basics)
# ---------------------------------------------------------------------

CPR_GUIDANCE = {
    "adult": (
        "CPR MAY BE NEEDED\n\n"
        "1. Call emergency services now.\n"
        "2. Place the person on a firm, flat surface.\n"
        "3. Put both hands in the center of the chest.\n"
        "4. Push hard and fast at 100-120 compressions per minute.\n"
        "5. Allow the chest to fully rise between compressions.\n"
        "6. Continue until they breathe normally or help arrives."
    ),
    "child": (
        "CPR MAY BE NEEDED (CHILD)\n\n"
        "1. Call emergency services now.\n"
        "2. Place the child on a firm, flat surface.\n"
        "3. Use one or two hands in the center of the chest.\n"
        "4. Push hard and fast at 100-120 compressions per minute, "
        "about 1/3 the depth of the chest.\n"
        "5. Allow the chest to fully rise between compressions.\n"
        "6. Continue until they breathe normally or help arrives."
    ),
    "infant": (
        "CPR MAY BE NEEDED (INFANT)\n\n"
        "1. Call emergency services now.\n"
        "2. Place the infant on a firm, flat surface.\n"
        "3. Use two fingers in the center of the chest, just below the "
        "nipple line.\n"
        "4. Push hard and fast at 100-120 compressions per minute, "
        "about 1/3 the depth of the chest.\n"
        "5. Allow the chest to fully rise between compressions.\n"
        "6. Continue until they breathe normally or help arrives."
    ),
}


def get_cpr_guidance(age_group="adult"):
    return CPR_GUIDANCE.get(age_group, CPR_GUIDANCE["adult"])


# ---------------------------------------------------------------------
# Emergency numbers by country (verified, commonly published numbers).
# Configurable -- not hard-coded to a single country as universal.
# ---------------------------------------------------------------------

EMERGENCY_NUMBERS = {
    "Pakistan": {"Ambulance": "1122", "Police": "15", "Fire & Rescue": "16"},
    "United States": {"Ambulance": "911", "Police": "911", "Fire & Rescue": "911"},
    "United Kingdom": {"Ambulance": "999", "Police": "999", "Fire & Rescue": "999"},
    "India": {"Ambulance": "108", "Police": "100", "Fire & Rescue": "101"},
    "Canada": {"Ambulance": "911", "Police": "911", "Fire & Rescue": "911"},
    "Australia": {"Ambulance": "000", "Police": "000", "Fire & Rescue": "000"},
    "European Union (112 zone)": {"Ambulance": "112", "Police": "112", "Fire & Rescue": "112"},
    "United Arab Emirates": {"Ambulance": "998", "Police": "999", "Fire & Rescue": "997"},
    "Saudi Arabia": {"Ambulance": "997", "Police": "999", "Fire & Rescue": "998"},
    "Other / Not Listed": {"Ambulance": "Check local listing", "Police": "Check local listing", "Fire & Rescue": "Check local listing"},
}

DEFAULT_COUNTRY = "Pakistan"


def get_emergency_numbers(country):
    return EMERGENCY_NUMBERS.get(country, EMERGENCY_NUMBERS["Other / Not Listed"])
