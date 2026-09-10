# 🚨 EmergencyGuide AI

### Stay calm. Take the right next step.

EmergencyGuide AI is a Streamlit MVP for **emergency first-aid guidance**. A user can describe an emergency by typing or speaking, and the application uses Groq to route the description to a predefined emergency pathway.

> **Important:** This is an informational/hackathon MVP. It does not diagnose medical conditions and does not replace emergency medical services or professional medical care.

## What problem does it solve?

During an emergency, people may not know the medical terminology needed to find the right first-aid information. EmergencyGuide AI lets them describe what they see in ordinary language and routes the situation to a short, structured emergency pathway.

The design principle is:

**UNDERSTAND → TRIAGE → GUIDE → GET HELP**

## Key features

- Natural-language emergency routing with Groq
- Groq model: `openai/gpt-oss-120b`
- Text input
- Optional microphone input + speech-to-text
- Curated emergency protocols
- Cardiac-arrest / CPR pathway
- Possible cardiac emergency pathway
- Severe bleeding
- Choking
- Breathing difficulty
- Seizure
- Burns
- Poisoning / suspected overdose
- Serious injury
- Unconsciousness
- Possible stroke
- Safe unknown-emergency fallback
- Country-based emergency-number configuration
- Optional emergency contact
- Optional emergency profile
- Emergency timer
- Emergency Mode with simplified UI
- No authentication
- No external database

## Safety architecture

The LLM is **not** the source of truth for first-aid instructions.

The architecture is:

```text
USER INPUT
    ↓
Groq interprets natural language
    ↓
Structured category
    ↓
Category validation
    ↓
Curated protocol in protocols.py
    ↓
Short user-facing guidance
```

This means the model does not get to invent CPR steps, medication doses, dangerous home remedies, or other emergency procedures.

If the Groq response cannot be parsed or the API is unavailable, the application falls back to the `unknown` pathway.

## Medical guidance sources

The protocol content was designed around authoritative guidance including:

- American Heart Association — 2025 Guidelines for CPR and Emergency Cardiovascular Care
- American Heart Association + American Red Cross — 2024 First Aid Guidelines

Official sources:

- https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines
- https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/adult-basic-life-support
- https://cpr.heart.org/en/resuscitation-science/2024-first-aid-guidelines

**Before production use, have every protocol reviewed by a qualified medical professional and keep it synchronized with current local guidance.**

## Tech stack

- Python
- Streamlit
- Groq API
- `openai/gpt-oss-120b`
- Optional `streamlit-mic-recorder`
- Session state for MVP-only profile/contact storage

## Project structure

```text
EmergencyGuide-AI/
│
├── app.py
├── ai_engine.py
├── protocols.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Run locally

Clone/download the repository and install dependencies:

```bash
pip install -r requirements.txt
```

Create Streamlit secrets:

```text
GROQ_API_KEY = "your_groq_api_key"
```

Then run:

```bash
streamlit run app.py
```

## Streamlit Community Cloud deployment

1. Upload these files to a GitHub repository.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select the GitHub repository.
5. Select `app.py` as the main file.
6. Open the app's **Secrets** settings.
7. Add:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

8. Deploy.

### Never put your Groq API key in GitHub.

Do not add `.streamlit/secrets.toml` to the repository.

## Voice input

Voice is intentionally optional.

The app uses `streamlit-mic-recorder` to capture browser microphone audio and Groq's transcription endpoint with:

```text
whisper-large-v3-turbo
```

If microphone access or transcription fails, users can still use the typing interface.

For the most reliable browser behavior:

- Allow microphone access when the browser asks.
- Use HTTPS/Streamlit Community Cloud for deployment.
- Keep the Type interface available as a fallback.

## Emergency numbers

The MVP includes:

- Pakistan: 1122
- United States: 911
- United Kingdom: 999
- Other: instructs the user to contact their local emergency medical service

The application does **not** claim that it has contacted emergency services.

## Demo scenario

Try:

> My father suddenly collapsed. He is not responding and he is only gasping.

The intended experience is:

1. Natural-language input is interpreted.
2. The situation routes toward possible cardiac arrest.
3. Emergency Mode opens.
4. The app emphasizes contacting emergency services.
5. The predefined CPR pathway is displayed.
6. The emergency timer can be started.
7. Emergency profile/contact options are available.

## Limitations

This MVP does not:

- diagnose medical conditions
- contact emergency services automatically
- send SMS messages
- provide a clinical decision system
- replace dispatcher instructions
- provide a complete pediatric/neonatal emergency protocol library
- store a permanent medical record
- guarantee microphone support on every browser/device

## Privacy

The MVP avoids an external medical database.

Profile and emergency-contact fields are kept in Streamlit session state. They are not intentionally persisted by this project to a database.

Do not enter information you are not comfortable handling in a hackathon MVP.

## Future improvements

- Clinician-reviewed protocol versioning
- Pediatric-specific pathways
- Local poison-control directory
- Better multilingual voice support
- Offline emergency protocol mode
- Accessibility improvements
- Verified local emergency-service directories
- Formal clinical/safety review
- Audit logging that excludes sensitive free-text medical information

## Medical safety disclaimer

EmergencyGuide AI is an informational emergency-guidance tool. It does not diagnose medical conditions and does not replace emergency medical services or professional medical care.

**If someone may be experiencing a life-threatening emergency, contact local emergency medical services immediately and follow dispatcher instructions.**

## License

Choose an appropriate open-source license before publishing the project publicly.
