import streamlit as st
import re # Add import for regex

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
    GENDER_ARTICLES, DEFAULT_LANGUAGE, DEFAULT_DECK_NAME,
    VERB_CONJUGATIONS
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
# Add state for user plural input and validation result
if 'user_plural_input' not in st.session_state:
    st.session_state.user_plural_input = ""
if 'plural_validation' not in st.session_state:
    st.session_state.plural_validation = None
# Add state for type/gender validation
if 'type_gender_validation' not in st.session_state:
    st.session_state.type_gender_validation = None

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
    
    # Clear new session state variables
    if 'plurality_check' in st.session_state:
        del st.session_state.plurality_check
    if 'conjugations' in st.session_state:
        del st.session_state.conjugations
    if 'conjugation_verification' in st.session_state:
        del st.session_state.conjugation_verification
    # Clear plural input and validation state
    if 'user_plural_input' in st.session_state:
        del st.session_state.user_plural_input
    if 'plural_validation' in st.session_state:
        del st.session_state.plural_validation
    # Clear type/gender validation state
    if 'type_gender_validation' in st.session_state:
        del st.session_state.type_gender_validation

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

# Add CSS for colored feedback boxes
def add_custom_css():
    st.markdown("""
    <style>
    .correct-input {
        border: 2px solid #28a745 !important;
        background-color: rgba(40, 167, 69, 0.1) !important;
    }
    .incorrect-input {
        border: 2px solid #dc3545 !important;
        background-color: rgba(220, 53, 69, 0.1) !important;
    }
    .correction-box {
        background-color: #d4edda;
        color: #155724;
        padding: 8px 12px;
        border-radius: 4px;
        margin: 5px 0;
        font-weight: 500;
        border-left: 4px solid #28a745;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .explanation-box {
        background-color: #e2e3e5;
        color: #383d41;
        padding: 10px 15px;
        border-radius: 4px;
        margin: 10px 0;
        border-left: 4px solid #6c757d;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .status-correct {
        color: #28a745; /* Green */
        font-weight: bold;
    }
    .status-incorrect {
        color: #dc3545; /* Red */
        font-weight: bold;
    }
    /* Add custom styling for conjugation tables */
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("AnkiForge")
    st.subheader("AI-powered flashcard creator for language learning")
    
    # Add custom CSS for feedback styling
    add_custom_css()
    
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
                # --- Word Type and Initial Gender Selection --- 
                # Use callbacks to reset dependent states when type/gender changes
                def reset_dependent_states():
                    st.session_state.type_gender_validation = None
                    st.session_state.plural_validation = None
                    st.session_state.user_plural_input = ""
                
                word_type = st.selectbox(
                    "Select word type:", 
                    WORD_TYPES[selected_language],
                    key="word_type_select",
                    on_change=reset_dependent_states
                )
                
                gender = None
                gender_selection_needed = selected_language in GENDER_OPTIONS and word_type == "noun"
                if gender_selection_needed:
                     gender = st.selectbox(
                         "Select gender:", 
                         GENDER_OPTIONS[selected_language], 
                         index=None, 
                         placeholder="Select gender...",
                         key="gender_select",
                         on_change=reset_dependent_states # Reset if gender changes too
                     )
                
                # --- Type/Gender Validation --- 
                type_gender_validated = False
                type_gender_correct = False
                # Check if ready for type/gender validation (word, type selected, gender selected if needed)
                ready_for_type_gender_validation = bool(word and word_type and (gender is not None if gender_selection_needed else True))
                
                if ready_for_type_gender_validation:
                    if st.button("Validate Word Info", key="validate_type_gender_btn"):
                         with st.spinner(f"Validating type/gender for '{word}'..."):
                             word_interpreter = resources['word_interpreter']
                             validation_result = word_interpreter.validate_word_type_gender(
                                 word, selected_language, word_type, gender
                             )
                             st.session_state.type_gender_validation = validation_result
                             st.rerun()
                            
                    # Display Type/Gender Validation Feedback
                    tg_validation = st.session_state.get('type_gender_validation')
                    if tg_validation:
                        type_gender_validated = True
                        st.markdown("--- T Y P E / G E N D E R   V A L I D A T I O N ---")
                        if not tg_validation.get("success", False):
                             st.error(f"Validation failed: {tg_validation.get('reason', 'Unknown API error')}")
                             # Allow proceeding even if validation fails, but maybe flag it?
                             type_gender_correct = False # Treat failure as incorrect for blocking
                        else:
                            is_type_ok = tg_validation.get("is_type_correct")
                            is_gender_ok = tg_validation.get("is_gender_correct")
                            ai_type = tg_validation.get("ai_word_type")
                            ai_gender = tg_validation.get("ai_gender")
                            ai_reason = tg_validation.get("reason")
                            
                            # Determine overall correctness for blocking
                            if gender_selection_needed:
                                type_gender_correct = is_type_ok and is_gender_ok
                            else:
                                type_gender_correct = is_type_ok # Only type matters
                                
                            # Display feedback
                            if type_gender_correct:
                                st.success("✓ Word Type & Gender seem correct!")
                            else:
                                st.warning("Potential issue with Word Type or Gender:")
                                if not is_type_ok:
                                     st.error(f"Word Type: Incorrect. AI suggests: **{ai_type}**")
                                else:
                                     st.success("Word Type: Correct")
                                    
                                if gender_selection_needed:
                                    if not is_gender_ok:
                                         st.error(f"Gender: Incorrect. AI suggests: **{ai_gender or 'N/A'}**")
                                    else:
                                        st.success("Gender: Correct")
                           
                            # Display AI reason
                            if ai_reason:
                                st.markdown(
                                    f'<div class="explanation-box"><strong>Reason:</strong> {ai_reason}</div>',
                                    unsafe_allow_html=True
                                )
                        st.markdown("--- E N D   T Y P E / G E N D E R   V A L I D A T I O N ---")
                else:
                    # If not ready for validation, ensure validation state is clear
                    st.session_state.type_gender_validation = None

                # Determine if we can proceed to the next input stage (plural/conjugations/definition)
                # Requires word input AND successful type/gender validation
                can_proceed = bool(word and type_gender_validated and type_gender_correct)
                
                if not word:
                     st.info("Please enter a word to begin.")
                elif not ready_for_type_gender_validation:
                     st.info("Please select word type (and gender if applicable) to proceed.")
                elif not type_gender_validated:
                     st.info("Please validate the Word Type/Gender information before proceeding.")
                elif not type_gender_correct:
                     st.error("Please correct the Word Type/Gender based on the validation feedback before proceeding.")
                
                # --- NOUN Specific Handling (Plural) --- 
                if word_type == "noun":
                    # --- User Plural Input & Validation --- 
                    plural_input_ready = False
                    plural_validated = False
                    
                    # Only show plural input if type/gender validation passed
                    if can_proceed:
                        st.subheader("Plural Information") # Add subheader
                        st.session_state.user_plural_input = st.text_input(
                            "Enter your guess for the plural form (leave blank if none):",
                            value=st.session_state.user_plural_input,
                            key="user_plural_input_field",
                            on_change=lambda: st.session_state.update(plural_validation=None) 
                        )
                        
                        user_plural_attempt = st.session_state.user_plural_input.strip()
                        # Allow verifying even if input is blank (to check if it SHOULD be blank)
                        plural_input_ready = True 

                        # Verification Button
                        verify_plural_btn = st.button(
                            "Verify Plural", 
                            key="verify_plural_btn", 
                            disabled=not plural_input_ready # Should always be enabled if we reach here
                        )

                        if verify_plural_btn:
                            with st.spinner(f"Validating plural form in {selected_language}..."):
                                word_interpreter = resources['word_interpreter']
                                validation_result = word_interpreter.validate_user_plural(
                                    word, user_plural_attempt, selected_language
                                )
                                st.session_state.plural_validation = validation_result
                                st.rerun()
                        
                        # Display Plural Validation Feedback
                        validation_data = st.session_state.get('plural_validation')
                        if validation_data:
                            plural_validated = True
                            st.markdown("--- E N D   P L U R A L   V A L I D A T I O N ---")
                            if not validation_data.get("success", False):
                                st.error(f"Validation failed: {validation_data.get('ai_reason', 'Unknown API error')}")
                            else:
                                user_correct = validation_data.get("user_correct")
                                ai_status = validation_data.get("ai_status")
                                ai_form = validation_data.get("ai_plural_form")
                                ai_article = validation_data.get("ai_plural_article")
                                ai_reason = validation_data.get("ai_reason")
                                
                                # Display Correct/Incorrect Status
                                if user_correct:
                                    st.markdown('<span class="status-correct">✓ Correct</span>', unsafe_allow_html=True)
                                elif user_correct is False:
                                     st.markdown('<span class="status-incorrect">✗ Incorrect</span>', unsafe_allow_html=True)
                                     # Show correction if available
                                     if ai_status == "HAS_PLURAL" and ai_form:
                                         correction_display = f"{ai_article} {ai_form}".strip() if ai_article else ai_form
                                         st.markdown(
                                             f'<div class="correction-box">Suggested: <strong>{correction_display}</strong></div>',
                                             unsafe_allow_html=True
                                         )
                                else:
                                    st.warning("Could not determine correctness.")

                                # Display AI Status and Reason (in target language)
                                # REMOVED AI STATUS BOX
                                # if ai_status:
                                #    st.info(f"AI Analysis Status: {ai_status}")
                                if ai_reason:
                                    st.markdown(
                                        f'<div class="explanation-box"><strong>Explanation ({selected_language}):</strong> {ai_reason}</div>',
                                        unsafe_allow_html=True
                                    )
                            st.markdown("--- E N D   P L U R A L   V A L I D A T I O N ---")

                    # --- Preview Word with Article (Singular) --- 
                    # Show this preview earlier, after gender is selected
                    if gender_selection_needed and gender:
                        article = GENDER_ARTICLES[selected_language][gender]
                        full_word = f"{article} {word}"
                        st.write(f"Word with article: **{full_word}**")
                    # elif not gender_selection_needed: # Handled by initial word display?
                    #    st.write(f"Word: **{word}**") # Redundant if word is already shown

                    # --- Generate Definition Button --- 
                    # Ready if type/gender validation passed AND plural has been validated
                    if can_proceed and plural_validated:
                        if st.button("Generate Definition", key="generate_def_noun"):
                            with st.spinner("Generating definition..."):
                                # Get validation data again to store
                                validation_data = st.session_state.plural_validation
                                ai_status = validation_data.get('ai_status')
                                ai_plural_form = validation_data.get('ai_plural_form')
                                ai_plural_article = validation_data.get('ai_plural_article')
                                user_correct = validation_data.get('user_correct')
                                ai_reason = validation_data.get('ai_reason')
                                user_attempt = st.session_state.user_plural_input # Store user's input

                                # Store word data including validation info
                                word_data = {
                                    "word": word,
                                    "language": selected_language,
                                    "word_type": word_type,
                                    # Plural Info
                                    "user_plural_attempt": user_attempt,
                                    "plural_validation_status": ai_status, 
                                    "plural_user_correct": user_correct,
                                    "plural_ai_form": ai_plural_form,
                                    "plural_ai_article": ai_plural_article,
                                    "plural_ai_reason": ai_reason 
                                }
                                
                                # Add gender and article 
                                if selected_language in GENDER_OPTIONS and gender:
                                    word_data.update({
                                        "gender": gender,
                                        "article": GENDER_ARTICLES[selected_language][gender]
                                    })
                                
                                # Determine final plural form/article to use (prefer AI's if available)
                                final_plural_form = ai_plural_form if ai_status == "HAS_PLURAL" else None
                                final_plural_article = ai_plural_article if ai_status == "HAS_PLURAL" else None
                                
                                # Store final forms if they exist
                                if final_plural_form:
                                    word_data["plural_form"] = final_plural_form
                                if final_plural_article:
                                    word_data["plural_article"] = final_plural_article
                                elif ai_status == "HAS_PLURAL" and language == "German": # Default German plural article if missing
                                    word_data["plural_article"] = GENDER_ARTICLES[selected_language].get('plural', 'die')
                                        
                                st.session_state.word_data = word_data
                                
                                # Generate definition using the AI-validated plural form if available
                                word_interpreter = resources['word_interpreter']
                                definition = word_interpreter.generate_definition(
                                    word,
                                    selected_language,
                                    word_type,
                                    gender=gender,
                                    plural_form=final_plural_form 
                                )
                                st.session_state.definition = definition
                                
                                # Fetch audio (use singular word)
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
                
                # Handle VERBS
                elif word_type == "verb":
                    # Check if language has verb conjugation patterns defined
                    if selected_language in VERB_CONJUGATIONS:
                        # Show conjugation form for present tense
                        st.subheader("Enter Present Tense Conjugations")
                        
                        # Create dictionary to store conjugations
                        if 'conjugations' not in st.session_state:
                            st.session_state.conjugations = {}
                        
                        # Display form fields for each person/pronoun
                        conjugation_patterns = VERB_CONJUGATIONS[selected_language]["present"]
                        all_conjugations_provided = True
                        
                        # Track whether we have verification results to apply styling
                        has_verification = 'conjugation_verification' in st.session_state
                        verification = st.session_state.get('conjugation_verification', {})
                        feedback = verification.get('feedback', {})
                        
                        # Use columns for input and feedback
                        with st.container():
                            # Add clear instructions
                            st.info("Enter conjugations for each form, then click 'Verify' to check your answers.")
                            
                            # Create a grid layout with headers
                            col1, col2, col3 = st.columns([2, 3, 3])
                            with col1:
                                st.markdown("**Pronoun**")
                            with col2:
                                st.markdown("**Your Conjugation**")
                            with col3:
                                st.markdown("**Status**")
                            
                            # Display each conjugation with better visual feedback
                            for pattern in conjugation_patterns:
                                pronoun = pattern["person"]
                                description = pattern["description"]
                                
                                # Create a unique key for each input field
                                input_key = f"conj_{selected_language}_{pronoun}"
                                
                                # Get feedback for this pronoun if available
                                pronoun_feedback = feedback.get(pronoun, {})
                                is_pronoun_correct = pronoun_feedback.get("is_correct", True)
                                
                                # Create a row for this conjugation
                                col1, col2, col3 = st.columns([2, 3, 3])
                                
                                with col1:
                                    st.write(f"{pronoun}")
                                    st.caption(f"{description}")
                                
                                with col2:
                                    # Regular input field (we'll apply styling via CSS)
                                    st.session_state.conjugations[pronoun] = st.text_input(
                                        f"Conjugation for {pronoun}",  # Added descriptive label
                                        value=st.session_state.conjugations.get(pronoun, ""),
                                        key=input_key,
                                        placeholder=f"Conjugation for '{pronoun}'",
                                        label_visibility="collapsed" # Hide the label visually
                                    )
                                
                                with col3:
                                    if has_verification:
                                        if pronoun not in feedback:
                                            st.warning("Verification issue")
                                        elif is_pronoun_correct:
                                            st.success("Correct! ✓")
                                        else:
                                            # Show error and correction
                                            correction = verification.get('corrections', {}).get(pronoun, "")
                                            if correction:
                                                st.error(f"Incorrect ✗")
                                                st.markdown(
                                                    f"""<div class="correction-box">
                                                    Correct: <strong>{correction}</strong>
                                                    </div>""", 
                                                    unsafe_allow_html=True
                                                )
                                            else:
                                                st.error(f"Incorrect ✗ (no correction available)")
                                        
                                        # Show debug info in expander if needed
                                        with st.expander("Technical details"):
                                            if pronoun in feedback:
                                                st.write(f"Raw feedback: {feedback[pronoun].get('message', 'No message')}")
                                            else:
                                                st.write("No feedback available for this pronoun")
                                
                                # Check if this conjugation is provided
                                if not st.session_state.conjugations[pronoun]:
                                    all_conjugations_provided = False
                        
                        # Verification button - always show it, but disable if not all fields filled
                        verify_button = st.button(
                            "Verify Conjugations",
                            disabled=not all_conjugations_provided,
                            help="Fill all conjugation fields to enable verification"
                        )
                        
                        if not all_conjugations_provided and not has_verification:
                            st.info("Please complete all conjugation fields to verify.")
                        
                        if verify_button:
                            with st.spinner("Verifying conjugations with AI..."):
                                # Clear any previous verification results
                                if 'conjugation_verification' in st.session_state:
                                    del st.session_state.conjugation_verification
                                
                                # Prepare conjugations data for validation
                                conjugations_data = st.session_state.conjugations
                                
                                # Call API to verify
                                word_interpreter = resources['word_interpreter']
                                verification = word_interpreter.validate_verb_conjugations(
                                    word, conjugations_data, selected_language
                                )
                                
                                # Store verification result
                                st.session_state.conjugation_verification = verification
                                
                                # Force a rerun to update UI with new verification results
                                st.rerun()
                        
                        # If verification was performed, show results summary
                        if has_verification:
                            verification = st.session_state.conjugation_verification
                            
                            st.markdown("---")
                            
                            if not verification["success"]:
                                st.error("Verification failed - please try again")
                                st.write(f"Error: {verification.get('reason', 'Unknown error')}")
                            elif verification["is_correct"]:
                                st.success("🎉 All conjugations are correct!")
                                
                                # Show the overall explanation in a box
                                if verification.get("reason"):
                                    st.markdown(
                                        f"""<div class="explanation-box">
                                        <strong>Explanation:</strong> {verification["reason"]}
                                        </div>""", 
                                        unsafe_allow_html=True
                                    )
                            else:
                                incorrect_count = len(verification.get("corrections", {}))
                                st.warning(f"⚠️ Found {incorrect_count} incorrect conjugation{'s' if incorrect_count > 1 else ''}. Corrections shown above.")
                                
                                # Show the overall explanation in a box
                                if verification.get("reason"):
                                    st.markdown(
                                        f"""<div class="explanation-box">
                                        <strong>Explanation:</strong> {verification["reason"]}
                                        </div>""", 
                                        unsafe_allow_html=True
                                    )
                                    
                                # If we have corrections with incomplete feedback, show a special message
                                if any(pronoun not in feedback for pronoun in st.session_state.conjugations):
                                    st.info("Some conjugations could not be fully verified. Please check your entries carefully.")
                            
                            # Add a "Try again" button to clear verification and try again
                            if st.button("Reset Verification", key="reset_verification"):
                                # Clear verification results but keep entered conjugations
                                if 'conjugation_verification' in st.session_state:
                                    del st.session_state.conjugation_verification
                                st.rerun()
                            
                            # Button to proceed
                            proceed_label = "Continue with These Conjugations"
                            if st.button(proceed_label):
                                with st.spinner("Generating definition..."):
                                    # Store word data with conjugations
                                    st.session_state.word_data = {
                                        "word": word,
                                        "language": selected_language,
                                        "word_type": word_type,
                                        "conjugations": st.session_state.conjugations,
                                        "corrections": verification.get("corrections", {})
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
                    
                    # If language doesn't have conjugation patterns, use the default flow
                    elif can_proceed: # Check added here
                         if st.button("Generate Definition", key="generate_def_verb_simple"):
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
                
                # Handle other word types (adjectives, adverbs, etc.)
                else:
                    if can_proceed:
                         if st.button("Generate Definition", key="generate_def_other"):
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
            
            # Display generated image if available
            if st.session_state.image_path:
                st.image(Image.open(st.session_state.image_path), use_column_width=True)

            # Display the sentence (corrected if needed)
            if st.session_state.grammar_check["is_correct"]:
                sentence = st.session_state.grammar_check.get("sentence", "")
            else:
                sentence = st.session_state.grammar_check.get("corrected_sentence", "")
            
            st.write(f"**Sentence:** {sentence}")
            
            generate_image_checkbox = st.checkbox("Generate an image for this sentence?", value=True, key="gen_img_cb")
            
            if generate_image_checkbox:
                if st.button("Generate Image", key="gen_img_btn"):
                    with st.spinner("Generating image... This may take a minute."):
                        # Refine prompt
                        prompt_refiner = resources['prompt_refiner']
                        language = st.session_state.word_data["language"]
                        refined_prompt = prompt_refiner.refine_prompt(sentence, language)
                        
                        # --- Store prompt for potential regeneration --- 
                        st.session_state.image_prompt = refined_prompt 
                        
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
                        
                        # Don't move step yet, stay on step 3 to allow regeneration
                        # st.session_state.step = 4 # REMOVED
                        st.rerun() # Rerun to show the new image & regen options
            else:
                if st.button("Skip Image Generation", key="skip_img_btn"):
                    st.session_state.image_path = None # Ensure no image path
                    st.session_state.image_prompt = None # Ensure no prompt stored
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
        if st.session_state.step >= 1 and st.session_state.word_data:
            wd = st.session_state.word_data
            st.subheader("Front")
            
            # Word with article if applicable
            word_display = wd['word']
            if wd.get("word_type") == "noun" and "article" in wd:
                 word_display = f"{wd['article']} {wd['word']}"
            elif wd.get("word_type") == "verb":
                 # Maybe add infinitive marker later?
                 pass 
                
            st.markdown(f"### {word_display}")
            
            # Audio player (available from step 2 onwards technically, but word_data exists earlier)
            if st.session_state.audio_path:
                st.markdown(get_audio_html(st.session_state.audio_path), unsafe_allow_html=True)
            
            # Image (available from step 4 onwards)
            if st.session_state.image_path and st.session_state.step >= 4: # Show image later
                try:
                    st.image(Image.open(st.session_state.image_path), use_column_width=True)
                except FileNotFoundError:
                    st.warning("Preview image file not found. It might have been cleared.")
            
            # Back of card (available from step 2 onwards)
            if st.session_state.step >= 2:
                st.subheader("Back")
                
                # Definition
                if st.session_state.definition:
                    st.markdown("**Definition:**")
                    st.write(st.session_state.definition)
                
                # Sentence (available from step 3 onwards)
                if st.session_state.step >= 3 and st.session_state.grammar_check:
                    gc = st.session_state.grammar_check
                    st.markdown("**Example Sentence:**")
                    sentence_to_display = gc.get("corrected_sentence") if not gc.get("is_correct") else gc.get("sentence", "")
                    st.write(sentence_to_display)
                    
                    # Grammar note
                    if not gc.get("is_correct"):
                        st.markdown("**Grammar Note:**")
                        st.write(gc.get("explanation", ""))
                
                # Word metadata (updated for new plural info)
                if wd.get("word_type") == "noun":
                     st.markdown("**Word Information:**")
                     if "gender" in wd:
                         st.write(f"Gender: {wd.get('gender', 'N/A')}")
                     
                     # Updated plural display logic based on validation
                     p_status = wd.get("plural_validation_status")
                     if p_status == "HAS_PLURAL":
                         # Display the AI-confirmed plural form and article
                         p_form = wd.get("plural_ai_form", "N/A") 
                         p_article = wd.get("plural_ai_article", "") 
                         # Use stored final article/form if available
                         if "plural_form" in wd:
                             p_form = wd["plural_form"]
                         if "plural_article" in wd:
                             p_article = wd["plural_article"]
                         
                         plural_display = f"{p_article} {p_form}".strip()
                         st.write(f"Plural: {plural_display}")
                     elif p_status == "NO_PLURAL":
                         st.write("Plural: None (typically)")
                     elif p_status == "ALREADY_PLURAL":
                         st.write("Plural: Already plural or uncountable")
                     else:
                         # Check if validation was even done
                         if wd.get("user_plural_attempt") is not None: # Check if attempt was made
                             st.write(f"Plural: Status unknown (User attempt: {wd.get('user_plural_attempt')})")
                         else:
                             st.write("Plural: Not determined")

if __name__ == "__main__":
    main()
