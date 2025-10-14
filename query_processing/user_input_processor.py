"""
Orchestrates preprocessing, section classification, and intent classification
into a single user input pipeline.
"""

from datetime import datetime
import re
from typing import Dict



from query_processing.preprocessing import preprocess_query, detect_code, detect_url, detect_numbers, detect_question
from query_processing.embedding_utils import query_embeddings
from query_processing.section_classifier import predict_query_section
# Intent classifier import moved to function level




class UserInputProcessor:
    def __init__(self):
        self.session_state = {}  # To store user or competition session info



    def structure_query(self, query: str) -> Dict:
        """
        Sequentially process the user query: preprocess, embed, classify section, then intent, and extract metadata.
        """
        # Step 1: Preprocessing
        cleaned_info = preprocess_query(query, remove_stopwords=False, spellcheck=False)
        cleaned_query = cleaned_info["cleaned_query"]
        tokens = cleaned_info["tokens"]

        # Step 2: Embedding creation
        embedding = query_embeddings(cleaned_query)

        # Step 3: Section classification
        section_result = predict_query_section(cleaned_query)
        section = section_result["top_section"]
        section_method = "semantic-similarity"

        # Step 4: Intent classification
        from .intent_classifier import IntentClassifier
        classifier = IntentClassifier()
        intent, intent_method = classifier.classify_intent(cleaned_query)

        # Additional metadata using preprocessing helpers
        contains_code = detect_code(query)
        contains_url = detect_url(query)
        contains_number = detect_numbers(query)
        contains_question = detect_question(query)

        structured = {
            "original_query": query,
            "cleaned_query": cleaned_query,
            "tokens": tokens,
            "embedding": embedding,
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