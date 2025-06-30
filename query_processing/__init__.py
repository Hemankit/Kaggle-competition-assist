"""
NLP package for query understanding in the Kaggle Expert Assist project.
Provides preprocessing, embedding, intent classification, section prediction,
and structured query processing for downstream agents and orchestrators.
"""

from .preprocessing import preprocess_query, detect_code, detect_url, detect_numbers
from .embedding_utils import query_embeddings
from .section_classifier import predict_query_section
from .intent_classifier import classify_intent
from .user_input_processor import UserInputProcessor

__all__ = [
    "preprocess_query",
    "query_embeddings",
    "predict_query_section",
    "classify_intent",
    "UserInputProcessor",
]