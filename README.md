# Healthify

**Clear guidance when every second matters.**

Healthify is a Streamlit MVP for concise emergency first-response guidance. It is designed for stressful situations where the user needs the next useful action rather than a long medical explanation.

> Healthify is not a diagnostic tool and does not replace emergency medical professionals or local emergency services.

## What it does

- Emergency Mode with one continuous conversation
- Text input plus optional browser microphone input
- Groq-powered emergency description understanding
- Structured, protocol-driven first-aid content
- Session state for emergency context
- Red-flag escalation
- Short numbered instructions
- General Health Information mode
- First Aid Guide
- Configurable emergency-service information
- GitHub + Streamlit Cloud deployment
- Groq model: `openai/gpt-oss-120b`
- Optional Groq speech-to-text: `whisper-large-v3-turbo`

## Safety-first architecture

Healthify does **not** ask the language model to invent emergency procedures.

The flow is:

```text
User
  |
  v
Streamlit UI
  |
  +--> Text / optional voice transcription
  |
  v
Groq interpretation
  |
  v
Allowed protocol selection
  |
  v
emergency_protocols.json
  |
  v
Short verified protocol actions
  |
  v
Next critical question / escalation
```

The LLM is used mainly for understanding the user's description, selecting an allowed protocol, extracting a small set of facts, maintaining conversational context, and answering general health questions. Emergency actions are stored separately in `emergency_protocols.json`.

## Emergency Mode

The user does not need to navigate between separate pages for CPR, choking, bleeding, burns, bee stings, stroke, seizures, and other emergencies.

Healthify keeps the emergency inside one conversation and stores structured state with Streamlit `session_state`.

Important state includes:

- `emergency_active`
- `emergency_type`
- `severity`
- `current_protocol`
- `current_step`
- `user_answers`
- `patient_responsive`
- `breathing_status`
- `bleeding_status`
- `allergy_information`
- `medication_information`
- `emergency_services_called`
- `conversation_history`

## Protocol knowledge base

`emergency_protocols.json` contains the MVP protocol set.

The protocol content is intended to follow recognized first-aid guidance from organizations such as the American Red Cross and American Heart Association. The most important emergency actions should still be reviewed by a qualified medical/first-aid professional before public production use.

Examples covered:

- Unresponsive person
- Adult CPR
- Choking
- Severe bleeding
- Burns
- Bee/insect stings
- Anaphylaxis
- Seizures
- Stroke
- Chest pain
- Breathing difficulty
- Fainting
- Fracture/serious injury
- Poisoning
- Heat illness
- Electric shock
- Nosebleed
- Minor cuts
- Eye injury
- Sprains/strains

## Project structure

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

## Requirements

- Python 3.10+
- A Groq API key
- Streamlit

## Local setup

Clone or download the repository, then run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

For local secrets, create:

```text
.streamlit/secrets.toml
```

and add:

```toml
GROQ_API_KEY = "your_key_here"
```

Never commit that file.

## Streamlit Cloud deployment

1. Create a GitHub repository.
2. Upload all project files.
3. Open Streamlit Cloud.
4. Create a new app from the GitHub repository.
5. Select `app.py` as the main file.
6. Open the app's Secrets settings.
7. Add:

```toml
GROQ_API_KEY = "your_key_here"
```

8. Save the secret.
9. Deploy.

No ngrok, Cloudflare tunnel, Google Colab, or localhost tunnel is required for the final deployment.

## Live Demo

`YOUR_STREAMLIT_APP_LINK`

Replace the placeholder after deployment.

## Security

Never place a Groq API key in:

- `app.py`
- `emergency_protocols.json`
- `README.md`
- GitHub source files
- screenshots
- public configuration files

The repository ignores `.streamlit/secrets.toml` and `.env`.

## Error handling

The app is designed to continue safely when:

- the API key is missing
- Groq is unavailable
- voice transcription fails
- the user submits empty text
- a protocol cannot be identified
- a network request fails

When AI services fail during an emergency, Healthify should not invent replacement medical instructions. The user should be directed toward local emergency services and the local protocol content where available.

## Medical safety limitations

Healthify is an MVP and should not be treated as a certified medical device or emergency dispatch service.

Important limitations:

- Emergency numbers are location-dependent.
- The app does not automatically call emergency services.
- It cannot physically assess breathing, pulse, bleeding, consciousness, injury severity, or airway obstruction.
- Voice transcription can be inaccurate.
- AI classification can be wrong.
- Protocol content should be clinically reviewed before public deployment.
- The app should never delay professional emergency care while gathering information.

For life-threatening situations, users should contact their local emergency service immediately and follow dispatcher instructions.

## Future improvements

- Clinical review and versioning of every protocol
- More complete pediatric protocols
- Country-aware emergency-service configuration
- Retrieval-Augmented Generation using versioned, trusted first-aid references
- Formal protocol testing
- Automated safety regression tests
- Accessibility testing
- Multilingual emergency mode
- Offline emergency reference cache
- Human-reviewed protocol change management
- Optional location-based emergency-number lookup with explicit user permission

## License

Choose an appropriate license before public release.
