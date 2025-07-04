import re
import unicodedata
import logging
from typing import List, Dict, Any

# Assuming logger is configured elsewhere and imported, e.g., from config.logging_config
# from config.logging_config import logger
# For standalone testing, a basic logger can be set up:
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class TextProcessor:
    """
    A class for robust text cleaning, normalization, and feature engineering,
    inspired by the data processing principles in the Whisper paper (txt/articles.txt)
    and quality directives from txt/quality.txt.
    """

    def __init__(self):
        logger.info("Initializing TextProcessor.")
        # Precompile regex for efficiency
        self._html_tag_pattern = re.compile(r'<.*?>')
        self._bracket_pattern = re.compile(r'\[.*?\]|\(.*?\)') # Matches [] and ()
        self._punctuation_pattern = re.compile(r'[^\w\s\.\%\$]') # Keep alphanumeric, space, ., %, $
        self._numeric_expression_pattern = re.compile(r'(\d+)\s*(million|billion|trillion)?\s*(dollars|euros|pounds)?')
        self._contraction_map = self._load_contraction_map()

    def _load_contraction_map(self) -> Dict[str, str]:
        """
        Loads a simple map for common English contractions.
        This can be expanded for more comprehensive coverage.
        """
        return {
            "ain't": "am not", "aren't": "are not", "can't": "cannot", "can't've": "cannot have",
            "could've": "could have", "couldn't": "could not", "didn't": "did not", "doesn't": "does not",
            "don't": "do not", "hadn't": "had not", "hasn't": "has not", "haven't": "have not",
            "he'd": "he would", "he'll": "he will", "he's": "he is", "how'd": "how did",
            "how'll": "how will", "how's": "how is", "i'd": "I would", "i'll": "I will",
            "i'm": "I am", "i've": "I have", "isn't": "is not", "it'd": "it would",
            "it'll": "it will", "it's": "it is", "let's": "let us", "ma'am": "madam",
            "mightn't": "might not", "must've": "must have", "mustn't": "must not",
            "needn't": "need not", "she'd": "she would", "she'll": "she will", "she's": "she is",
            "should've": "should have", "shouldn't": "should not", "that's": "that is",
            "there'd": "there would", "there'll": "there will", "there's": "there is",
            "they'd": "they would", "they'll": "they will", "they're": "they are",
            "they've": "they have", "we'd": "we would", "we'll": "we will", "we're": "we are",
            "we've": "we have", "weren't": "were not", "what'll": "what will", "what're": "what are",
            "what's": "what is", "what've": "what have", "when's": "when is", "where'd": "where did",
            "where's": "where is", "who'll": "who will", "who's": "who is", "who've": "who have",
            "why's": "why is", "won't": "will not", "would've": "would have", "wouldn't": "would not",
            "you'd": "you would", "you'll": "you will", "you're": "you are", "you've": "you have"
        }

    def _remove_html_tags(self, text: str) -> str:
        """Removes HTML tags from the text."""
        return self._html_tag_pattern.sub('', text)

    def _remove_phrases_in_brackets(self, text: str) -> str:
        """Removes phrases enclosed in brackets or parentheses."""
        return self._bracket_pattern.sub('', text)

    def _remove_filler_words(self, text: str) -> str:
        """Removes common filler words."""
        filler_words = r'\b(hmm|mm|mhm|mmm|uh|um)\b'
        return re.sub(filler_words, '', text, flags=re.IGNORECASE)

    def _expand_contractions(self, text: str) -> str:
        """Expands common English contractions."""
        for contraction, expansion in self._contraction_map.items():
            text = re.sub(r'\b' + re.escape(contraction) + r'\b', expansion, text, flags=re.IGNORECASE)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Replaces multiple spaces with a single space and strips leading/trailing whitespace."""
        return re.sub(r'\s+', ' ', text).strip()

    def _remove_non_alphanumeric_except_currency(self, text: str) -> str:
        """
        Removes non-alphanumeric characters, but keeps '.', '%', and '$' for numeric expressions.
        This is a simplified version of the Whisper paper's approach to punctuation.
        """
        return self._punctuation_pattern.sub('', text)

    def _standardize_numeric_expressions(self, text: str) -> str:
        """
        Standardizes numerical and monetary expressions (e.g., "Ten thousand dollars" to "$10000").
        This is a simplified example and can be made more robust.
        """
        def replace_match(match):
            num = int(match.group(1))
            multiplier = 1
            if match.group(2):
                if match.group(2).lower() == 'million':
                    multiplier = 1_000_000
                elif match.group(2).lower() == 'billion':
                    multiplier = 1_000_000_000
                elif match.group(2).lower() == 'trillion':
                    multiplier = 1_000_000_000_000
            value = num * multiplier
            currency_symbol = '$' # Default to dollar for simplicity
            if match.group(3):
                if match.group(3).lower() == 'euros':
                    currency_symbol = '€'
                elif match.group(3).lower() == 'pounds':
                    currency_symbol = '£'
            return f"{currency_symbol}{value}"

        return self._numeric_expression_pattern.sub(replace_match, text)

    def _remove_whitespace_before_apostrophe(self, text: str) -> str:
        """Removes whitespace characters that come before an apostrophe.\n        e.g., "don 't" -> "don't""" 
        return re.sub(r'\s+\'', '\'', text)

    def _normalize_unicode(self, text: str) -> str:
        """Normalizes unicode characters to their canonical decomposition form."""
        return unicodedata.normalize('NFKC', text)

    def process_text(self, text: str, language: str = 'en') -> str:
        """
        Applies a series of cleaning and normalization steps to the input text.
        Adheres to 'Say What You Do, Do What You Say' by formalizing the process.
        """
        if not isinstance(text, str):
            logger.warning(f"Input is not a string: {type(text)}. Attempting to convert.")
            text = str(text)

        original_text = text
        logger.info(f"Processing text (language: {language}): '{original_text[:100]}...'") # Log first 100 chars

        # Step 1: Remove HTML tags
        text = self._remove_html_tags(text)
        logger.debug(f"After HTML removal: {text[:100]}...")

        # Step 2: Remove phrases in brackets/parentheses
        text = self._remove_phrases_in_brackets(text)
        logger.debug(f"After bracket removal: {text[:100]}...")

        # Step 3: Remove common filler words
        text = self._remove_filler_words(text)
        logger.debug(f"After filler word removal: {text[:100]}...")

        # Step 4: Remove whitespace before apostrophe (e.g., "don 't" -> "don't")
        text = self._remove_whitespace_before_apostrophe(text)
        logger.debug(f"After apostrophe whitespace removal: {text[:100]}...")

        # Step 5: Expand contractions (English-specific)
        if language.lower() == 'en':
            text = self._expand_contractions(text)
            logger.debug(f"After contraction expansion: {text[:100]}...")

        # Step 6: Standardize numeric expressions (English-specific example)
        if language.lower() == 'en':
            text = self._standardize_numeric_expressions(text)
            logger.debug(f"After numeric standardization: {text[:100]}...")

        # Step 7: Remove non-alphanumeric characters (keeping some for currency/percentage)
        text = self._remove_non_alphanumeric_except_currency(text)
        logger.debug(f"After non-alphanumeric removal: {text[:100]}...")

        # Step 8: Normalize Unicode characters
        text = self._normalize_unicode(text)
        logger.debug(f"After Unicode normalization: {text[:100]}...")

        # Step 9: Normalize whitespace and strip
        text = self._normalize_whitespace(text)
        logger.debug(f"Final text: {text[:100]}...")

        logger.info(f"Text processing complete. Original length: {len(original_text)}, Processed length: {len(text)}")
        return text

    def extract_features(self, text: str) -> Dict[str, Any]:
        """
        Extracts conceptual features from processed text.
        This is a placeholder for more advanced feature engineering (e.g., token counts,
        sentiment, named entity recognition, topic modeling, etc.).
        """
        logger.info(f"Extracting features from text: '{text[:100]}...' ")
        features = {
            "char_count": len(text),
            "word_count": len(text.split()),
            "is_empty": not bool(text.strip()),
            # Add more sophisticated features here based on requirements
            # e.g., "avg_word_length": sum(len(word) for word in text.split()) / len(text.split())
        }
        logger.info(f"Features extracted: {features}")
        return features

