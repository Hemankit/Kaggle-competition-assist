"""
Text preprocessing utilities for Kaggle Expert Assist.
Handles tokenization, lemmatization, stopword removal, and cleaning.
"""

import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


def preprocess_query(query: str, remove_stopwords: bool = False, stopwords_set: set = None, spellcheck: bool = False) -> dict:
    """
    Lowercase, remove punctuation, tokenize, and lemmatize the input query.

    Args:
        query (str): The user input string.
        remove_stopwords (bool): Whether to remove stopwords.
        stopwords_set (set, optional): Optional custom stopword list.
        spellcheck (bool): Placeholder for future spellcheck support.

    Returns:
        dict: {"cleaned_query": str, "tokens": list}
    """
    cleaned = re.sub(r'[^\w\s]', '', query.lower())
    tokens = word_tokenize(cleaned)
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    if remove_stopwords and stopwords_set:
        tokens = [token for token in tokens if token not in stopwords_set]

    return {"cleaned_query": cleaned, "tokens": tokens}


def detect_code(text: str) -> bool:
    """Detects if a string contains code-related patterns."""
    return bool(re.search(r'```|import |def |class |\=', text))


def detect_url(text: str) -> bool:
    """Detects if a string contains a URL."""
    return bool(re.search(r'http[s]?://', text))


def detect_numbers(text: str) -> bool:
    """Detects if a string contains numeric characters."""
    return any(char.isdigit() for char in text)


def detect_question(text: str) -> bool:
    """Detects if the text is a question (naive)."""
    return '?' in text


# Optional: test the preprocessing when running directly
if __name__ == "__main__":
    sample_query = "What's the best baseline model for this competition?"
    result = preprocess_query(sample_query)
    print(f"Cleaned query: {result['cleaned_query']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Contains code? {detect_code(sample_query)}")
    print(f"Contains URL? {detect_url(sample_query)}")
    print(f"Contains number? {detect_numbers(sample_query)}")