from typing import List, Dict
import json
import re

def load_guidelines(filepath: str) -> Dict[str, List[str]]:
    with open(filepath, "r") as f:
        return json.load(f)

def match_keywords(response: str, guidelines: List[str]) -> List[str]:
    matched = []
    for tip in guidelines:
        # Simple keyword check; can be improved with fuzzy matching
        tip_keywords = re.findall(r"\b\w+\b", tip.lower())
        if any(keyword in response.lower() for keyword in tip_keywords):
            matched.append(tip)
    return matched

def evaluate_response(response: str, task: str, guideline_json_path: str = "data/evaluation/kaggle_expert_tips.json") -> Dict:
    guidelines = load_guidelines(guideline_json_path)
    task_tips = guidelines.get(task, [])
    matched = match_keywords(response, task_tips)

    score = round(len(matched) / len(task_tips), 2) if task_tips else 0.0

    return {
        "task": task,
        "score": score,
        "total_guidelines": len(task_tips),
        "matched_tips": matched,
        "all_tips": task_tips
    }