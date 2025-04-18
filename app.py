import streamlit as st

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="AnkiForge",
    page_icon="📚",
    layout="wide"
)

import os
import tempfile
import base64
from PIL import Image
from io import BytesIO
import time

from agents.word_interpreter import WordInterpreter
from agents.grammar_checker import GrammarChecker
from agents.prompt_refiner import PromptRefiner
from integrations.image_generator import ImageGenerator
from integrations.audio_fetcher import AudioFetcher
from integrations.anki_uploader import AnkiUploader
from utils.card_compiler import CardCompiler
from config.config import (
    SUPPORTED_LANGUAGES, WORD_TYPES, GENDER_OPTIONS, 
    GENDER_ARTICLES, DEFAULT_LANGUAGE, DEFAULT_DECK_NAME
)

# Initialize session state variables if they don't exist
if 'word_data' not in st.session_state:
    st.session_state.word_data = None
if 'definition' not in st.session_state:
    st.session_state.definition = None
if 'grammar_check' not in st.session_state:
    st.session_state.grammar_check = None
if 'image_path' not in st.session_state:
    st.session_state.image_path = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'card_data' not in st.session_state:
    st.session_state.card_data = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
if 'anki_connected' not in st.session_state:
    st.session_state.anki_connected = False
if 'decks' not in st.session_state:
    st.session_state.decks = [DEFAULT_DECK_NAME]

# Initialize agents and integrations
@st.cache_resource
def load_resources():
    return {
        'word_interpreter': WordInterpreter(),
        'grammar_checker': GrammarChecker(),
        'prompt_refiner': PromptRefiner(),
        'image_generator': ImageGenerator(),
        'audio_fetcher': AudioFetcher(),
        'anki_uploader': AnkiUploader(),
        'card_compiler': CardCompiler()
    }

resources = load_resources()

def reset_session():
    """Reset the session state to start over."""
    st.session_state.word_data = None
    st.session_state.definition = None
    st.session_state.grammar_check = None
    st.session_state.image_path = None
    st.session_state.audio_path = None
    st.session_state.card_data = None
    st.session_state.step = 1

def check_anki_connection():
    """Check if Anki MCP server is running and update connection status."""
    uploader = resources['anki_uploader']
    result = uploader.check_connection()
    
    if result['success']:
        st.session_state.anki_connected = True
        # Get available decks
        decks = uploader.get_deck_names()
        if decks:
            st.session_state.decks = decks
        return True
    else:
        st.session_state.anki_connected = False
        return False

