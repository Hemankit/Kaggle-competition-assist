"""
Guideline Evaluator - Validates responses against Kaggle expert best practices.

Enhances multi-agent responses by:
1. Matching response content against expert guidelines
2. Scoring response quality based on best practice coverage
3. Enriching responses with relevant tips not yet mentioned
"""

from typing import List, Dict, Optional
import json
import re
import os


def load_guidelines(filepath: str = None) -> Dict[str, List[str]]:
    """Load expert guidelines from JSON."""
    if filepath is None:
        # Default to the project's expert guidelines
        filepath = os.path.join(os.path.dirname(__file__), "..", "data", "expert_guidelines.json")
    
    with open(filepath, "r") as f:
        return json.load(f)


def match_keywords(response: str, guidelines: List[str]) -> List[str]:
    """Match guidelines to response content using keyword matching."""
    matched = []
    response_lower = response.lower()
    
    for tip in guidelines:
        # Extract key technical terms and concepts
        tip_keywords = re.findall(r"\b\w+\b", tip.lower())
        # Need at least 2 keyword matches to consider it a match (reduces false positives)
        matches = sum(1 for keyword in tip_keywords if keyword in response_lower and len(keyword) > 3)
        if matches >= 2:
            matched.append(tip)
    
    return matched


def infer_task_from_query(query: str) -> Optional[str]:
    """Infer the most relevant task category from user query."""
    query_lower = query.lower()
    
    # Task detection patterns
    task_patterns = {
        "Understanding the Problem": ["understand", "problem", "competition", "metric", "evaluation"],
        "EDA": ["eda", "explore", "exploratory", "data analysis", "distribution", "visualize"],
        "Data Preprocessing": ["preprocess", "clean", "missing", "nan", "encode", "normalize"],
        "Feature Engineering": ["feature", "engineering", "create", "interaction", "polynomial"],
        "Baseline Modeling": ["baseline", "simple model", "first model", "logistic", "random forest"],
        "Iterative Improvement and Ensembling": ["improve", "optimize", "tune", "ensemble", "stack", "blend", "xgboost"],
        "Leaderboard Management": ["leaderboard", "submission", "score", "cv", "validation"],
        "Time Management": ["time", "deadline", "schedule", "milestone", "plan"],
        "Meta Practices": ["git", "version", "reproduce", "seed", "checkpoint"]
    }
    
    # Score each task
    task_scores = {}
    for task, keywords in task_patterns.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            task_scores[task] = score
    
    # Return highest scoring task
    if task_scores:
        return max(task_scores, key=task_scores.get)
    
    return "Iterative Improvement and Ensembling"  # Default for general queries


def evaluate_response(
    response: str, 
    query: str = "", 
    task: Optional[str] = None, 
    guideline_json_path: Optional[str] = None
) -> Dict:
    """
    Evaluate response against expert guidelines.
    
    Args:
        response: The multi-agent response to evaluate
        query: Original user query (used to infer task if task not provided)
        task: Specific task category to evaluate against
        guideline_json_path: Path to guidelines JSON (uses default if None)
    
    Returns:
        Dict with evaluation metrics and enrichment suggestions
    """
    guidelines = load_guidelines(guideline_json_path)
    
    # Infer task from query if not provided
    if task is None and query:
        task = infer_task_from_query(query)
    elif task is None:
        task = "Iterative Improvement and Ensembling"  # Default
    
    task_tips = guidelines.get(task, {}).get("tips", [])
    
    # Match tips mentioned in response
    matched = match_keywords(response, task_tips)
    
    # Find unmentioned tips (enrichment opportunities)
    unmatched = [tip for tip in task_tips if tip not in matched]
    
    # Calculate quality score
    score = round(len(matched) / len(task_tips), 2) if task_tips else 0.0
    
    return {
        "task": task,
        "score": score,
        "total_guidelines": len(task_tips),
        "matched_count": len(matched),
        "matched_tips": matched,
        "unmatched_tips": unmatched[:3],  # Top 3 suggestions for enrichment
        "quality_level": "high" if score >= 0.7 else "medium" if score >= 0.4 else "basic"
    }


def enrich_response_with_guidelines(response: str, query: str = "") -> str:
    """
    Enrich a response with relevant expert guidelines not yet mentioned.
    
    Args:
        response: Original multi-agent response
        query: User's original query
    
    Returns:
        Enhanced response with expert tips appended
    """
    evaluation = evaluate_response(response, query)
    
    if not evaluation["unmatched_tips"] or evaluation["score"] >= 0.8:
        # Response already comprehensive
        return response
    
    # Add expert tips section
    enrichment = "\n\n---\n\n**💡 Additional Kaggle Expert Tips:**\n"
    for i, tip in enumerate(evaluation["unmatched_tips"], 1):
        enrichment += f"{i}. {tip}\n"
    
    return response + enrichment