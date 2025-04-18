import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
FORVO_API_KEY = os.getenv("FORVO_API_KEY")

# ElevenLabs settings
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default to a standard voice

# Anki MCP Server settings
ANKI_MCP_SERVER_URL = os.getenv("ANKI_MCP_SERVER_URL", "http://localhost:8765")

# Language settings
DEFAULT_LANGUAGE = "German"
SUPPORTED_LANGUAGES = ["German"]  # Will be expanded later

# Word types by language
WORD_TYPES = {
    "German": ["noun", "verb", "adjective", "adverb", "preposition", "conjunction", "pronoun"],
}

# Gender options by language (for nouns)
GENDER_OPTIONS = {
    "German": ["der", "die", "das"],  # Use articles for UI selection
}

# Gender articles by language
# Mapping the article choice back to the article itself for consistency
# Also keeping original keys in case they are used elsewhere, but map them to new values too.
GENDER_ARTICLES = {
    "German": {
        "der": "der",         # Map article to itself
        "die": "die",         # Map article to itself
        "das": "das",         # Map article to itself
        "plural": "die",      # Plural article remains 'die'
        # Keep old keys mapping to new values just in case?
        "masculine": "der", 
        "feminine": "die",
        "neuter": "das",
    },
}

# Verb conjugation patterns by language
VERB_CONJUGATIONS = {
    "German": {
        "present": [
            {"person": "ich", "description": "1st person singular"},
            {"person": "du", "description": "2nd person singular"},
            {"person": "er/sie/es", "description": "3rd person singular"},
            {"person": "wir", "description": "1st person plural"},
            {"person": "ihr", "description": "2nd person plural"},
            {"person": "sie/Sie", "description": "3rd person plural / formal"}
        ]
        # Future expansion - add other tenses as needed
        # "past": [...],
        # "future": [...]
    }
    # Future expansion for other languages
    # "Spanish": {...},
    # "French": {...}
}

# Image generation settings
DEFAULT_IMAGE_MODEL = "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316"

# Audio settings
AUDIO_PREFERENCE = ["Forvo", "ElevenLabs"]  # Try Forvo first, then ElevenLabs

# Anki settings
DEFAULT_DECK_NAME = "Default"
DEFAULT_MODEL_NAME = "Basic"
DEFAULT_TAGS = ["auto", "anki-forge"]
