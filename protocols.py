"""
Curated emergency first-aid protocols for EmergencyGuide AI.

Safety note:
These are concise first-aid pathways intended for an MVP demonstration.
They should be reviewed by a qualified medical professional before production use.
The AI never generates these steps; it only routes natural-language input to a
predefined category.
"""

EMERGENCY_NUMBERS = {
    "Pakistan": "1122",
    "United States": "911",
    "United Kingdom": "999",
    "Other": None,
}

CATEGORY_LABELS = {
    "cardiac_emergency": "Possible Cardiac Emergency",
    "cardiac_arrest": "Possible Cardiac Arrest",
    "severe_bleeding": "Severe Bleeding",
    "choking": "Choking Emergency",
    "breathing_difficulty": "Breathing Difficulty",
    "seizure": "Seizure",
    "burn": "Burn",
    "poisoning": "Possible Poisoning / Overdose",
    "serious_injury": "Serious Injury",
    "unconsciousness": "Unconsciousness",
    "stroke": "Possible Stroke",
    "unknown": "Unclear Emergency",
}

EMERGENCY_PROTOCOLS = {
    "cardiac_emergency": {
        "title": "Possible Cardiac Emergency",
        "urgency": "critical",
        "message": "Concerning chest symptoms can be a life-threatening emergency.",
        "steps": [
            "Call local emergency medical services immediately.",
            "Keep the person resting and avoid unnecessary exertion.",
            "Stay with the person and monitor their responsiveness and breathing.",
            "Follow the emergency dispatcher's instructions.",
            "If the person becomes unresponsive and is not breathing normally or is only gasping, switch to the cardiac-arrest pathway and begin CPR as directed.",
        ],
        "questions": ["Is the person conscious and responding?"],
        "warnings": [
            "Do not delay emergency care while trying to identify the exact cause.",
            "Do not automatically start CPR on a conscious person with chest pain.",
        ],
        "source_note": "Based on 2024 AHA/American Red Cross first-aid guidance for acute chest pain.",
    },
    "cardiac_arrest": {
        "title": "Possible Cardiac Arrest",
        "urgency": "critical",
        "message": "This may be a life-threatening emergency.",
        "steps": [
            "Call local emergency medical services now, or send someone to call and get an AED if available.",
            "Check responsiveness and normal breathing. If the person is unresponsive and not breathing normally or is only gasping, begin CPR.",
            "For an adult or person showing signs of puberty: give chest compressions and follow emergency-dispatch instructions. If trained and willing, follow dispatcher guidance for breaths.",
            "Use an AED as soon as it is available and follow its voice prompts.",
            "Continue CPR until emergency professionals take over or the person shows clear signs of recovery.",
        ],
        "questions": [],
        "warnings": [
            "Do not spend time trying to diagnose the cause.",
            "For an infant or young child, call emergency services and follow dispatcher instructions for age-appropriate CPR.",
        ],
        "source_note": "Based on the 2025 American Heart Association Adult Basic Life Support guidelines.",
    },
    "severe_bleeding": {
        "title": "Severe Bleeding",
        "urgency": "critical",
        "message": "Life-threatening bleeding can become fatal within minutes.",
        "steps": [
            "Call local emergency medical services immediately.",
            "Apply firm, direct pressure to the bleeding wound with suitable clean material.",
            "Keep steady pressure on the wound and follow dispatcher instructions.",
            "If trained and appropriate for the location of the wound, follow emergency guidance about a tourniquet or wound-packing.",
            "Keep monitoring the person until professional help arrives.",
        ],
        "questions": [],
        "warnings": [
            "Do not remove an embedded object from a wound; apply pressure around it and follow emergency guidance.",
        ],
        "source_note": "Based on the 2024 AHA/American Red Cross first-aid guidelines for life-threatening bleeding.",
    },
    "choking": {
        "title": "Choking Emergency",
        "urgency": "critical",
        "message": "Severe choking can stop breathing and requires immediate action.",
        "steps": [
            "If the person can cough or speak effectively, encourage them to keep coughing and watch closely.",
            "If the person cannot breathe, speak, or cough effectively, call emergency medical services and follow the current choking sequence for their age.",
            "For a conscious adult or child with severe choking, current AHA guidance uses alternating sets of 5 back blows and 5 abdominal thrusts, starting with back blows.",
            "If the person becomes unresponsive, begin CPR and follow dispatcher instructions.",
            "If an object becomes visible in the mouth, remove it only if it can be easily seen; do not blindly sweep the mouth.",
        ],
        "questions": ["Can the person cough or speak effectively?"],
        "warnings": [
            "Infants require a different choking technique. Follow emergency-dispatch instructions for infants.",
        ],
        "source_note": "Based on the 2025 AHA Basic Life Support/foreign-body airway obstruction guidance.",
    },
    "breathing_difficulty": {
        "title": "Breathing Difficulty",
        "urgency": "critical",
        "message": "Severe or worsening breathing difficulty can be life-threatening.",
        "steps": [
            "Call local emergency medical services if breathing difficulty is severe, sudden, worsening, or associated with collapse, blue/gray color, confusion, or inability to speak normally.",
            "Help the person use their own prescribed emergency medication if they have one and can safely use it.",
            "Keep the person in a position that helps them breathe comfortably unless they are unconscious.",
            "Monitor responsiveness and breathing continuously.",
            "If they become unresponsive and are not breathing normally, begin the cardiac-arrest pathway and follow dispatcher instructions.",
        ],
        "questions": [],
        "warnings": [
            "Do not give someone another person's prescription medicine.",
        ],
        "source_note": "General first-aid pathway aligned with AHA/American Red Cross emergency-care principles.",
    },
    "seizure": {
        "title": "Seizure",
        "urgency": "urgent",
        "message": "Protect the person from injury and monitor the duration.",
        "steps": [
            "Move nearby dangerous objects away and help the person safely to the ground if possible.",
            "Do not restrain the person.",
            "Do not put anything in their mouth and do not give food, drink, or oral medicine during the seizure.",
            "If safe, place the person on their side in the recovery position after or during the seizure when appropriate, and stay with them.",
            "Time the seizure. Call emergency medical services for a first seizure, a seizure lasting more than 5 minutes, repeated seizures without recovery, a seizure in water, breathing difficulty/choking, significant injury, pregnancy, or failure to return toward normal after the seizure.",
        ],
        "questions": ["Is the person still having the seizure, and approximately how long has it lasted?"],
        "warnings": [],
        "source_note": "Based on the 2024 AHA/American Red Cross first-aid seizure guidance.",
    },
    "burn": {
        "title": "Burn",
        "urgency": "urgent",
        "message": "Cool a thermal burn promptly and seek professional help when the burn is serious.",
        "steps": [
            "For a thermal burn, cool the area promptly with clean, cool running water when available.",
            "Cooling may be continued for about 5–20 minutes while avoiding whole-body chilling.",
            "Remove jewelry, belts, and other tight items near the burned area before swelling develops, if this can be done safely.",
            "Seek urgent medical evaluation for full-thickness burns, larger burns, burns involving the face, hands, feet, or genitals, or signs of inhalation injury.",
            "Activate emergency medical services for breathing difficulty, facial burns, singed nasal hairs, or soot around the nose or mouth.",
        ],
        "questions": [],
        "warnings": [
            "Do not intentionally cool the whole person or cause hypothermia.",
            "Chemical and electrical burns need professional assessment; avoid experimenting with home treatments.",
        ],
        "source_note": "Based on the 2024 AHA/American Red Cross first-aid burn guidance.",
    },
    "poisoning": {
        "title": "Possible Poisoning / Overdose",
        "urgency": "critical",
        "message": "Poisoning or overdose can become life-threatening quickly.",
        "steps": [
            "Contact local emergency medical services or an appropriate poison-control service immediately.",
            "If the person is unconscious, having trouble breathing, or collapsing, activate emergency medical services immediately.",
            "If safe, keep the container, label, or information about the substance available for responders.",
            "Tell professionals what substance may have been involved and approximately when it happened.",
            "Follow professional instructions rather than trying home remedies.",
        ],
        "questions": [
            "What substance may have been involved?",
            "Is the person conscious and responding?",
            "Is the person breathing normally?",
        ],
        "warnings": [
            "Do not induce vomiting unless a qualified professional specifically tells you to.",
        ],
        "source_note": "Aligned with current AHA resuscitation/first-aid principles for toxicological emergencies.",
    },
    "serious_injury": {
        "title": "Serious Injury",
        "urgency": "critical",
        "message": "A serious injury may require immediate professional assessment.",
        "steps": [
            "Call local emergency medical services for severe injury, major bleeding, loss of consciousness, breathing problems, or rapidly worsening symptoms.",
            "Do not move the person unnecessarily when a serious head, neck, back, or major injury is suspected, unless the scene is unsafe.",
            "Control life-threatening external bleeding with firm direct pressure when appropriate.",
            "Monitor responsiveness and breathing.",
            "Follow emergency-dispatch instructions until professional help arrives.",
        ],
        "questions": [],
        "warnings": [
            "Do not attempt complicated procedures beyond your training.",
        ],
        "source_note": "General first-aid emergency pathway.",
    },
    "unconsciousness": {
        "title": "Unconsciousness",
        "urgency": "critical",
        "message": "Unresponsiveness is an emergency until the cause is established.",
        "steps": [
            "Call local emergency medical services and get nearby help.",
            "Check responsiveness and normal breathing.",
            "If the person is not breathing normally or is only gasping, begin the cardiac-arrest pathway and follow dispatcher instructions.",
            "If they are breathing normally, continue monitoring and follow emergency-dispatch instructions.",
            "Do not give food, drink, or oral medicine to an unconscious person.",
        ],
        "questions": ["Is the person breathing normally?"],
        "warnings": [],
        "source_note": "Based on current AHA Basic Life Support principles.",
    },
    "stroke": {
        "title": "Possible Stroke",
        "urgency": "critical",
        "message": "Sudden facial, arm, or speech changes can be a time-sensitive emergency.",
        "steps": [
            "Call local emergency medical services immediately.",
            "Use FAST: check for sudden Face weakness, Arm weakness, and Speech difficulty.",
            "Note the time the symptoms started, or the last time the person was known to be normal.",
            "Keep the person safe and monitored while waiting for emergency help.",
            "Tell emergency professionals exactly when the symptoms began or were first noticed.",
        ],
        "questions": ["When did the symptoms begin, or when was the person last known to be normal?"],
        "warnings": [
            "Do not wait for symptoms to improve before contacting emergency services.",
        ],
        "source_note": "Based on the 2024 AHA/American Red Cross first-aid stroke guidance.",
    },
    "unknown": {
        "title": "Unclear Emergency",
        "urgency": "urgent",
        "message": "I can't safely determine the situation from this information.",
        "steps": [
            "If the person may be in immediate danger, contact local emergency medical services now.",
            "Check whether the person is conscious and responding.",
            "Check whether they are breathing normally.",
            "Look for severe bleeding, sudden collapse, choking, or a seizure.",
            "Follow emergency-dispatch instructions and do not delay care while trying to identify a diagnosis.",
        ],
        "questions": [
            "Is the person conscious and responding?",
            "Are they breathing normally?",
            "Is there severe bleeding?",
            "Did they suddenly collapse?",
            "Are they choking?",
            "Are they having a seizure?",
        ],
        "warnings": [],
        "source_note": "Safe fallback pathway; not a diagnosis.",
    },
}


def get_protocol(category: str) -> dict:
    """Return a safe protocol, falling back to unknown."""
    return EMERGENCY_PROTOCOLS.get(category, EMERGENCY_PROTOCOLS["unknown"])
