import requests
import os
import json
import miniaudio
import tempfile
from io import BytesIO
from config.config import FORVO_API_KEY, ELEVENLABS_API_KEY, AUDIO_PREFERENCE, ELEVENLABS_VOICE_ID

class AudioFetcher:
    """
    Integration responsible for fetching audio pronunciations from Forvo
    or generating them using ElevenLabs if not available on Forvo.
    """
    
    def __init__(self):
        """Initialize the AudioFetcher with API keys."""
        self.forvo_api_key = FORVO_API_KEY
        self.elevenlabs_api_key = ELEVENLABS_API_KEY
        self.elevenlabs_voice_id = ELEVENLABS_VOICE_ID
        
    def get_audio(self, word, language, save_path=None, fallback_text=None):
        """
        Get audio pronunciation for a word, trying Forvo first and then ElevenLabs.
        
        Args:
            word (str): The word to get pronunciation for
            language (str): The language of the word
            save_path (str, optional): Path to save the audio file
            fallback_text (str, optional): Text to use for TTS if word not found on Forvo
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Whether audio fetching was successful
                - audio_path (str): Path to the saved audio if save_path is provided
                - audio_data (bytes): Raw audio data if save_path is not provided
                - source (str): Source of the audio ("Forvo" or "ElevenLabs")
                - error (str): Error message if fetching failed
        """
        # Try sources in order of preference
        for source in AUDIO_PREFERENCE:
            if source == "Forvo":
                result = self._get_from_forvo(word, language, save_path)
                if result["success"]:
                    return result
            elif source == "ElevenLabs" and fallback_text:
                result = self._get_from_elevenlabs(fallback_text, language, save_path)
                if result["success"]:
                    return result
        
        # If all sources failed
        return {
            "success": False,
            "error": "Could not fetch audio from any source"
        }
    
    def _get_from_forvo(self, word, language, save_path=None):
        """Get pronunciation from Forvo."""
        try:
            # Map language names to Forvo language codes
            language_codes = {
                "German": "de",
                "Polish": "pl",
                # Add more languages as needed
            }
            
            lang_code = language_codes.get(language, "en")
            
            # Forvo API endpoint
            url = f"https://apifree.forvo.com/key/{self.forvo_api_key}/format/json/action/word-pronunciations/word/{word}/language/{lang_code}/order/rate-desc/limit/1"
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Check if pronunciations are available
            if "items" in data and len(data["items"]) > 0:
                # Get the first pronunciation
                pronunciation = data["items"][0]
                audio_url = pronunciation.get("pathmp3")
                
                if audio_url:
                    # Download the audio
                    audio_response = requests.get(audio_url)
                    audio_response.raise_for_status()
                    audio_data = audio_response.content
                    
                    # Save the audio if a path is provided
                    if save_path:
                        with open(save_path, "wb") as f:
                            f.write(audio_data)
                        return {
                            "success": True,
                            "audio_path": save_path,
                            "source": "Forvo"
                        }
                    else:
                        return {
                            "success": True,
                            "audio_data": audio_data,
                            "source": "Forvo"
                        }
            
            return {
                "success": False,
                "error": f"No pronunciation found on Forvo for '{word}' in {language}"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Forvo API request failed: {e}"
            }
        except (KeyError, IndexError) as e:
            return {
                "success": False,
                "error": f"Error parsing Forvo response: {e}"
            }
    
    def _get_from_elevenlabs(self, text, language, save_path=None):
        """Generate pronunciation using ElevenLabs TTS."""
        try:
            # Map language names to ElevenLabs voice IDs
            # These are example IDs - you would need to replace with actual voice IDs
            voice_ids = {
                "German": "XrExE9yKIg1WjnnlVkGX",  # Example German voice ID
                "Polish": "uLBVUmPGcvbERSvULSJa",  # Example Polish voice ID
                # Add more languages as needed
            }
            
            voice_id = voice_ids.get(language, "21m00Tcm4TlvDq8ikWAM")  # Default to English voice
            
            # ElevenLabs API endpoint
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                audio_data = response.content
                
                # Save the audio if a path is provided
                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(audio_data)
                    return {
                        "success": True,
                        "audio_path": save_path,
                        "source": "ElevenLabs"
                    }
                else:
                    return {
                        "success": True,
                        "audio_data": audio_data,
                        "source": "ElevenLabs"
                    }
            else:
                return {
                    "success": False,
                    "error": f"ElevenLabs API error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"ElevenLabs API request failed: {e}"
            }

    def save_audio(self, audio_content: bytes, filename: str) -> str | None:
        """
        Saves audio content to a temporary file.

        Args:
            audio_content (bytes): The audio data.
            filename (str): The desired base filename (without extension).

        Returns:
            str | None: The path to the saved temporary file, or None if saving failed.
        """
        try:
            # Use a temporary file to store the audio before processing/uploading
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", prefix=f"{filename}_") as temp_audio:
                temp_audio.write(audio_content)
                temp_file_path = temp_audio.name
            print(f"Audio saved temporarily to {temp_file_path}")
            return temp_file_path
        except IOError as e:
            print(f"Error saving audio file: {e}")
            return None
