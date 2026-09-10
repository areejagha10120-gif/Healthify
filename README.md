# Healthify

**Clear guidance when every second matters.**

Healthify is an AI-powered emergency first-aid assistant built with
Python and Streamlit, using the Groq API for conversational AI.

Healthify is **not** a replacement for doctors, paramedics, or
emergency services. It provides short, step-by-step first-aid guidance
during an emergency and helps the user decide when professional
emergency help is required.

## Features

- Real-time, conversational emergency chat that remembers context and
  never re-asks answered questions.
- Emergency Mode with a persistent panel showing the current
  situation, immediate action, emergency contact, emergency services,
  and patient information — all without leaving the chat.
- Emergency Profile (name, age, blood group, allergies, conditions,
  medications, notes).
- Emergency Contacts with one-tap CALL links.
- Emergency Numbers configurable by country (Ambulance, Police, Fire &
  Rescue).
- Quick-response buttons (YES / NO / NOT SURE) for fast answers under
  pressure.
- Voice input (SPEAK mode) transcribed via Groq's Whisper endpoint,
  with a clean fallback to typing.
- Clean, professional healthcare-style interface: white, black, and
  red used sparingly and deliberately. No emojis.

## Project structure

```
healthify/
├── app.py                   # Streamlit UI, navigation, session state
├── ai_engine.py              # Groq API calls (chat + voice transcription)
├── emergency_protocols.py    # Situation detection, CPR text, emergency numbers
├── prompts.py                 # System prompt and message building
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup

1. Clone this repository and enter the folder:

   ```bash
   cd healthify
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Groq API key. Create `.streamlit/secrets.toml`:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   # Optional overrides:
   # GROQ_MODEL = "openai/gpt-oss-120b"
   # GROQ_TRANSCRIPTION_MODEL = "whisper-large-v3"
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

## Deploying to Streamlit Cloud

1. Push this repository to GitHub.
2. Create a new app on Streamlit Cloud pointing to `app.py`.
3. In the app's **Secrets** settings, add:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ```

4. Deploy. No other configuration is required.

## Important safety note

Healthify provides AI-assisted first-aid information only. It is not a
replacement for emergency medical services, doctors, or trained
medical professionals. For anything life-threatening, contact your
local emergency service immediately.
