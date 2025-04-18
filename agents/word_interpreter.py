import openai
from config.config import OPENAI_API_KEY

class WordInterpreter:
    """
    Agent responsible for generating native-language definitions for words
    using GPT-4 without translating to the user's native language.
    """
    
    def __init__(self):
        """Initialize the WordInterpreter agent with OpenAI API key."""
        openai.api_key = OPENAI_API_KEY
        
    def generate_definition(self, word, language, word_type, gender=None, plural_form=None):
        """
        Generate a native-language definition for the given word.
        
        Args:
            word (str): The word to define
            language (str): The target language (e.g., "German")
            word_type (str): Type of word (noun, verb, etc.)
            gender (str, optional): Gender for nouns (masculine, feminine, neuter)
            plural_form (str, optional): Plural form for nouns
            
        Returns:
            str: Native-language definition of the word
        """
        # Construct the prompt based on word type and language
        if word_type == "noun" and gender and plural_form:
            if language == "German":
                article = self._get_german_article(gender)
                prompt = f"""
                As a German language expert, provide a clear and simple definition IN GERMAN for the noun:
                
                Word: {article} {word}
                Plural: die {plural_form}
                
                Important guidelines:
                1. The definition must be IN GERMAN only, not in English or any other language
                2. Use simple German that a language learner could understand
                3. Include 1-2 common usage examples
                4. Keep the definition concise (3-5 sentences maximum)
                5. Do not include any translations
                """
        else:
            prompt = f"""
            As a {language} language expert, provide a clear and simple definition IN {language.upper()} for the {word_type}:
            
            Word: {word}
            
            Important guidelines:
            1. The definition must be IN {language.upper()} only, not in English or any other language
            2. Use simple {language} that a language learner could understand
            3. Include 1-2 common usage examples
            4. Keep the definition concise (3-5 sentences maximum)
            5. Do not include any translations
            """
        
        # Call OpenAI API to generate definition
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f"You are a {language} language teacher providing simple definitions for language learners."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating definition: {str(e)}"
    
    def _get_german_article(self, gender):
        """Get the appropriate German article based on gender."""
        articles = {
            "masculine": "der",
            "feminine": "die",
            "neuter": "das"
        }
        return articles.get(gender, "")

    def check_noun_plurality(self, noun, language):
        """
        Uses a lightweight LLM to determine if a noun typically has a plural form.
        
        Args:
            noun (str): The noun to check.
            language (str): The language of the noun.
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the check was successful.
                - has_plural (bool | None): True if plural exists, False if not, None on error.
                - reason (str | None): Explanation from the LLM or error message.
        """
        # --- Placeholder for actual OpenAI API call --- 
        # This function needs to be implemented using the OpenAI API.
        # 1. Ensure OPENAI_API_KEY is set in config/config.py or environment.
        # 2. Use a lightweight model (e.g., gpt-3.5-turbo or newer cost-effective model).
        # 3. Construct a prompt asking if the given noun in the specified language typically 
        #    has a plural form, requesting a simple YES/NO answer and a brief reason.
        # 4. Parse the response to determine True/False for 'has_plural'.
        # 5. Handle potential API errors gracefully.
        
        # Example Prompt Structure:
        # prompt = f"Does the {language} noun '{noun}' typically have a plural form? Answer only YES or NO, followed by a brief explanation." 
        
        # Example API call structure (requires 'openai' library):
        # try:
        #     client = openai.OpenAI(api_key=OPENAI_API_KEY) # Use client if > OpenAI v1.0
        #     response = client.chat.completions.create(
        #         model="gpt-3.5-turbo", # Choose a lightweight model
        #         messages=[
        #             {"role": "system", "content": "You are a helpful linguistic assistant."},
        #             {"role": "user", "content": prompt}
        #         ],
        #         temperature=0.2,
        #         max_tokens=50
        #     )
        #     content = response.choices[0].message.content.strip().upper()
        #     
        #     # Basic parsing (needs refinement)
        #     has_plural = content.startswith("YES")
        #     reason = response.choices[0].message.content.strip() # Get the full reason
        #     
        #     return {"success": True, "has_plural": has_plural, "reason": reason}
        #     
        # except Exception as e:
        #     return {"success": False, "has_plural": None, "reason": f"API Error: {str(e)}"}
        
        # --- End Placeholder --- 
        
        # Return a default error state until implemented
        return {
            "success": False, 
            "has_plural": None, 
            "reason": "AI Plurality Check not implemented yet."
        }
