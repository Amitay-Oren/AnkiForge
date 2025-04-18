import openai
from config.config import OPENAI_API_KEY

class GrammarChecker:
    """
    Agent responsible for checking the grammar of user-provided sentences
    using GPT-4 and providing corrections and explanations if needed.
    """
    
    def __init__(self):
        """Initialize the GrammarChecker agent with OpenAI API key."""
        openai.api_key = OPENAI_API_KEY
        
    def check_grammar(self, sentence, language, word):
        """
        Check the grammar of a user-provided sentence.
        
        Args:
            sentence (str): The sentence to check
            language (str): The target language (e.g., "German")
            word (str): The target word that should be used in the sentence
            
        Returns:
            dict: A dictionary containing:
                - is_correct (bool): Whether the sentence is grammatically correct
                - corrected_sentence (str): Corrected version if there are errors
                - explanation (str): Explanation of errors and corrections
        """
        prompt = f"""
        As a {language} language expert, check the grammar of this sentence that uses the word "{word}":
        
        Sentence: {sentence}
        
        Important guidelines:
        1. Verify if the sentence is grammatically correct in {language}
        2. Check if the word "{word}" is used correctly
        3. If there are errors, provide a corrected version
        4. Explain any corrections in simple {language}
        5. If the sentence is correct, simply confirm it's correct
        
        Format your response as a JSON object with these fields:
        - is_correct: true/false
        - corrected_sentence: (only if is_correct is false)
        - explanation: (explanation in {language})
        """
        
        # Call OpenAI API to check grammar
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f"You are a {language} language teacher checking grammar for language learners."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            # Parse the JSON response
            import json
            grammar_check = json.loads(result)
            
            # Ensure all required fields are present
            if "is_correct" not in grammar_check:
                grammar_check["is_correct"] = False
            if not grammar_check["is_correct"] and "corrected_sentence" not in grammar_check:
                grammar_check["corrected_sentence"] = sentence
            if "explanation" not in grammar_check:
                grammar_check["explanation"] = "No explanation provided."
                
            return grammar_check
            
        except Exception as e:
            return {
                "is_correct": False,
                "corrected_sentence": sentence,
                "explanation": f"Error checking grammar: {str(e)}"
            }
