"""
Text preprocessing utilities for Kaggle Expert Assist system.

This module provides functions for cleaning, tokenizing, lemmatizing, and analyzing
text queries with proper error handling and input validation.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Union
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)

# Try to import NLTK with proper error handling
try:
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords
    from nltk.data import find
    NLTK_AVAILABLE = True
except ImportError as e:
    logger.warning("NLTK not available: %s", e)
    NLTK_AVAILABLE = False
    word_tokenize = None
    WordNetLemmatizer = None
    stopwords = None
    find = None

# Compile regex patterns once for better performance
CODE_PATTERN = re.compile(r'```|import |def |class |\=', re.IGNORECASE)
URL_PATTERN = re.compile(r'http[s]?://', re.IGNORECASE)
CLEAN_PATTERN = re.compile(r'[^\w\s]', re.UNICODE)

# Default stopwords set
DEFAULT_STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above',
    'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once'
}


def _validate_string_input(text: str, param_name: str) -> None:
    """Validate that input is a non-empty string."""
    if not isinstance(text, str):
        raise TypeError(f"{param_name} must be a string, got {type(text).__name__}")
    if not text.strip():
        raise ValueError(f"{param_name} cannot be empty")


def _validate_set_input(stopwords_set: Optional[Set[str]], param_name: str) -> None:
    """Validate that stopwords_set is a set when provided."""
    if stopwords_set is not None and not isinstance(stopwords_set, set):
        raise TypeError(f"{param_name} must be a set when provided, got {type(stopwords_set).__name__}")


def _ensure_nltk_data() -> bool:
    """Ensure required NLTK data is available."""
    if not NLTK_AVAILABLE:
        return False
    
    try:
        # Check if required NLTK data is available
        find('tokenizers/punkt')
        find('corpora/wordnet')
        return True
    except LookupError:
        logger.warning("Required NLTK data not found. Please run: nltk.download('punkt') and nltk.download('wordnet')")
        return False


@lru_cache(maxsize=128)
def _get_lemmatizer() -> Optional[WordNetLemmatizer]:
    """Get cached lemmatizer instance."""
    if not NLTK_AVAILABLE or not _ensure_nltk_data():
        return None
    
    try:
        return WordNetLemmatizer()
    except Exception as e:
        logger.error("Failed to initialize lemmatizer: %s", e)
        return None


def preprocess_query(
    query: str, 
    remove_stopwords: bool = False, 
    stopwords_set: Optional[Set[str]] = None, 
    spellcheck: bool = False
) -> Dict[str, Union[str, List[str], int, bool]]:
    """
    Preprocess a text query by cleaning, tokenizing, and optionally lemmatizing.
    
    Args:
        query: Input text to preprocess
        remove_stopwords: Whether to remove stopwords
        stopwords_set: Custom set of stopwords to remove (defaults to built-in set)
        spellcheck: Whether to perform spell checking (currently unused)
        
    Returns:
        Dictionary containing:
        - original: Original input text
        - cleaned: Cleaned text
        - tokens: List of processed tokens
        - token_count: Number of tokens
        - has_code: Whether text contains code
        - has_url: Whether text contains URLs
        - has_numbers: Whether text contains numbers
        - is_question: Whether text is a question
        
    Raises:
        TypeError: If query is not a string
        ValueError: If query is empty
        RuntimeError: If NLTK is not available and required
    """
    # Validate inputs
    _validate_string_input(query, "query")
    _validate_set_input(stopwords_set, "stopwords_set")
    
    # Initialize result dictionary
    result = {
        "original": query,
        "cleaned": "",
        "tokens": [],
        "token_count": 0,
        "has_code": False,
        "has_url": False,
        "has_numbers": False,
        "is_question": False
    }
    
    try:
        # Clean the text
        cleaned = CLEAN_PATTERN.sub('', query.lower().strip())
        result["cleaned"] = cleaned
        
        # Check if text is empty after cleaning
        if not cleaned:
            logger.warning("Text became empty after cleaning")
            return result
        
        # Tokenize
        if NLTK_AVAILABLE and _ensure_nltk_data():
            try:
                tokens = word_tokenize(cleaned)
            except Exception as e:
                logger.error("Tokenization failed: %s", e)
                # Fallback to simple whitespace splitting
                tokens = cleaned.split()
        else:
            # Fallback to simple whitespace splitting
            tokens = cleaned.split()
        
        # Lemmatize if NLTK is available
        if NLTK_AVAILABLE and _ensure_nltk_data():
            lemmatizer = _get_lemmatizer()
            if lemmatizer:
                try:
                    tokens = [lemmatizer.lemmatize(token) for token in tokens if token.strip()]
                except Exception as e:
                    logger.error("Lemmatization failed: %s", e)
                    # Continue with original tokens
            else:
                tokens = [token for token in tokens if token.strip()]
        else:
            tokens = [token for token in tokens if token.strip()]
        
        # Remove stopwords if requested
        if remove_stopwords:
            if stopwords_set is None:
                stopwords_set = DEFAULT_STOPWORDS
            try:
                tokens = [token for token in tokens if token.lower() not in stopwords_set]
            except Exception as e:
                logger.error("Stopword removal failed: %s", e)
                # Continue with original tokens
        
        result["tokens"] = tokens
        result["token_count"] = len(tokens)
        
        # Analyze text features
        result["has_code"] = detect_code(query)
        result["has_url"] = detect_url(query)
        result["has_numbers"] = detect_numbers(query)
        result["is_question"] = detect_question(query)
        
    except Exception as e:
        logger.error("Error in preprocess_query: %s", e)
        # Return partial result
        result["tokens"] = []
        result["token_count"] = 0
    
    return result


def detect_code(text: str) -> bool:
    """
    Detect if text contains code patterns.
    
    Args:
        text: Input text to analyze
        
    Returns:
        True if code patterns are detected, False otherwise
        
    Raises:
        TypeError: If text is not a string
    """
    _validate_string_input(text, "text")
    
    try:
        return bool(CODE_PATTERN.search(text))
    except Exception as e:
        logger.error("Error in detect_code: %s", e)
        return False


def detect_url(text: str) -> bool:
    """
    Detect if text contains URLs.
    
    Args:
        text: Input text to analyze
        
    Returns:
        True if URLs are detected, False otherwise
        
    Raises:
        TypeError: If text is not a string
    """
    _validate_string_input(text, "text")
    
    try:
        return bool(URL_PATTERN.search(text))
    except Exception as e:
        logger.error("Error in detect_url: %s", e)
        return False


def detect_numbers(text: str) -> bool:
    """
    Detect if text contains numbers.
    
    Args:
        text: Input text to analyze
        
    Returns:
        True if numbers are detected, False otherwise
        
    Raises:
        TypeError: If text is not a string
    """
    _validate_string_input(text, "text")
    
    try:
        return any(char.isdigit() for char in text)
    except Exception as e:
        logger.error("Error in detect_numbers: %s", e)
        return False


def detect_question(text: str) -> bool:
    """
    Detect if text is a question.
    
    Args:
        text: Input text to analyze
        
    Returns:
        True if text appears to be a question, False otherwise
        
    Raises:
        TypeError: If text is not a string
    """
    _validate_string_input(text, "text")
    
    try:
        # More sophisticated question detection
        text_lower = text.lower().strip()
        
        # Check for question mark
        if '?' in text:
            return True
        
        # Check for question words at the beginning
        question_words = ['what', 'where', 'when', 'why', 'how', 'who', 'which', 'whose']
        words = text_lower.split()
        if words and words[0] in question_words:
            return True
        
        # Check for question patterns
        question_patterns = [
            r'^can you',
            r'^could you',
            r'^would you',
            r'^should i',
            r'^do you',
            r'^are you',
            r'^is there',
            r'^are there'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    except Exception as e:
        logger.error("Error in detect_question: %s", e)
        return False


def get_available_stopwords() -> Set[str]:
    """
    Get available stopwords from NLTK or return default set.
    
    Returns:
        Set of stopwords
    """
    if NLTK_AVAILABLE and _ensure_nltk_data():
        try:
            return set(stopwords.words('english'))
        except Exception as e:
            logger.error("Failed to load NLTK stopwords: %s", e)
    
    return DEFAULT_STOPWORDS


def validate_preprocessing_result(result: Dict[str, Union[str, List[str], int, bool]]) -> bool:
    """
    Validate that preprocessing result has expected structure.
    
    Args:
        result: Preprocessing result to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = {
        "original", "cleaned", "tokens", "token_count", 
        "has_code", "has_url", "has_numbers", "is_question"
    }
    
    if not isinstance(result, dict):
        return False
    
    return all(key in result for key in required_keys)


if __name__ == "__main__":
    # Test the preprocessing functions
    try:
        sample_query = "Hello! How are you? Can you help me with this code: ```python print('hello')```"
        
        print("Testing preprocessing functions...")
        print(f"Sample query: {sample_query}")
        
        # Test basic preprocessing
        result = preprocess_query(sample_query)
        print(f"Preprocessing result: {result}")
        
        # Test validation
        is_valid = validate_preprocessing_result(result)
        print(f"Result validation: {is_valid}")
        
        # Test individual detection functions
        print(f"Has code: {detect_code(sample_query)}")
        print(f"Has URL: {detect_url(sample_query)}")
        print(f"Has numbers: {detect_numbers(sample_query)}")
        print(f"Is question: {detect_question(sample_query)}")
        
        # Test with stopwords removal
        result_with_stopwords = preprocess_query(sample_query, remove_stopwords=True)
        print(f"With stopwords removed: {result_with_stopwords}")
        
        print("All tests completed successfully!")
        
    except Exception as e:
        logger.error("Test failed: %s", e)
        print(f"Test failed: {e}")