import json
import re
from typing import Any, Dict, Optional

import streamlit as st
from groq import Groq

from protocols import EMERGENCY_PROTOCOLS

MODEL_NAME = "openai/gpt-oss-120b"
ALLOWED_CATEGORIES = set(EMERGENCY_PROTOCOLS.keys())


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Safely extract a JSON object from a model response."""
    text = (text or "").strip()

    # Remove common markdown fences.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass

    # Fallback: find the first plausible JSON object.
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        return None

    try:
        value = json.loads(match.group(0))
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        return None


def _validate_result(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate model output and fail safely."""
    if not isinstance(data, dict):
        return {
            "category": "unknown",
            "urgency": "urgent",
            "confidence": 0.0,
            "needs_question": True,
            "question": "Is the person conscious and responding?",
            "reason": "The AI response could not be safely interpreted.",
        }

    category = data.get("category", "unknown")
    if category not in ALLOWED_CATEGORIES:
        category = "unknown"

    urgency = data.get("urgency", "urgent")
    if urgency not in {"routine", "urgent", "critical"}:
        urgency = "urgent"

    try:
        confidence = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    question = data.get("question")
    if not isinstance(question, str):
        question = None

    reason = data.get("reason")
    if not isinstance(reason, str):
        reason = "The description was routed to a predefined emergency pathway."

    return {
        "category": category,
        "urgency": urgency,
        "confidence": confidence,
        "needs_question": bool(data.get("needs_question", False)),
        "question": question,
        "reason": reason[:500],
    }


def _client() -> Groq:
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets before using AI analysis."
        )
    return Groq(api_key=api_key)


def classify_emergency(user_text: str) -> Dict[str, Any]:
    """
    Classify natural-language input into a predefined category.
    The model does NOT generate first-aid instructions.
    """
    if not user_text or not user_text.strip():
        return {
            "category": "unknown",
            "urgency": "urgent",
            "confidence": 0.0,
            "needs_question": True,
            "question": "Please briefly describe what is happening.",
            "reason": "No emergency description was provided.",
        }

    system_prompt = """
You are the triage-routing component of EmergencyGuide AI.

Your ONLY job is to interpret the user's plain-language description and route it
to exactly one predefined emergency category. You are NOT a doctor, and you
must not diagnose a disease or generate medical treatment instructions.

Allowed categories:
- cardiac_emergency
- cardiac_arrest
- severe_bleeding
- choking
- breathing_difficulty
- seizure
- burn
- poisoning
- serious_injury
- unconsciousness
- stroke
- unknown

Important routing rules:
1. If a person is described as unresponsive AND not breathing normally / only
   gasping, use cardiac_arrest.
2. Do not use cardiac_arrest merely because someone has chest pain.
3. Chest pressure/pain with concerning associated symptoms while conscious
   should generally route to cardiac_emergency.
4. Sudden face/arm/speech changes should route to stroke.
5. Never claim certainty or diagnosis.
6. If information is insufficient or ambiguous, use unknown and ask one short,
   high-value question.
7. Prefer safety: potentially dangerous ambiguous situations should not be
   falsely downgraded.
8. Do not output treatment steps.

Return ONLY valid JSON with this schema:
{
  "category": "one_allowed_category",
  "urgency": "routine|urgent|critical",
  "confidence": 0.0,
  "needs_question": true,
  "question": "short question or null",
  "reason": "brief routing reason"
}
"""

    try:
        client = _client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            max_tokens=300,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text.strip()},
            ],
        )
        raw = response.choices[0].message.content or ""
        return _validate_result(_extract_json(raw))
    except Exception:
        # Never expose provider/API details to the user.
        return {
            "category": "unknown",
            "urgency": "urgent",
            "confidence": 0.0,
            "needs_question": True,
            "question": "Is the person conscious and responding?",
            "reason": "AI analysis is temporarily unavailable.",
        }


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Optional speech-to-text using Groq's audio transcription endpoint.
    If transcription fails, raise a user-safe exception.
    """
    if not audio_bytes:
        raise ValueError("No audio was recorded.")

    try:
        client = _client()
        result = client.audio.transcriptions.create(
            file=("emergency_input.wav", audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="text",
        )
        text = getattr(result, "text", result)
        if not isinstance(text, str) or not text.strip():
            raise ValueError("No speech could be transcribed.")
        return text.strip()
    except Exception as exc:
        raise RuntimeError(
            "Speech-to-text is temporarily unavailable. You can use the typing option instead."
        ) from exc
