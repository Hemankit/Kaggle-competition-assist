"""
Classifies the user's query intent using sentence embeddings with an LLM fallback.
"""

# Removed unused import
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Tuple
# from langchain_community.chat_models import ChatGoogleGenerativeAI  # Temporarily disabled due to version conflicts
from dotenv import load_dotenv
load_dotenv()
import os
class IntentClassifier:
    def __init__(self, threshold: float = 0.65):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        # self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)  # Temporarily disabled
        self.llm = None
        self.threshold = threshold

        # Intent categories with representative phrases
        self.intent_map: Dict[str, List[str]] = {
            "onboarding": [
                "just joined this competition", "first time", "beginner", "getting started"
            ],
            "progress": [
                "started exploring", "here is my code", "i tried", "my current approach"
            ],
            "confusion": [
                "not sure", "don’t understand", "explain this code", "need help"
            ]
        }

        # Precompute phrase embeddings per intent
        self.intent_embeddings = {
            intent: self.model.encode(phrases, convert_to_tensor=True)
            for intent, phrases in self.intent_map.items()
        }

    def classify_with_embeddings(self, cleaned_query: str) -> Tuple[str, float]:
        input_embedding = self.model.encode(cleaned_query, convert_to_tensor=True)

        best_intent = None
        best_score = -1

        for intent, phrase_embeds in self.intent_embeddings.items():
            score = util.pytorch_cos_sim(input_embedding, phrase_embeds).max().item()
            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent, best_score

    def classify_with_llm(self, cleaned_query: str) -> str:
        prompt = f"""
You're an assistant classifying a user's intent based on their query.

Categories:
- onboarding: user is new to Kaggle or the competition
- progress: user is describing what they've tried or built
- confusion: user is stuck or asking for help

Classify this query:
"{cleaned_query}"

Only respond with: onboarding, progress, or confusion.
"""

        response = self.llm.invoke(prompt).content.strip().lower()
        return response if response in self.intent_map else "other"

    def classify_intent(self, cleaned_query: str) -> Tuple[str, str]:
        intent, score = self.classify_with_embeddings(cleaned_query)

        if score >= self.threshold:
            return intent, "embedding"
        else:
            llm_intent = self.classify_with_llm(cleaned_query)
            return llm_intent, "llm"


# Optional test
if __name__ == "__main__":
    classifier = IntentClassifier()
    test_queries = [
        "Hi, I'm new to this competition and don't know where to start.",
        "Here's my latest submission. I'm trying XGBoost and getting 0.78.",
        "What does this error mean in the evaluation script?"
    ]

    for query in test_queries:
        intent, method = classifier.classify_intent(query)
        print(f"\nQuery: {query}")
        print(f"→ Intent: {intent} (via {method})")