# Example Usage (for testing purposes)
if __name__ == "__main__":
    processor = TextProcessor()

    sample_texts = [
        "Hello, world! This is a test. (Please ignore this part) [and this too].",
        "It's a beautiful day, isn't it? I can't believe it! <html>tags</html>",
        "  This text has   extra spaces and a filler word like umm.  ",
        "The company earned 10 million dollars last year. They're doing great!",
        "This is a sentence with a number 1,000,000 and a percentage 50%.",
        "A sentence with a weird unicode character: \u00e9cole.", # école
        "What's up, doc? I'm going to the store.",
        "This is a test with no special characters.",
        "", # Empty string
        "   " # Whitespace only
    ]

    for i, text in enumerate(sample_texts):
        print(f"\n--- Sample {i+1} ---")
        print(f"Original: '{text}'")
        processed_text = processor.process_text(text)
        print(f"Processed: '{processed_text}'")
        features = processor.extract_features(processed_text)
        print(f"Features: {features}")

    # Example with a non-English text (will apply general cleaning)
    print("\n--- Non-English Sample ---")
    non_en_text = "Ceci est un texte en français. (Ignorer) [aussi]."
    processed_non_en = processor.process_text(non_en_text, language='fr')
    print(f"Original (FR): '{non_en_text}'")
    print(f"Processed (FR): '{processed_non_en}'")
    print(f"Features (FR): {processor.extract_features(processed_non_en)}")