def get_audio_html(audio_path):
    """Generate HTML for audio playback."""
    audio_format = audio_path.split('.')[-1]
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio controls>
            <source src="data:audio/{audio_format};base64,{audio_b64}" type="audio/{audio_format}">
            Your browser does not support the audio element.
        </audio>
    """
    return audio_html

def main():
    st.title("AnkiForge")
    st.subheader("AI-powered flashcard creator for language learning")
    
    # Sidebar for settings and instructions
    with st.sidebar:
        st.header("Settings")
        selected_language = st.selectbox("Target Language", SUPPORTED_LANGUAGES, index=SUPPORTED_LANGUAGES.index(DEFAULT_LANGUAGE))
        
        # Check Anki connection
        if st.button("Check Anki Connection"):
            with st.spinner("Checking connection to Anki..."):
                if check_anki_connection():
                    st.success(f"Connected to Anki MCP Server! Found {len(st.session_state.decks)} decks.")
                else:
                    st.error("Could not connect to Anki MCP Server. Make sure it's installed and running.")
                    st.info("See instructions below for setting up anki-mcp-server.")
        
        # Display connection status
        if st.session_state.anki_connected:
            st.success("✅ Connected to Anki")
        else:
            st.warning("❌ Not connected to Anki")
        
        # Instructions for anki-mcp-server
        with st.expander("Anki MCP Server Setup"):
            st.markdown("""
            ### Setting up anki-mcp-server
            
            1. Make sure Anki is installed on your system
            2. Install anki-mcp-server:
               ```
               pip install anki-mcp-server
               ```
            3. Start the server:
               ```
               anki-mcp-server
               ```
            4. Keep Anki running in the background
            
            For more details, visit: [anki-mcp-server GitHub](https://github.com/nailuogg/anki-mcp-server)
            """)
        
        # Reset button
        if st.button("Start Over"):
            reset_session()
            st.rerun()
    
    # Main workflow
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Create New Flashcard")
        
        # Step 1: Word Input
        if st.session_state.step == 1:
            word = st.text_input("Enter a word in the target language:")
            
            if word:
                # Word type selection
                word_type = st.selectbox("Select word type:", WORD_TYPES[selected_language])
                
                # If noun, ask for gender and plural form
                if word_type == "noun" and selected_language == "German":
                    gender = st.selectbox("Select gender:", GENDER_OPTIONS[selected_language])
                    plural_form = st.text_input("Enter plural form:")
                    
                    if gender and plural_form:
                        article = GENDER_ARTICLES[selected_language][gender]
                        full_word = f"{article} {word}"
                        plural_full = f"{GENDER_ARTICLES[selected_language]['plural']} {plural_form}"
                        st.write(f"Word with article: **{full_word}**")
                        st.write(f"Plural form: **{plural_full}**")
                        
                        if st.button("Generate Definition"):
                            with st.spinner("Generating definition..."):
                                # Store word data
                                st.session_state.word_data = {
                                    "word": word,
                                    "language": selected_language,
                                    "word_type": word_type,
                                    "gender": gender,
                                    "article": article,
                                    "plural_form": plural_form,
                                    "plural_article": GENDER_ARTICLES[selected_language]['plural']
                                }
                                
                                # Generate definition
                                word_interpreter = resources['word_interpreter']
                                definition = word_interpreter.generate_definition(
                                    word, selected_language, word_type, gender, plural_form
                                )
                                st.session_state.definition = definition
                                
                                # Fetch audio
                                audio_fetcher = resources['audio_fetcher']
                                audio_file = os.path.join(st.session_state.temp_dir, f"{word}.mp3")
                                audio_result = audio_fetcher.get_audio(
                                    word, selected_language, audio_file, definition
                                )
                                
                                if audio_result["success"]:
                                    st.session_state.audio_path = audio_result.get("audio_path")
                                
                                # Move to next step
                                st.session_state.step = 2
                                st.rerun()
                else:
                    if st.button("Generate Definition"):
                        with st.spinner("Generating definition..."):
                            # Store word data
                            st.session_state.word_data = {
                                "word": word,
                                "language": selected_language,
                                "word_type": word_type
                            }
                            
                            # Generate definition
                            word_interpreter = resources['word_interpreter']
                            definition = word_interpreter.generate_definition(
                                word, selected_language, word_type
                            )
                            st.session_state.definition = definition
                            
                            # Fetch audio
                            audio_fetcher = resources['audio_fetcher']
                            audio_file = os.path.join(st.session_state.temp_dir, f"{word}.mp3")
                            audio_result = audio_fetcher.get_audio(
                                word, selected_language, audio_file, definition
                            )
                            
                            if audio_result["success"]:
                                st.session_state.audio_path = audio_result.get("audio_path")
                            
                            # Move to next step
                            st.session_state.step = 2
                            st.rerun()
        
        # Step 2: Sentence Input and Grammar Check
        elif st.session_state.step == 2:
            st.subheader("Definition")
            st.write(st.session_state.definition)
            
            if st.session_state.audio_path:
                st.subheader("Pronunciation")
                st.markdown(get_audio_html(st.session_state.audio_path), unsafe_allow_html=True)
            
            st.subheader("Create a Sentence")
            user_sentence = st.text_area("Write a sentence using this word:")
            
            if user_sentence:
                if st.button("Check Grammar"):
                    with st.spinner("Checking grammar..."):
                        # Check grammar
                        grammar_checker = resources['grammar_checker']
                        grammar_check = grammar_checker.check_grammar(
                            user_sentence, 
                            st.session_state.word_data["language"],
                            st.session_state.word_data["word"]
                        )
                        st.session_state.grammar_check = grammar_check
                        
                        # Display grammar check results
                        if grammar_check["is_correct"]:
                            st.success("Your sentence is grammatically correct! ✓")
                        else:
                            st.warning("Grammar issues found:")
                            st.write(f"**Corrected sentence:** {grammar_check['corrected_sentence']}")
                            st.write(f"**Explanation:** {grammar_check['explanation']}")
                        
                        # Ask if user wants to generate an image
                        st.session_state.step = 3
                        st.rerun()
        
        # Step 3: Image Generation
        elif st.session_state.step == 3:
            st.subheader("Generate an Image")
            
            # Display the sentence (corrected if needed)
            if st.session_state.grammar_check["is_correct"]:
                sentence = st.session_state.grammar_check.get("sentence", "")
            else:
                sentence = st.session_state.grammar_check.get("corrected_sentence", "")
            
            st.write(f"**Sentence:** {sentence}")
            
            generate_image = st.checkbox("Generate an image for this sentence?", value=True)
            
            if generate_image:
                if st.button("Generate Image"):
                    with st.spinner("Generating image... This may take a minute."):
                        # Refine prompt
                        prompt_refiner = resources['prompt_refiner']
                        language = st.session_state.word_data["language"]
                        refined_prompt = prompt_refiner.refine_prompt(sentence, language)
                        
                        # Generate image
                        image_generator = resources['image_generator']
                        # Create a unique filename
                        timestamp = int(time.time())
                        safe_word = "".join(c for c in st.session_state.word_data['word'] if c.isalnum() or c in (' ', '_')).rstrip()
                        image_filename = f"ankiforge_{safe_word}_{timestamp}.png"
                        image_file = os.path.join(st.session_state.temp_dir, image_filename) # Use the unique filename
                        image_result = image_generator.generate_image(refined_prompt, save_path=image_file)
                        
                        if image_result["success"]:
                            st.session_state.image_path = image_result.get("image_path") # Store the full path to the temp file
                        
                        # Move to next step
                        st.session_state.step = 4
                        st.rerun()
            else:
                if st.button("Skip Image Generation"):
                    st.session_state.step = 4
                    st.rerun()
        
        # Step 4: Card Preview and Upload
        elif st.session_state.step == 4:
            st.subheader("Card Preview and Upload")
            
            # Compile card data
            if not st.session_state.card_data:
                card_compiler = resources['card_compiler']
                
                # Get the final sentence
                if st.session_state.grammar_check["is_correct"]:
                    sentence = st.session_state.grammar_check.get("sentence", "")
                else:
                    sentence = st.session_state.grammar_check.get("corrected_sentence", "")
                
                st.session_state.card_data = card_compiler.compile_card(
                    st.session_state.word_data,
                    st.session_state.definition,
                    sentence,
                    st.session_state.grammar_check,
                    st.session_state.image_path,
                    st.session_state.audio_path
                )
            
            # Select deck
            selected_deck = st.selectbox("Select Anki Deck:", st.session_state.decks)
            
            # Upload button
            if st.button("Add to Anki"):
                if not st.session_state.anki_connected:
                    st.error("Not connected to Anki. Please check the connection first.")
                else:
                    with st.spinner("Adding card to Anki..."):
                        anki_uploader = resources['anki_uploader']
                        result = anki_uploader.upload_card(
                            st.session_state.card_data,
                            deck_name=selected_deck
                        )
                        
                        if result["success"]:
                            st.success(f"Card successfully added to Anki! Card ID: {result['card_id']}")
                            st.balloons()
                            # Reset for next card after a short delay
                            time.sleep(2)
                            reset_session()
                            st.rerun()
                        else:
                            st.error(f"Failed to add card to Anki: {result['error']}")
                            st.info("Make sure Anki and anki-mcp-server are running.")
    
    with col2:
        st.header("Card Preview")
        
        # Display card preview based on current step
        if st.session_state.step >= 2:
            st.subheader("Front")
            
            # Word with article if applicable
            if st.session_state.word_data.get("word_type") == "noun" and "article" in st.session_state.word_data:
                word_display = f"{st.session_state.word_data['article']} {st.session_state.word_data['word']}"
            else:
                word_display = st.session_state.word_data['word']
                
            st.markdown(f"### {word_display}")
            
            # Audio player
            if st.session_state.audio_path:
                st.markdown(get_audio_html(st.session_state.audio_path), unsafe_allow_html=True)
            
            # Image
            if st.session_state.image_path and st.session_state.step >= 3:
                st.image(Image.open(st.session_state.image_path), use_column_width=True)
            
            # Back of card
            if st.session_state.step >= 2:
                st.subheader("Back")
                
                # Definition
                st.markdown("**Definition:**")
                st.write(st.session_state.definition)
                
                # Sentence
                if st.session_state.step >= 3 and st.session_state.grammar_check:
                    st.markdown("**Example Sentence:**")
                    if st.session_state.grammar_check["is_correct"]:
                        st.write(st.session_state.grammar_check.get("sentence", ""))
                    else:
                        st.write(st.session_state.grammar_check.get("corrected_sentence", ""))
                    
                    # Grammar note
                    if not st.session_state.grammar_check["is_correct"]:
                        st.markdown("**Grammar Note:**")
                        st.write(st.session_state.grammar_check.get("explanation", ""))
                
                # Word metadata for nouns
                if st.session_state.word_data.get("word_type") == "noun" and "plural_form" in st.session_state.word_data:
                    st.markdown("**Word Information:**")
                    st.write(f"Gender: {st.session_state.word_data.get('gender', '')}")
                    plural_display = f"{st.session_state.word_data.get('plural_article', 'die')} {st.session_state.word_data['plural_form']}"
                    st.write(f"Plural: {plural_display}")

if __name__ == "__main__":
    main()
