"""
ai_engine.py

Thin wrapper around the Groq API used to generate Healthify's
conversational responses. Keeps all network/error-handling logic in one
place so app.py stays focused on UI and state.
"""

import streamlit as st
from groq import Groq
from prompts import build_messages

DEFAULT_MODEL = "openai/gpt-oss-120b"


class AIEngineError(Exception):
    """Raised for any recoverable AI-engine failure, with a
    user-friendly message already attached."""
    pass


def _get_client():
    api_key = st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        raise AIEngineError(
            "Healthify's AI connection is not configured. Please add "
            "GROQ_API_KEY to Streamlit secrets to enable the chat."
        )
    try:
        return Groq(api_key=api_key)
    except Exception:
        raise AIEngineError(
            "Could not initialize the AI connection. Please check your "
            "API key configuration."
        )


def get_model_name():
    return st.secrets.get("GROQ_MODEL", DEFAULT_MODEL)


DEFAULT_TRANSCRIPTION_MODEL = "whisper-large-v3"


def transcribe_audio(audio_file):
    """
    Transcribe a recorded answer using Groq's Whisper endpoint, so voice
    input becomes a normal text message in the conversation.

    audio_file: a file-like object (e.g. from st.audio_input), which
        exposes .name and can be read as bytes.

    Returns: transcribed text (str), or "" if nothing could be
    transcribed.
    Raises: AIEngineError with a friendly message on failure.
    """
    client = _get_client()
    try:
        audio_bytes = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
        filename = getattr(audio_file, "name", "recording.wav")
        transcription = client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model=st.secrets.get("GROQ_TRANSCRIPTION_MODEL", DEFAULT_TRANSCRIPTION_MODEL),
        )
        text = getattr(transcription, "text", "") or ""
        return text.strip()
    except AIEngineError:
        raise
    except Exception:
        raise AIEngineError(
            "Could not process the voice recording. Please try again or "
            "switch to TYPE mode."
        )


def generate_response(conversation_history, situation_context=None):
    """
    Generate the next Healthify AI message given the full conversation
    history so far.

    conversation_history: list of {"role": "user"/"assistant", "content": str}
    situation_context: optional short string summary of what's already
        known, used to prevent repeated questions.

    Returns: the AI's reply text (str).
    Raises: AIEngineError with a friendly message on any failure.
    """
    if not conversation_history:
        raise AIEngineError("There is no conversation to respond to yet.")

    client = _get_client()
    messages = build_messages(conversation_history, situation_context)

    try:
        completion = client.chat.completions.create(
            model=get_model_name(),
            messages=messages,
            temperature=0.3,
            max_tokens=400,
        )
    except Exception as exc:
        message = str(exc).lower()
        if "api key" in message or "unauthorized" in message or "401" in message:
            raise AIEngineError(
                "The AI service rejected the API key. Please check your "
                "GROQ_API_KEY in Streamlit secrets."
            )
        if "rate limit" in message or "429" in message:
            raise AIEngineError(
                "The AI service is busy right now. Please try again in a "
                "moment. If this is a real emergency, contact emergency "
                "services immediately instead of waiting."
            )
        raise AIEngineError(
            "Could not reach the AI service due to a network or service "
            "error. If this is a real emergency, contact emergency "
            "services immediately."
        )

    try:
        reply = completion.choices[0].message.content
        if not reply or not reply.strip():
            raise ValueError("empty reply")
        return reply.strip()
    except Exception:
        raise AIEngineError(
            "The AI service returned an unexpected response. Please try "
            "again."
        )
