
"""Scraper for model section of Kaggle competition page.
Cleans and exposes model metadata for agent-driven filtering, sorting, and tagging.
Supports filtering by framework, variation, and score.
Also decides to scrape if it lacks a description or usage guide showing how to use the model.
"""

import json
import os
import hashlib
from typing import List, Dict, Optional, Callable, Any

class ScrapingModelSectionData:
    def __init__(self, model_metadata_path: str):
        self.model_metadata_path = model_metadata_path
        self.metadata = []
        self.cleaned_metadata = []
        self.load_metadata()
    
    def load_metadata(self):
        """Load and clean model metadata from JSON file."""
        if not os.path.exists(self.model_metadata_path):
            print(f"[ERROR] Model metadata file '{self.model_metadata_path}' not found.")
            return

        try:
            with open(self.model_metadata_path, 'r') as f:
                self.metadata = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON: {e}")
            return

        self.cleaned_metadata = self.clean_metadata(self.metadata)

        
    
    def clean_metadata(self, metadata: List[Dict]) -> List[Dict]:
        """Remove extraneous fields, standardize, and tag models."""
        cleaned = []
        for item in metadata:
            try:
                cleaned_item = {
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'author': item.get('author', ''),
                    'description': item.get('description', ''),
                    'tags': item.get('tags', []),
                    'url': item.get('url', ''),
                    'score': item.get('score', 0),
                    'framework': item.get('framework', ''),
                    'variation': item.get('variation', ''),
                }
                cleaned_item = self.tag_model(cleaned_item)
                cleaned.append(cleaned_item)
            except Exception as e:
                print(f"[WARN] Skipping invalid item: {e}")
        return cleaned
    
    def tag_model(self, model: Dict) -> Dict:
        """Add a content hash for deduplication."""
        content = f"{model.get('title','')}{model.get('author','')}{model.get('framework','')}{model.get('variation','')}"
        model['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
        return model
    
    def get_all_cleaned_models(self) -> List[Dict]:
        """Return all cleaned models."""
        return self.cleaned_metadata
    
    def filter_metadata(
        self,
        metadata: List[Dict],
        framework: Optional[str] = None,
        variation: Optional[str] = None,
        min_score: Optional[float] = None,
        require_usage_example: Optional[bool] = None,
        custom_filter_fn: Optional[Callable[[Dict], bool]] = None
    ) -> List[Dict]:
        """
        Filter models based on framework, variation, score, usage example, or a custom function.
        """
        filtered = []
        for item in metadata:
            if framework and item.get('framework', '').lower() != framework.lower():
                continue
            if variation and item.get('variation', '').lower() != variation.lower():
                continue
            if min_score is not None and item.get('score', 0) < min_score:
                continue
            if require_usage_example is True and not self.has_usable_description(item.get("description", "")):
                continue
            if require_usage_example is False and self.has_usable_description(item.get("description", "")):
                continue
            if custom_filter_fn and not custom_filter_fn(item):
                continue
            filtered.append(item)
        return filtered
    
    def has_usable_description(self, desc: str) -> bool:
        """Check if the description contains usage-related keywords."""
        if not desc:
            return False
        usage_keywords = ['example', 'usage', 'run this', 'how to', 'inference']
        return any(keyword in desc.lower() for keyword in usage_keywords)
    
    def sort_by(
        self,
        models: List[Dict],
        key: str,
        reverse: bool = True
    ) -> List[Dict]:
        """Sort a given list of models by any metadata key."""
        try:
            return sorted(models, key=lambda x: x.get(key, 0), reverse=reverse)
        except Exception as e:
            print(f"[ERROR] Failed to sort by {key}: {e}")
            return models
        
    def save_metadata(self, metadata: List[Dict], filename: str):
        """Save structured metadata to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(metadata, f, indent=4)
            print(f"[INFO] Saved {len(metadata)} entries to {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to save {filename}: {e}")

if __name__ == "__main__":
    # Example usage
    metadata_path = "path_to_your_model_metadata.json"
    model_scraper = ScrapingModelSectionData(metadata_path)

    print("\n[SUMMARY]")
    print(f"Total: {len(model_scraper.metadata)}")
    print(f"Cleaned: {len(model_scraper.cleaned_metadata)}")

    print("\n[Top models by score]")
    for m in model_scraper.sort_by(model_scraper.cleaned_metadata, "score")[:3]:
        print(f"- {m['title']} ({m['score']})")

    print("\n[Models with framework 'pytorch']")
    for m in model_scraper.filter_metadata(model_scraper.cleaned_metadata, framework="pytorch")[:3]:
        print(f"- {m['title']} (Framework: {m['framework']})")

    print("\n[Models with variation 'ensemble']")
    for m in model_scraper.filter_metadata(model_scraper.cleaned_metadata, variation="ensemble")[:3]:
        print(f"- {m['title']} (Variation: {m['variation']})")

    print("\n[Models missing usage guide]")
    missing_usage = model_scraper.filter_metadata(
        model_scraper.cleaned_metadata,
        require_usage_example=False
    )
    for m in missing_usage[:3]:
        print(f"- {m['title']} (No usage guide)")

    
    

        
