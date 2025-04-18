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
    "German": ["masculine", "feminine", "neuter"],  # der, die, das
}

# Gender articles by language
GENDER_ARTICLES = {
    "German": {
        "masculine": "der",
        "feminine": "die",
        "neuter": "das",
        "plural": "die"
    },
}

# Image generation settings
DEFAULT_IMAGE_MODEL = "stability-ai/sdxl:c221b2b8ef527988fb59bf24a8b97c4561f1c671f73bd389f866bfb27c061316"

# Audio settings
AUDIO_PREFERENCE = ["Forvo", "ElevenLabs"]  # Try Forvo first, then ElevenLabs

# Anki settings
DEFAULT_DECK_NAME = "Default"
DEFAULT_MODEL_NAME = "Basic"
DEFAULT_TAGS = ["auto", "anki-forge"]
