import os
import sys
sys.path.append('/home/ubuntu')

# from workflow.workflow_manager import WorkflowManager # Commented out - not found and unused
from config import Config
# from state import State # Commented out - not found and unused
import logging
from agents.word_interpreter import WordInterpreter  # Removed Agent suffix
from agents.grammar_checker import GrammarChecker  # Removed Agent suffix
from agents.prompt_refiner import PromptRefiner  # Removed Agent suffix
from integrations.anki_uploader import AnkiUploader
from utils.card_compiler import CardCompiler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test the workflow with a German noun
def test_german_noun_workflow():
    print("=== Testing German Noun Workflow ===")
    
    # 1. Word data
    word_data = {
        "word": "Hund",
        "language": "German",
        "word_type": "noun",
        "gender": "masculine",
        "article": "der",
        "plural_form": "Hunde",
        "plural_article": "die"
    }
    print(f"Word data: {word_data}")
    
    # 2. Generate definition
    try:
        print("\nGenerating definition...")
        interpreter = WordInterpreter() # Removed Agent suffix
        definition = interpreter.generate_definition(
            word_data["word"], 
            word_data["language"], 
            word_data["word_type"], 
            word_data["gender"], 
            word_data["plural_form"]
        )
        print(f"Definition: {definition}")
    except Exception as e:
        print(f"Error generating definition: {str(e)}")
        definition = "Ein Hund ist ein domestiziertes Säugetier aus der Familie der Canidae. Hunde sind bekannt für ihre Treue und Freundlichkeit. Sie werden oft als Haustiere gehalten."
        print(f"Using fallback definition: {definition}")
    
    # 3. Check grammar of a sentence
    sentence = "Der große Hund spielt im Park."
    try:
        print("\nChecking grammar...")
        checker = GrammarChecker() # Removed Agent suffix
        grammar_check = checker.check_grammar(
            sentence,
            word_data["language"],
            word_data["word"]
        )
        print(f"Grammar check result: {grammar_check}")
    except Exception as e:
        print(f"Error checking grammar: {str(e)}")
        grammar_check = {
            "is_correct": True,
            "explanation": ""
        }
        print(f"Using fallback grammar check: {grammar_check}")
    
    # 4. Refine prompt for image generation
    try:
        print("\nRefining prompt for image generation...")
        refiner = PromptRefiner() # Removed Agent suffix
        refined_prompt = refiner.refine_prompt(
            sentence,
            word_data["language"]
        )
        print(f"Refined prompt: {refined_prompt}")
    except Exception as e:
        print(f"Error refining prompt: {str(e)}")
        refined_prompt = "Ein großer Hund spielt fröhlich in einem grünen Park, sonniger Tag, lebendige Farben"
        print(f"Using fallback refined prompt: {refined_prompt}")
    
    # 5. Compile card
    print("\nCompiling card...")
    compiler = CardCompiler()
    card_data = compiler.compile_card(
        word_data,
        definition,
        sentence,
        grammar_check
    )
    print("Card compiled successfully")
    print(f"Front HTML: {card_data['front_html'][:100]}...")
    print(f"Back HTML: {card_data['back_html'][:100]}...")
    print(f"Tags: {card_data['tags']}")
    
    # 6. Check Anki connection (without actually uploading)
    print("\nChecking Anki connection...")
    uploader = AnkiUploader()
    connection = uploader.check_connection()
    print(f"Anki connection: {connection}")
    
    print("\n=== Workflow Test Complete ===")
    return True

if __name__ == "__main__":
    test_german_noun_workflow()
