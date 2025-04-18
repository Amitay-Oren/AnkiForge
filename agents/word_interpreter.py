import openai
from config.config import OPENAI_API_KEY, GENDER_OPTIONS

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
    
    def _get_german_article(self, gender_article):
        """Get the appropriate German article based on the selected article form (der, die, das)."""
        # Gender here is expected to be 'der', 'die', or 'das'
        # The mapping is trivial, but this keeps the structure if needed later.
        # If generate_definition needs the old terms, we'd map here.
        # For now, just return the input if it's valid.
        if gender_article in ["der", "die", "das"]:
             return gender_article
        return "" # Return empty if invalid input

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
        # Using GPT-4.1 Nano for efficient, low-cost plurality checking
        prompt = f"""
        Does the {language} noun '{noun}' typically have a plural form?
        
        Analyze this carefully and provide a structured response in this exact format:
        ANSWER: [YES or NO]
        REASON: [Brief explanation of your reasoning]
        EXAMPLES: [If it has a plural, provide 1-2 examples of common plural forms]
        
        For words that inherently don't have plurals (like mass nouns, abstract concepts) answer NO.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Using the GPT-4.1 Nano equivalent
                messages=[
                    {"role": "system", "content": "You are a precise linguistic assistant specializing in grammatical analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=150
            )
            result = response.choices[0].message.content.strip()
            
            # Parse the structured response
            answer_line = next((line for line in result.split('\n') if line.strip().startswith('ANSWER:')), '')
            reason_line = next((line for line in result.split('\n') if line.strip().startswith('REASON:')), '')
            examples_line = next((line for line in result.split('\n') if line.strip().startswith('EXAMPLES:')), '')
            
            has_plural = "YES" in answer_line.upper()
            
            # Build a user-friendly reason
            reason = ""
            if reason_line:
                reason = reason_line.split(':', 1)[1].strip()
            if has_plural and examples_line:
                examples = examples_line.split(':', 1)[1].strip()
                reason = f"{reason}\nPossible plural forms: {examples}"
            
            return {
                "success": True, 
                "has_plural": has_plural, 
                "reason": reason
            }
            
        except Exception as e:
            return {
                "success": False,
                "has_plural": None,
                "reason": f"API Error: {str(e)}"
            }
        
    def validate_verb_conjugations(self, verb, conjugations, language):
        """
        Uses a lightweight LLM to validate provided verb conjugations.
        
        Args:
            verb (str): The base verb.
            conjugations (dict): Dictionary mapping pronouns to conjugated forms.
            language (str): The language of the verb.
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the validation was successful.
                - is_correct (bool | None): True if all conjugations are correct.
                - corrections (dict): Dictionary of pronouns to corrected forms.
                - feedback (dict): Dictionary with detailed feedback per conjugation.
                - reason (str | None): Overall explanation or error message.
        """
        # Format the conjugations for the prompt
        conjugation_str = "\n".join([f"{pronoun}: {form}" for pronoun, form in conjugations.items()])
        
        # Define language-specific prompts for better accuracy
        if language == "German":
            prompt = f"""
            You are a German grammar expert. 
            
            Evaluate if these present tense conjugations for the German verb '{verb}' are correct:
            
            {conjugation_str}
            
            Be extremely critical and precise. Consider all German grammar rules including:
            - Strong/weak/mixed verb patterns
            - Stem-changing verbs (e→ie, e→i, a→ä, etc.)
            - Irregular verbs
            - Appropriate endings for each person
            
            Format your response EXACTLY as follows:
            
            OVERALL: [YES if all are correct, NO if any are incorrect]
            EXPLANATION: [Brief explanation of conjugation patterns or errors]
            
            For each conjugation, on a new line:
            - pronoun: [CORRECT or INCORRECT] | [correct form if incorrect]
            
            Example:
            - ich: INCORRECT | gehe
            - du: CORRECT
            """
        else:
            # Generic prompt for other languages
            prompt = f"""
            For the {language} verb '{verb}', evaluate if these conjugations are correct:
            
            {conjugation_str}
            
            Format your response EXACTLY as follows:
            
            OVERALL: [YES if all are correct, NO if any are incorrect]
            EXPLANATION: [Brief explanation of any patterns/rules]
            
            For each conjugation, on a new line:
            - pronoun: [CORRECT or INCORRECT] | [correct form if incorrect]
            """
        
        try:
            # Make API call with a lower temperature for more reliable accuracy
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Using the GPT-4.1 Nano equivalent
                messages=[
                    {"role": "system", "content": "You are a precise linguistic assistant specializing in verb conjugations. Be extremely strict and accurate in your evaluations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=350  # Allow for longer, more detailed responses
            )
            result = response.choices[0].message.content.strip()
            
            # Parse structured response with improved robustness
            overall_line = next((line for line in result.split('\n') if line.strip().upper().startswith('OVERALL:')), '')
            explanation_line = next((line for line in result.split('\n') if line.strip().upper().startswith('EXPLANATION:')), '')
            
            # Extract overall correctness
            is_correct = "YES" in overall_line.upper() if overall_line else False
            
            # Extract explanation
            reason = explanation_line.split(':', 1)[1].strip() if explanation_line and ':' in explanation_line else "No explanation provided"
            
            # Parse detailed feedback with improved reliability
            corrections = {}
            feedback = {}
            
            # Extract each pronoun line and parse it
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('-') and ':' in line:
                    # Extract the pronoun part
                    parts = line[1:].strip().split(':', 1)
                    if len(parts) < 2:
                        continue
                    
                    pronoun = parts[0].strip()
                    feedback_text = parts[1].strip()
                    
                    # Check if marked as correct/incorrect
                    is_pronoun_correct = "CORRECT" in feedback_text.upper() and not "INCORRECT" in feedback_text.upper()
                    
                    # Store basic feedback
                    feedback[pronoun] = {
                        "is_correct": is_pronoun_correct,
                        "message": feedback_text.split('|')[0].strip()  # Just the correct/incorrect part
                    }
                    
                    # If marked incorrect, extract the correction
                    if not is_pronoun_correct and '|' in feedback_text:
                        correction = feedback_text.split('|', 1)[1].strip()
                        corrections[pronoun] = correction
            
            # Validate that we have feedback for each pronoun
            for pronoun in conjugations.keys():
                if pronoun not in feedback:
                    # If a pronoun was missed, mark it as needing verification
                    feedback[pronoun] = {
                        "is_correct": False,  # Assume incorrect if not explicitly verified
                        "message": "Verification incomplete"
                    }
            
            return {
                "success": True,
                "is_correct": is_correct and len(corrections) == 0,  # Double-check overall correctness
                "corrections": corrections,
                "feedback": feedback,
                "reason": reason
            }
            
        except Exception as e:
            return {
                "success": False,
                "is_correct": None,
                "corrections": {},
                "feedback": {},
                "reason": f"API Error: {str(e)}"
            }

    # Renamed from validate_plural_form
    def get_plural_info(self, noun, language, reason_language="English"):
        """
        Uses a lightweight LLM to determine the plural status, form, and article for a noun.
        The reason provided will be in the specified reason_language.

        Args:
            noun (str): The singular noun (or potentially already plural noun).
            language (str): The language of the noun.
            reason_language (str): The language requested for the explanation (default: English).

        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the analysis call succeeded.
                - status ('HAS_PLURAL' | 'NO_PLURAL' | 'ALREADY_PLURAL' | None): The determined plural status.
                - plural_form (str | None): The most common plural form, if status is HAS_PLURAL.
                - plural_article (str | None): The definite article for the plural form (e.g., 'die' in German), if status is HAS_PLURAL.
                - reason (str | None): Explanation in the requested reason_language or error message.
        """
        # Language-specific instruction for articles if needed
        article_instruction = ""
        if language == "German":
             article_instruction = "If status is HAS_PLURAL, also provide the correct definite article (usually 'die')."
        # Add instructions for other languages with plural articles here if necessary

        prompt = f"""
        You are a {language} language expert specializing in noun morphology.
        
        Analyze the {language} noun: '{noun}'
        
        Determine its plural status based on common usage:
        1. Does it typically form a plural? (HAS_PLURAL)
        2. Is it a word that usually has no plural form (like mass nouns, some abstract nouns)? (NO_PLURAL)
        3. Is the provided word '{noun}' itself likely already plural or uncountable? (ALREADY_PLURAL)
        
        Respond ONLY with the following structured format, choosing ONE status:
        
        STATUS: [HAS_PLURAL or NO_PLURAL or ALREADY_PLURAL]
        PLURAL_FORM: [If STATUS is HAS_PLURAL, provide the most common plural form. Otherwise, leave blank.]
        PLURAL_ARTICLE: [If STATUS is HAS_PLURAL, provide the definite article for the plural in {language}. {article_instruction} Otherwise, leave blank.]
        REASON: [Provide a brief explanation for your determination IN {reason_language.upper()}.]
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini", # Efficient model for focused tasks
                messages=[
                    {"role": "system", "content": f"You are a precise linguistic assistant specializing in {language} noun plurals and articles. You provide explanations in {reason_language}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # Low temperature for deterministic analysis
                max_tokens=200 # Increased slightly for potentially longer translated reasons
            )
            result = response.choices[0].message.content.strip()
            
            # Parse the structured response
            status = None
            plural_form = None
            plural_article = None
            reason = f"Could not parse AI response in {reason_language}."
            
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("STATUS:"):
                    status_text = line.split(':', 1)[1].strip().upper()
                    if status_text in ["HAS_PLURAL", "NO_PLURAL", "ALREADY_PLURAL"]:
                         status = status_text
                elif line.startswith("PLURAL_FORM:"):
                    form = line.split(':', 1)[1].strip()
                    if form:
                         plural_form = form
                elif line.startswith("PLURAL_ARTICLE:"):
                    article = line.split(':', 1)[1].strip()
                    if article:
                        plural_article = article
                elif line.startswith("REASON:"):
                    reason = line.split(':', 1)[1].strip()
            
            if status is None:
                 # Failed to parse the core part of the response
                 raise ValueError(f"Could not parse STATUS field from AI response.")

            # Ensure form and article are None if status is not HAS_PLURAL
            if status != "HAS_PLURAL":
                plural_form = None
                plural_article = None
                
            return {
                "success": True,
                "status": status,
                "plural_form": plural_form,
                "plural_article": plural_article,
                "reason": reason
            }

        except Exception as e:
            return {
                "success": False,
                "status": None,
                "plural_form": None,
                "plural_article": None,
                "reason": f"API Error during plural analysis: {str(e)}"
            }

    def validate_user_plural(self, noun, user_plural, language):
        """
        Validates a user's plural attempt against AI analysis and provides feedback.

        Args:
            noun (str): The singular noun.
            user_plural (str): The plural form entered by the user.
            language (str): The language of the noun (used as reason_language).

        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the validation process completed.
                - user_correct (bool | None): True if user's input matches AI's analysis.
                - ai_status (str | None): Plural status determined by AI (HAS_PLURAL, etc.).
                - ai_plural_form (str | None): Correct plural form suggested by AI.
                - ai_plural_article (str | None): Plural article suggested by AI.
                - ai_reason (str | None): AI's explanation in the target language.
        """
        # Get AI's analysis, requesting reason in the target language
        ai_info = self.get_plural_info(noun, language, reason_language=language)
        
        if not ai_info or not ai_info["success"]:
            return {
                "success": False,
                "user_correct": None,
                "ai_status": None,
                "ai_plural_form": None,
                "ai_plural_article": None,
                "ai_reason": ai_info.get("reason", "Failed to get AI analysis.")
            }

        ai_status = ai_info["status"]
        ai_plural_form = ai_info["plural_form"]
        ai_plural_article = ai_info["plural_article"]
        ai_reason = ai_info["reason"]
        user_correct = False

        # Compare user input with AI analysis
        if ai_status == "HAS_PLURAL":
            # Case-insensitive comparison
            if ai_plural_form and user_plural.strip().lower() == ai_plural_form.strip().lower():
                user_correct = True
            else:
                user_correct = False
        elif ai_status == "NO_PLURAL" or ai_status == "ALREADY_PLURAL":
            # If AI says no plural/already plural, user is correct ONLY if they left the input blank.
            if not user_plural.strip(): # Check if user input is empty
                user_correct = True # Correct behavior for no/already plural
            else:
                user_correct = False # Incorrect if user entered something
        else:
            # Unknown AI status
             user_correct = None # Cannot determine correctness
             
        return {
            "success": True,
            "user_correct": user_correct,
            "ai_status": ai_status,
            "ai_plural_form": ai_plural_form,
            "ai_plural_article": ai_plural_article,
            "ai_reason": ai_reason
        }

    def validate_word_type_gender(self, word, language, user_word_type, user_gender=None):
        """
        Uses a lightweight LLM to validate the user's selected word type and gender.
        Specifically handles German plural-only nouns and uses article terms (der, die, das).

        Args:
            word (str): The word entered by the user.
            language (str): The target language.
            user_word_type (str): The word type selected by the user.
            user_gender (str, optional): The gender article selected by the user (der, die, das).

        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the validation call succeeded.
                - is_type_correct (bool | None): True if the user's type seems correct.
                - is_gender_correct (bool | None): True if the user's gender seems correct.
                - ai_word_type (str | None): The word type suggested by the AI.
                - ai_gender (str | None): The gender article (der, die, das) suggested by the AI.
                - is_plural_only (bool): True if AI determined the noun is plural-only.
                - reason (str | None): Explanation in English or error message.
        """
        
        # Use the German gender articles from config
        german_genders_allowed = GENDER_OPTIONS.get("German", []) # ["der", "die", "das"]
        
        gender_instruction = ""
        user_gender_info = "Not applicable"
        if language == "German":
            # Strict instructions for German gender output
            gender_instruction = f"If it\'s a noun, what is its definite article? Respond with ONLY one of: {', '.join(german_genders_allowed)}. If the noun is plural-only (like \'Leute\') or has no gender, respond with it's article (Die, Das,der) for gender."
            if user_gender:
                 user_gender_info = user_gender
            else:
                 user_gender_info = "Not selected by user"
        elif language in GENDER_OPTIONS: # Handle other languages if needed later
            # ... (logic for other languages would go here)
            pass 

        # Specific German prompt additions
        german_plural_only_check = ""
        if language == "German":
             german_plural_only_check = "5. Is this German noun typically only used in the plural form (pluralia tantum, e.g., \'Leute\', \'Ferien\')? Answer YES or NO."

        # New prompt assigned to the variable
        prompt = f"""
You are a professional linguist specializing in {language} grammar and vocabulary.

Your task is to analyze a single word input by a language learner. The learner also selects a proposed word type and gender.

Analyze the word: '{word}'

The learner has provided:
- Claimed Word Type: {user_word_type}
- Claimed Gender: {user_gender_info} {'(equivalent to der/die/das)' if language == 'German' else ''}

Your job is to:
1. Determine the most likely **primary grammatical word type** for this word in {language}
2. For **German only**, determine the correct **grammatical gender article**. Your answer MUST be **exactly one of the following**: `'der'`, `'die'`, `'das'`
    - Do NOT use 'plural', 'maskulin', 'feminin', 'neutral', or any other variation.
3. Identify if the word is a **plural-only noun with no singular form** (e.g., "Leute"). This is only relevant in German.
4. Assess whether the learner's provided Word Type is correct
5. Assess whether the learner's provided Gender is correct (only for nouns with a singular form)

---

🔐 VERY IMPORTANT CONSTRAINTS:
- For **AI_GENDER(Article)**, only respond with **'der'**, **'die'**, or **'das'** — nothing else. No explanations, no alternatives.
- If the word is a **plural-only noun** (e.g., 'Leute', 'Ferien'), set **AI_GENDER** to **'die'** and **IS_PLURAL_ONLY** to **YES**.
- Your reasoning must be **short**, in **German**, and grounded in grammar rules or common usage.

---

Respond ONLY in the following structured format:
AI_TYPE: [Your inferred word type: noun, verb, adjective, etc.]
AI_GENDER: [One of: der / die / das]
IS_PLURAL_ONLY: [YES / NO]
TYPE_CORRECT: [YES / NO]
GENDER_CORRECT: [YES / NO]
REASON: [Kurzbegründung auf Deutsch – z.B. "Das Wort ist ein Pluralnomen, daher ist der Artikel 'die'."]
"""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": f"You are a precise linguistic assistant evaluating word type and gender classifications in {language}. For German gender, you MUST respond with 'der', 'die', 'das'. Follow the response format strictly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, 
                max_tokens=250
            )
            result = response.choices[0].message.content.strip()
            
            # Parse the structured response
            ai_type = None
            ai_gender = None
            is_plural_only = False 
            type_correct = None
            gender_correct = None
            reason = "Could not parse AI response."
            
            lines = result.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("AI_TYPE:"):
                    ai_type = line.split(':', 1)[1].strip()
                elif line.startswith("AI_GENDER:"):
                    raw_gender = line.split(':', 1)[1].strip()
                    if raw_gender.upper() == "N/A":
                        ai_gender = None
                    # For German, strictly validate against allowed articles
                    elif language == "German" and raw_gender in german_genders_allowed:
                        ai_gender = raw_gender
                    elif language == "German": # Invalid German gender/article provided by AI
                         ai_gender = None 
                         print(f"Warning: AI returned invalid German gender article '{raw_gender}' for word '{word}'. Expected 'der', 'die', 'das'. Discarding.")
                    # Add logic here if supporting gender validation for other languages
                    # else: ai_gender = raw_gender 
                elif line.startswith("IS_PLURAL_ONLY:"):
                    # Only relevant for German
                    if language == "German":
                         is_plural_only = "YES" in line.upper()
                elif line.startswith("TYPE_CORRECT:"):
                    type_correct = "YES" in line.upper()
                elif line.startswith("GENDER_CORRECT:"):
                    gc_val = line.split(':', 1)[1].strip().upper()
                    if gc_val == "YES": gender_correct = True
                    elif gc_val == "NO": gender_correct = False
                    else: gender_correct = None # Treat NA or anything else as None
                elif line.startswith("REASON:"):
                    reason = line.split(':', 1)[1].strip()
            
            # If it's plural only (German), determine correctness based on user input 'die'
            if language == "German" and is_plural_only:
                # ai_gender = None # Keep commented out: Let the AI's suggestion ('die') pass through
                # Instead of NA, check if user correctly chose 'die' for the plural-only noun
                gender_correct = (user_gender == "die")

            # Basic validation of parsing - check essential fields
            if ai_type is None or type_correct is None:
                 raise ValueError(f"Could not parse critical fields (AI_TYPE, TYPE_CORRECT) from AI response.")
            # Gender correctness check depends on context
            # Check only if gender *should* have been validated (i.e., language==German and not plural_only)
            if language == "German" and not is_plural_only and gender_correct is None:
                 # If AI suggested a gender or user provided one, we expect YES/NO
                 if ai_gender is not None or user_gender is not None:
                      raise ValueError(f"Could not parse GENDER_CORRECT field when German gender analysis was expected.")
                 
            return {
                "success": True,
                "is_type_correct": type_correct,
                "is_gender_correct": gender_correct,
                "ai_word_type": ai_type,
                "ai_gender": ai_gender, # Will be 'der', 'die', 'das', or None
                "is_plural_only": is_plural_only, 
                "reason": reason
            }

        except Exception as e:
            return {
                "success": False,
                "is_type_correct": None,
                "is_gender_correct": None,
                "ai_word_type": None,
                "ai_gender": None,
                "is_plural_only": False,
                "reason": f"API Error during type/gender validation: {str(e)}"
            }
