"""
Classifies user query into one or more Kaggle competition sections using semantic similarity.
Includes fallback logic for ambiguous or multi-topic queries.
"""

from sentence_transformers import SentenceTransformer, util
from typing import List, Tuple, Dict

# Initialize model and section labels
model = SentenceTransformer("all-mpnet-base-v2")

KAGGLE_SECTIONS = [
    "leaderboard",   # Ranks
    "data",          # Dataset details
    "overview",      # Problem statement, evaluation metric, timeline
    "code",          # Public notebooks
    "model",         # Model suggestions (often derived from code)
    "discussion"     # Q&A forum
]

# Precompute embeddings once
SECTION_EMBEDDINGS = model.encode(KAGGLE_SECTIONS, convert_to_tensor=True)


def predict_query_section(query: str, threshold: float = 0.5) -> Dict:
    """
    Predict the most relevant Kaggle section(s) for a given query.

    Args:
        query (str): User's query string.
        threshold (float): Cosine similarity threshold to select multiple sections.

    Returns:
        dict: {
            "top_section": str,
            "top_score": float,
            "ambiguous_sections": List[Tuple[str, float]]
        }
    """
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, SECTION_EMBEDDINGS)[0]

    top_score = similarities.max().item()
    top_index = similarities.argmax().item()
    top_section = KAGGLE_SECTIONS[top_index]

    # Fallback logic: If multiple sections have scores near top_score, flag ambiguity
    ambiguous_sections = [
        (KAGGLE_SECTIONS[i], float(sim))
        for i, sim in enumerate(similarities)
        if float(sim) >= top_score - 0.05  # Top ± small margin
    ]

    return {
        "top_section": top_section,
        "top_score": top_score,
        "ambiguous_sections": ambiguous_sections
    }


# Optional test block
if __name__ == "__main__":
    test_queries = [
        "What is the leaderboard evaluation metric?",
        "How do I preprocess the data and train a model?",
        "Can someone explain the timeline and data release schedule?"
    ]

    for q in test_queries:
        result = predict_query_section(q)
        print(f"\nQuery: {q}")
        print(f"→ Top Section: {result['top_section']} (score={result['top_score']:.3f})")
        if len(result["ambiguous_sections"]) > 1:
            print("→ Ambiguous Sections:")
            for sec, score in result["ambiguous_sections"]:
                print(f"   - {sec}: {score:.3f}")