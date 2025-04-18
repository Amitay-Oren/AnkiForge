import unittest
import os
import sys
sys.path.append('/home/ubuntu')

from AnkiForge.agents.word_interpreter import WordInterpreter
from AnkiForge.agents.grammar_checker import GrammarChecker
from AnkiForge.agents.prompt_refiner import PromptRefiner
from AnkiForge.utils.card_compiler import CardCompiler

class TestAnkiForgeComponents(unittest.TestCase):
    """Test cases for AnkiForge core components."""
    
    def setUp(self):
        """Set up test environment."""
        # Skip tests that require API keys if they're not available
        self.skip_api_tests = not os.environ.get("OPENAI_API_KEY")
        
    def test_word_interpreter_initialization(self):
        """Test that WordInterpreter can be initialized."""
        interpreter = WordInterpreter()
        self.assertIsInstance(interpreter, WordInterpreter)
        
    def test_grammar_checker_initialization(self):
        """Test that GrammarChecker can be initialized."""
        checker = GrammarChecker()
        self.assertIsInstance(checker, GrammarChecker)
        
    def test_prompt_refiner_initialization(self):
        """Test that PromptRefiner can be initialized."""
        refiner = PromptRefiner()
        self.assertIsInstance(refiner, PromptRefiner)
        
    def test_card_compiler(self):
        """Test that CardCompiler correctly compiles card data."""
        compiler = CardCompiler()
        
        # Test data
        word_data = {
            "word": "Hund",
            "language": "German",
            "word_type": "noun",
            "gender": "masculine",
            "article": "der",
            "plural_form": "Hunde",
            "plural_article": "die"
        }
        
        definition = "Ein Hund ist ein domestiziertes Säugetier aus der Familie der Canidae."
        
        sentence = "Der große Hund spielt im Park."
        
        grammar_check = {
            "is_correct": True,
            "explanation": ""
        }
        
        # Test without media files
        card_data = compiler.compile_card(word_data, definition, sentence, grammar_check)
        
        self.assertIn("front_html", card_data)
        self.assertIn("back_html", card_data)
        self.assertIn("tags", card_data)
        self.assertIn("media_files", card_data)
        
        # Check that word and article are in the front HTML
        self.assertIn("der Hund", card_data["front_html"])
        
        # Check that definition and sentence are in the back HTML
        self.assertIn(definition, card_data["back_html"])
        self.assertIn(sentence, card_data["back_html"])
        
        # Check that appropriate tags are included
        self.assertIn("noun", card_data["tags"])
        self.assertIn("german", card_data["tags"])
        self.assertIn("anki-forge", card_data["tags"])

if __name__ == '__main__':
    unittest.main()
