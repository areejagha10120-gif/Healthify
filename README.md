# HEALTHIFY

**Clear guidance when every second matters.**

Healthify is an AI-powered first-response assistance platform built with Streamlit and Groq. It is designed for stressful situations where users need short, clear, actionable guidance without navigating through multiple emergency pages.

> Healthify is not a doctor, diagnostic system, or replacement for emergency medical services. In a life-threatening situation, contact local emergency services immediately.

## Features

- Home dashboard
- Continuous Emergency Assistant conversation
- Text chat with automatic input reset after every message
- Optional voice-to-text input using Groq Whisper
- Protocol-driven emergency guidance
- Emergency state maintained with Streamlit session state
- Emergency Profile with optional fields
- Emergency Contacts with explicit call actions
- Location-dependent Emergency Information / Numbers
- First Aid reference guides
- General Health Chat
- Settings and destructive-action confirmations
- Groq `openai/gpt-oss-120b`
- Mobile-friendly responsive styling
- No emojis
- No hard-coded API key

## Emergency Assistant

The emergency assistant follows this flow:

```text
User describes problem
        ↓
Emergency interpretation
        ↓
Protocol selection
        ↓
Verified local protocol actions
        ↓
Concise conversational response
        ↓
Relevant next question
        ↓
User answers
        ↓
Input clears
        ↓
Emergency state updates
        ↓
Next action
```

The LLM is not allowed to freely invent emergency procedures. Emergency actions come from `emergency_protocols.json`; Groq primarily interprets the conversation and communicates those supplied actions concisely.

## Technology Stack

- Python
- Streamlit
- Groq API
- `openai/gpt-oss-120b`
- Groq Whisper for optional voice transcription
- JSON protocol/configuration files

## Project Structure

```text
healthify/
├── app.py
├── emergency_protocols.json
├── emergency_services.json
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── config.toml
```

## Installation

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd healthify
pip install -r requirements.txt
streamlit run app.py
```

For local secrets, create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-key-here"
```

Never commit that file.

## Groq API Setup

Healthify reads:

```python
st.secrets["GROQ_API_KEY"]
```

with an environment-variable fallback for local development.

## Streamlit Cloud Deployment

1. Push all project files to GitHub.
2. Open Streamlit Cloud.
3. Create a new app from your GitHub repository.
4. Select `app.py` as the main file.
5. Add the secret:

```toml
GROQ_API_KEY = "your-key-here"
```

6. Deploy.

No ngrok, Cloudflare tunnel, Google Colab, or localhost tunnel is required.

## Live Demo

`YOUR_STREAMLIT_APP_LINK`

## Safety Limitations

Emergency instructions are stored separately from application logic so the protocol knowledge can be reviewed and updated without changing the whole UI. The LLM is constrained to communicate the supplied protocol rather than independently inventing procedures.

The MVP stores Emergency Profile and Emergency Contacts in Streamlit session state. This is **not** a secure medical-record or persistent healthcare database.

Emergency numbers are location-dependent and must be verified for the user's current location.

The protocol content should be reviewed by a qualified first-aid/emergency-care professional before Healthify is used as a real-world medical product.

## Disclaimer

Healthify provides general first-response information and does not replace emergency medical professionals, doctors, or local emergency services. In a life-threatening situation, contact emergency services immediately.

## Future Improvements

- Clinically reviewed and versioned protocol library
- Secure encrypted persistent profile storage
- Proper authentication and consent controls
- Region-aware emergency-number verification
- Multilingual emergency guidance
- AED/location integration
- Accessibility and screen-reader testing
- Formal clinical safety evaluation
- Audit logging and protocol version tracking
