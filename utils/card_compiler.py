import os

class CardCompiler:
    """
    Utility responsible for assembling all components into a complete Anki flashcard.
    """
    
    def __init__(self):
        """Initialize the CardCompiler."""
        pass
    
    def compile_card(self, word_data, definition, sentence, grammar_check, image_path=None, audio_path=None):
        """
        Compile all components into a complete Anki flashcard.
        
        Args:
            word_data (dict): Dictionary containing word information:
                - word (str): The word itself
                - language (str): The language of the word
                - word_type (str): Type of word (noun, verb, etc.)
                - gender (str, optional): Gender for nouns
                - article (str, optional): Article for nouns
                - plural_form (str, optional): Plural form for nouns
            definition (str): Native-language definition of the word
            sentence (str): User's sentence using the word (corrected if needed)
            grammar_check (dict): Grammar check results:
                - is_correct (bool): Whether the sentence is grammatically correct
                - corrected_sentence (str): Corrected version if there are errors
                - explanation (str): Explanation of errors and corrections
            image_path (str, optional): Path to the generated image
            audio_path (str, optional): Path to the audio pronunciation
            
        Returns:
            dict: A dictionary containing the compiled card data ready for Anki:
                - front_html (str): HTML content for the front of the card
                - back_html (str): HTML content for the back of the card
                - tags (list): List of tags for the card
                - media_files (list): List of media files to include
        """
        # Extract word information
        word = word_data.get("word", "")
        language = word_data.get("language", "")
        word_type = word_data.get("word_type", "")
        
        # Format the word display (with article for nouns)
        if word_type == "noun" and "article" in word_data:
            word_display = f"{word_data['article']} {word}"
        else:
            word_display = word
            
        # Determine which sentence to use (original or corrected)
        if grammar_check["is_correct"]:
            final_sentence = sentence
            grammar_note = ""
        else:
            final_sentence = grammar_check.get("corrected_sentence", sentence)
            grammar_note = grammar_check.get("explanation", "")
            
        # Prepare media files list
        media_files = []
        if image_path:
            media_files.append(image_path)
        if audio_path:
            media_files.append(audio_path)
            
        # Extract filenames from paths using os.path.basename for cross-platform compatibility
        image_filename = os.path.basename(image_path) if image_path else ""
        audio_filename = os.path.basename(audio_path) if audio_path else ""
            
        # Generate front HTML
        front_html = f"""
        <div class="card-front">
            <div class="word">{word_display}</div>
        """
        
        if audio_filename:
            front_html += f"""
            <div class="audio">[sound:{audio_filename}]</div>
            """
            
        if image_filename:
            front_html += f"""
            <div class="image"><img src="{image_filename}" alt="{word}"></div>
            """
            
        front_html += "</div>"
        
        # Generate back HTML
        back_html = f"""
        <div class="card-back">
            <div class="word">{word_display}</div>
            <div class="definition">{definition}</div>
            <div class="sentence">{final_sentence}</div>
        """
        
        if grammar_note:
            back_html += f"""
            <div class="grammar-note">{grammar_note}</div>
            """
            
        # Add word metadata for nouns
        if word_type == "noun" and "plural_form" in word_data:
            plural_display = f"{word_data.get('plural_article', 'die')} {word_data['plural_form']}"
            back_html += f"""
            <div class="metadata">
                <div class="gender">{word_data.get('gender', '')}</div>
                <div class="plural">{plural_display}</div>
            </div>
            """
            
        back_html += "</div>"
        
        # Generate tags
        tags = ["anki-forge", word_type, language.lower()]
        
        return {
            "front_html": front_html.strip(),
            "back_html": back_html.strip(),
            "tags": tags,
            "media_files": media_files
        }
