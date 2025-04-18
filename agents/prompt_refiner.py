import openai
from config.config import OPENAI_API_KEY

class PromptRefiner:
    """
    Agent responsible for converting user sentences into image prompts
    suitable for image generation using GPT-4.
    """
    
    def __init__(self):
        """Initialize the PromptRefiner agent with OpenAI API key."""
        openai.api_key = OPENAI_API_KEY
        
    def refine_prompt(self, sentence, language, target_language="English"):
        """
        Convert a user sentence into an image generation prompt.
        
        Args:
            sentence (str): The user's sentence to convert
            language (str): The source language of the sentence
            target_language (str): The target language for the prompt (default: English)
            
        Returns:
            str: A refined prompt suitable for image generation
        """
        # For German sentences, we'll try to keep the prompt in German first
        if language == language:
            prompt = f"""
            As an expert in creating image generation prompts, convert this {language} sentence into a detailed, 
            visual scene description in {language} that would work well for AI image generation:
            
            Sentence: {sentence}
            
            Important guidelines:
            1. Keep the prompt in {language}
            2. Create a vivid, detailed visual description based on the sentence
            3. Add visual details like colors, lighting, style, and mood
            4. Keep the core meaning of the original sentence
            5. Format as a comma-separated list of descriptive elements
            6. Length should be 1-3 sentences maximum
            7. Do not include any explanations, just the prompt itself
            """
        
        # Call OpenAI API to refine prompt
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at creating detailed, visual prompts for AI image generation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            refined_prompt = response.choices[0].message.content.strip()
            
            # If the target language is different from the source language and we need to translate
            if language != target_language:
                translation_prompt = f"""
                Translate this image generation prompt from {language} to {target_language} while preserving all visual details:
                
                {refined_prompt}
                
                Important: Only provide the translated prompt, no explanations.
                """
                
                translation_response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an expert {language} to {target_language} translator."},
                        {"role": "user", "content": translation_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=200
                )
                
                refined_prompt = translation_response.choices[0].message.content.strip()
            
            return refined_prompt
            
        except Exception as e:
            return f"Error refining prompt: {str(e)}"
