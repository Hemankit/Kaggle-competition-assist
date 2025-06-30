"""
Orchestrates preprocessing, section classification, and intent classification
into a single user input pipeline.
"""

from datetime import datetime
import re
from typing import Dict

from query_processing.intent_classifier import Preprocessor
from query_processing.intent_classifier import SectionClassifier
from query_processing.intent_classifier import IntentClassifier


class UserInputProcessor:
    def __init__(self):
        self.session_state = {}  # To store user or competition session info
        self.preprocessor = Preprocessor()
        self.section_classifier = SectionClassifier()
        self.intent_classifier = IntentClassifier()

    def structure_query(self, query: str) -> Dict:
        """
        Process the user query, classify it by section and intent,
        and extract relevant metadata.
        """
        cleaned_info = self.preprocessor.preprocess_query(
            query, remove_stopwords=False, spellcheck=False
        )

        cleaned_query = cleaned_info["cleaned_query"]
        tokens = cleaned_info["tokens"]

        # Intent and section classification
        section, section_method = self.section_classifier.predict_section(cleaned_query)
        intent, intent_method = self.intent_classifier.classify_intent(cleaned_query)

        # Additional metadata
        contains_code = bool(re.search(r'```|import |def |class |=', query))
        contains_url = bool(re.search(r"http[s]?://", query))
        contains_number = any(char.isdigit() for char in query)
        contains_question = "?" in query

        structured = {
            "original_query": query,
            "cleaned_query": cleaned_query,
            "tokens": tokens,
            "section": section,
            "intent": intent,
            "metadata": {
                "contains_code": contains_code,
                "contains_url": contains_url,
                "contains_number": contains_number,
                "contains_question": contains_question,
                "section_method": section_method,
                "intent_method": intent_method,
            },
            "timestamp": datetime.now().isoformat()
        }

        return structured


# Optional test
if __name__ == "__main__":
    processor = UserInputProcessor()

    test_query = "Here's my XGBoost baseline. How can I improve this?"
    structured = processor.structure_query(test_query)

    print("\nStructured Output:")
    for key, val in structured.items():
        print(f"{key}: {val}")