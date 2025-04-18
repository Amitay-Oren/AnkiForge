import requests
import json
import os
from config.config import ANKI_MCP_SERVER_URL, DEFAULT_DECK_NAME, DEFAULT_MODEL_NAME, DEFAULT_TAGS

class AnkiUploader:
    """
    Integration responsible for uploading flashcards to Anki using the anki-mcp-server.
    """
    
    def __init__(self, server_url=ANKI_MCP_SERVER_URL):
        """
        Initialize the AnkiUploader with the anki-mcp-server URL.
        
        Args:
            server_url (str): URL of the anki-mcp-server (default from config)
        """
        self.server_url = server_url
        
    def upload_card(self, card_data, deck_name=DEFAULT_DECK_NAME, model_name=DEFAULT_MODEL_NAME, additional_tags=None):
        """
        Upload a flashcard to Anki using the anki-mcp-server.
        
        Args:
            card_data (dict): Dictionary containing the compiled card data:
                - front_html (str): HTML content for the front of the card
                - back_html (str): HTML content for the back of the card
                - tags (list): List of tags for the card
                - media_files (list): List of media files to include
            deck_name (str): Name of the Anki deck to add the card to
            model_name (str): Name of the Anki note model to use
            additional_tags (list, optional): Additional tags to add to the card
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the upload was successful
                - card_id (int): ID of the created card if successful
                - error (str): Error message if upload failed
        """
        try:
            # Combine tags
            tags = card_data.get("tags", []) + (additional_tags or []) + DEFAULT_TAGS
            tags = list(set(tags))  # Remove duplicates
            
            # Prepare the note data
            note = {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": {
                    "Front": card_data["front_html"],
                    "Back": card_data["back_html"]
                },
                "tags": tags,
                "options": {
                    "allowDuplicate": False
                }
            }
            
            # First, check if anki-mcp-server is running
            try:
                response = requests.post(
                    self.server_url,
                    json={
                        "action": "deckNames",
                        "version": 6
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"anki-mcp-server not responding: HTTP {response.status_code}"
                    }
                    
                # Check if the deck exists, create it if not
                decks = response.json().get("result", [])
                if deck_name not in decks:
                    self._create_deck(deck_name)
                
            except requests.exceptions.ConnectionError:
                return {
                    "success": False,
                    "error": "Could not connect to anki-mcp-server. Make sure it's installed and running."
                }
            
            # Upload media files first
            for media_file in card_data.get("media_files", []):
                media_upload_result = self._upload_media(media_file)
                # Check if the upload was successful or if there was an error reported by the API
                if media_upload_result.get("error") is not None:
                    # If error is not None, upload failed
                    return {
                        "success": False,
                        "error": f"Failed to upload media file '{os.path.basename(media_file)}': {media_upload_result['error']}"
                    }
                # Optional: check if result is the expected filename, though storeMediaFile might return None on success
                # if media_upload_result.get("result") != os.path.basename(media_file):
                #    st.warning(f"Media file {os.path.basename(media_file)} uploaded, but API result was unexpected: {media_upload_result.get('result')}")
            
            # Add the note
            response = requests.post(
                self.server_url,
                json={
                    "action": "addNote",
                    "version": 6,
                    "params": {
                        "note": note
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("error"):
                    return {
                        "success": False,
                        "error": result["error"]
                    }
                else:
                    return {
                        "success": True,
                        "card_id": result.get("result")
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error uploading card: {str(e)}"
            }
    
    def _create_deck(self, deck_name):
        """Create a new deck in Anki."""
        try:
            response = requests.post(
                self.server_url,
                json={
                    "action": "createDeck",
                    "version": 6,
                    "params": {
                        "deck": deck_name
                    }
                }
            )
            return response.status_code == 200
        except:
            return False
    
    def _upload_media(self, file_path):
        """Upload a media file to Anki. Returns the API response dictionary."""
        try:
            filename = os.path.basename(file_path)
            
            with open(file_path, "rb") as f:
                file_data = f.read()
                
            # Convert binary data to base64
            import base64
            file_data_b64 = base64.b64encode(file_data).decode("utf-8")
            
            response = requests.post(
                self.server_url,
                json={
                    "action": "storeMediaFile",
                    "version": 6,
                    "params": {
                        "filename": filename,
                        "data": file_data_b64
                    }
                }
            )
            
            if response.status_code == 200:
                return response.json() # Return the full JSON response
            else:
                # Return an error structure similar to other methods
                return {
                    "result": None,
                    "error": f"HTTP error {response.status_code} uploading media {filename}"
                }
        except FileNotFoundError:
            return {
                "result": None,
                "error": f"Media file not found: {file_path}"
            }
        except Exception as e:
             return {
                "result": None,
                "error": f"Exception uploading media {filename}: {str(e)}"
            }
            
    def get_deck_names(self):
        """Get a list of all deck names in Anki."""
        try:
            response = requests.post(
                self.server_url,
                json={
                    "action": "deckNames",
                    "version": 6
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("result", [])
            else:
                return []
        except:
            return []
            
    def check_connection(self):
        """Check if anki-mcp-server is running and accessible."""
        try:
            response = requests.post(
                self.server_url,
                json={
                    "action": "version",
                    "version": 6
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "version": result.get("result")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP error: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
