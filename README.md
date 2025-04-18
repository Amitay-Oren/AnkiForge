# AnkiForge

AnkiForge is an AI-powered, grammar-aware flashcard creator for language learning that outputs directly into Anki using the anki-mcp-server.

## Features

- Create flashcards with native-language definitions (not translations)
- Grammar checking for your example sentences
- Image generation based on your sentences
- Audio pronunciation from Forvo or ElevenLabs
- Direct integration with Anki via anki-mcp-server
- Clean, step-by-step user interface
- Currently supports German (modular design for adding more languages)

## Installation

### Prerequisites

- Python 3.10 or higher
- Anki installed on your system
- API keys for:
  - OpenAI (for GPT-4)
  - Replicate (for image generation)
  - Forvo (for audio pronunciations)
  - ElevenLabs (for fallback audio)
- **FFmpeg:** Required by the `pydub` library for audio processing. Download from [ffmpeg.org](https://ffmpeg.org/download.html) and ensure it's added to your system's PATH.

### Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/AnkiForge.git
   cd AnkiForge
   ```

2. Install required dependencies:
   ```
   pip install streamlit openai replicate python-dotenv requests pillow pydub
   ```

3. Install anki-mcp-server:
   ```
   # Ensure Node.js and npm are installed
   # Then run the server using npx in a separate terminal (see Usage section)
   # No separate install command needed if using npx
   ```

4. Create a `.env` file in the project root directory with your API keys:
   ```
   # Copy from .env.template
   cp .env.template .env
   # Edit the .env file with your API keys
   nano .env
   ```

5. Fill in your API keys in the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   REPLICATE_API_KEY=your_replicate_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   FORVO_API_KEY=your_forvo_api_key_here
   ANKI_MCP_SERVER_URL=http://localhost:8765
   ```

## Usage

1. Start the anki-mcp-server in a separate terminal (requires Node.js/npm):
   ```
   npx --yes anki-mcp-server
   ```

2. Make sure Anki is running in the background with the AnkiConnect add-on installed and enabled.

3. Start the AnkiForge application:
   ```