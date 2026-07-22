# AMU

AMU is a Django web app for chatting with AI "characters" — each one built from a
personality profile (traits, background, speech patterns) and voiced through a
local LLM. Chats can optionally be read aloud with ElevenLabs text-to-speech, and
character profiles can be enriched with factual background pulled from Wikipedia.

## How it works

- **`chat`** — the web chat interface (character selection, message sending).
- **`personality_profiles`** — character definitions, loaded from JSON files in
  `personality_profiles/data/` via `python manage.py load_profiles`.
- **`conversations`** — stores conversation/message history and handles
  text-to-speech (ElevenLabs) for character replies.
- **`agents`** — generates in-character responses. Talks to a local
  [Ollama](https://ollama.com) server by default (`llama3.2` for English,
  `qwen2.5` for Turkish), and can fall back to OpenAI if configured.

## Requirements

- Python 3.12 (the project was built and tested on 3.12)
- [Ollama](https://ollama.com) running locally, with the `llama3.2` and
  `qwen2.5` models pulled — this is the primary LLM provider
- An ElevenLabs API key if you want spoken responses (optional)
- An OpenAI API key if you want the OpenAI fallback provider (optional)

## Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/Nasra7/AMU.git
cd AMU

# 2. Create and activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then edit .env and fill in any keys you have (ElevenLabs, OpenAI, Django secret)

# 5. Set up the database
python manage.py migrate

# 6. Load the built-in character profiles
python manage.py load_profiles

# 7. (Optional) Make sure Ollama is running with the required models
python check_ollama_files.py

# 8. Run the server
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Environment variables

See `.env.example` for the full list. At minimum:

| Variable | Purpose | Required? |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django's cryptographic signing key | Recommended for anything beyond local dev |
| `ELEVENLABS_API_KEY` / `ELEVENLABS_DEFAULT_VOICE_ID` | Text-to-speech for character replies | Only if using voice |
| `OPENAI_API_KEY` | Fallback LLM provider if Ollama is unavailable | Only if using the OpenAI fallback |

## Notes

- The app defaults to SQLite (`db.sqlite3`), created locally on first `migrate`
  — it isn't committed to the repo.
- Uploaded/generated media (character images, generated TTS audio) is stored
  under `media/` and isn't committed either.
