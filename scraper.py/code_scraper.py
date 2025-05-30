"""fallback for handling raw code blocks or assist with notebook internals if needed to go deeper"""
import os
import json
from typing import List, Dict, Any, Optional
import re

# For pretty-printing and debugging
import pprint
import logging

class codeparser:
    def __init__(self, metadata_path: str):
        self.metadata_path = metadata_path
        self.metadata = []
        self.cleaned_metadata = []
        self.sorted_metadata = []
        self.filtered_metadata = []
        self.load_metadata()

    def load_metadata(self):
        """Load and process metadata from JSON file."""
        if not os.path.exists(self.metadata_path):
            print(f"[ERROR] Metadata file '{self.metadata_path}' not found.")
            return

        try:
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON: {e}")
            return

        self.cleaned_metadata = self.clean_metadata(self.metadata)
        self.sorted_metadata = self.sort_metadata(self.cleaned_metadata)
        self.filtered_metadata = self.filter_metadata(self.sorted_metadata)

        # Save all versions for debugging or reuse
        self.save_metadata(self.metadata, "original_metadata.json")
        self.save_metadata(self.cleaned_metadata, "cleaned_metadata.json")
        self.save_metadata(self.sorted_metadata, "sorted_metadata.json")
        self.save_metadata(self.filtered_metadata, "filtered_metadata.json")

    def clean_metadata(self, metadata: List[Dict]) -> List[Dict]:
        """Remove extraneous fields and standardize date format."""
        cleaned = []
        for item in metadata:
            try:
                cleaned.append({
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'author': item.get('author', ''),
                    'description': item.get('description', ''),
                    'tags': item.get('tags', []),
                    'url': item.get('url', ''),
                    'is_pinned': item.get('isPinned', False),
                    'votes': item.get('totalVotes', 0),
                    'comments': item.get('totalComments', 0),
                    'date_created': self.format_date(item.get('dateCreated')),
                    'date_modified': self.format_date(item.get('dateModified')),
                })
            except Exception as e:
                print(f"[WARN] Skipping invalid item: {e}")
        return cleaned
    def format_date(self, date_str: Optional[str]) -> Optional[str]:
        """Convert date string to a standardized format."""
        if not date_str:
            return None
        try:
            # Assuming the date is in ISO format
            return datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"[WARN] Invalid date format: {date_str}")
            return None
    
    def sort_metadata(self, metadata: List[Dict], key: str = 'date_created', reverse: bool = True) -> List[Dict]:
        """Sort metadata based on a specified key."""
        try:
            return sorted(metadata, key=lambda x: x.get(key), reverse=reverse)
        except Exception as e:
            print(f"[ERROR] Sorting failed: {e}")
            return metadata
    
    def filter_metadata(self, metadata: List[Dict], keyword: Optional[str] = 'data', tags: Optional[List[str]] = None) -> List[Dict]:
        """Filter metadata based on keyword and tags."""
        filtered = []
        for item in metadata:
            if keyword and keyword.lower() not in item.get('title', '').lower():
                continue
            if tags and not any(tag in item.get('tags', []) for tag in tags):
                continue
            filtered.append(item)
        return filtered
    
    def save_metadata(self, metadata: List[Dict], filename: str):
        """Save metadata to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(metadata, f, indent=4)
        except IOError as e:
            print(f"[ERROR] Failed to save metadata to '{filename}': {e}")

    def pretty_print(self, data: Any):
        """Pretty-print JSON data."""
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
    
    def extract_code_blocks(self, notebook_content: str) -> List[str]:
        """Extract code blocks from notebook content."""
        code_blocks = []
        # Regex to match code blocks
        code_block_pattern = re.compile(r'```(.*?)```', re.DOTALL)
        matches = code_block_pattern.findall(notebook_content)
        for match in matches:
            code_blocks.append(match.strip())
        return code_blocks
    
    def extract_markdown_blocks(self, notebook_content: str) -> List[str]:
        """Extract markdown blocks from notebook content."""
        markdown_blocks = []
        # Regex to match markdown blocks
        markdown_block_pattern = re.compile(r'```markdown(.*?)```', re.DOTALL)
        matches = markdown_block_pattern.findall(notebook_content)
        for match in matches:
            markdown_blocks.append(match.strip())
        return markdown_blocks
    
    def extract_code_and_markdown(self, notebook_content: str) -> Dict[str, List[str]]:
        """Extract both code and markdown blocks from notebook content."""
        return {
            'code_blocks': self.extract_code_blocks(notebook_content),
            'markdown_blocks': self.extract_markdown_blocks(notebook_content)
        }
    
    def extract_code_and_markdown_from_metadata(self) -> List[Dict[str, Any]]:
        """Extract code and markdown blocks from all notebooks in metadata."""
        extracted_data = []
        for item in self.filtered_metadata:
            notebook_content = item.get('description', '')
            extracted = self.extract_code_and_markdown(notebook_content)
            extracted_data.append({
                'id': item.get('id'),
                'title': item.get('title'),
                'code_blocks': extracted['code_blocks'],
                'markdown_blocks': extracted['markdown_blocks']
            })
        return extracted_data
    def save_extracted_data(self, extracted_data: List[Dict[str, Any]], filename: str):
        """Save extracted code and markdown blocks to a JSON file."""
        try:
            with open(filename,
                        'w') as f:
                    json.dump(extracted_data, f, indent=4)
        except IOError as e:
            print(f"[ERROR] Failed to save extracted data to '{filename}': {e}")
        else:
            print(f"[INFO] Extracted data saved to '{filename}'")
    
if __name__ == "__main__":
    metadata_path = "notebook_metadata.json"
    code_parser = codeparser(metadata_path)
    
    # Example usage
    extracted_data = code_parser.extract_code_and_markdown_from_metadata()
    code_parser.save_extracted_data(extracted_data, "extracted_code_and_markdown.json")
    
    # Pretty-print the extracted data
    code_parser.pretty_print(extracted_data)
    # Print the first 5 entries for brevity
    print("\n[EXTRACTED DATA]")
    for entry in extracted_data[:5]:
        print(f"- {entry['title']}: {len(entry['code_blocks'])} code blocks, {len(entry['markdown_blocks'])} markdown blocks")
        