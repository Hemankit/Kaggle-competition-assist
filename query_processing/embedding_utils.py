"""
Embedding utilities using SentenceTransformer for query understanding.
Encodes user queries into vector space for similarity and intent classification.
"""

from sentence_transformers import SentenceTransformer

# Load the model globally so it doesn’t reload every time
sent_transform_model = SentenceTransformer('all-MiniLM-L6-v2')


def query_embeddings(query: str | list[str]) -> list:
    """
    Generate sentence embeddings from a string or list of strings.

    Args:
        query (str or list of str): The query or list of queries.

    Returns:
        list: Sentence embeddings as NumPy arrays.
    """
    if isinstance(query, str):
        return sent_transform_model.encode([query])
    elif isinstance(query, list):
        return sent_transform_model.encode(query)
    else:
        raise TypeError("Input must be a string or list of strings.")


# Optional standalone test
if __name__ == "__main__":
    sample = "How do I improve my model score?"
    emb = query_embeddings(sample)
    print(f"Embedding shape: {emb[0].shape}")