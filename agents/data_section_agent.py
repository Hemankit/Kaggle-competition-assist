"""
Data Section Agent - Analyzes competition data files and structure

Provides information about:
- Available data files (train, test, submission templates)
- File sizes and formats
- Data description from competition page
- Quick insights about data structure

Uses Kaggle API for file metadata, with scraping fallback for descriptions.
"""

from typing import Dict, List, Any
from .base_rag_retrieval_agent import BaseRAGRetrievalAgent


class DataSectionAgent(BaseRAGRetrievalAgent):
    """Agent for analyzing and explaining competition data files."""
    
    def __init__(self, llm=None, retriever=None):
        """Initialize the Data Section Agent."""
        
        # ENHANCED prompt with 3-section breakdown (like CompetitionSummaryAgent evaluation)
        enhanced_data_prompt = """You are a Kaggle competition data expert. Your role is to help competitors understand the data structure and how to work with it effectively.

Competition: {competition}
User Level: {user_level}
Tone: {tone}

Data Information:
{section_content}

Provide a PRACTICAL breakdown covering these 3 key areas:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ DATA STRUCTURE - What's in each file?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each file (train, test, submission template):
- 📁 Filename and purpose
- 📊 Dimensions (rows x columns) if available
- 🎯 Target variable presence (train has it, test doesn't)
- 💡 What to use it for

Example format:
```
📁 train.csv (891 rows, 12 columns)
   - Ground truth included (target column)
   - Use for: Training + Cross-validation
   - Contains: All features + target variable

📁 test.csv (418 rows, 11 columns)  
   - NO ground truth (predict this!)
   - Use for: Final Kaggle submission predictions
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2️⃣ LOADING STRATEGY - How to read and validate the data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide Python code showing:
1. How to load the files correctly
2. How to validate the data (shape checks, column consistency)
3. Quick initial inspection

Example:
```python
import pandas as pd
import numpy as np

# Load data
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

# Quick validation
print(f"Train shape: {{train.shape}}")
print(f"Test shape: {{test.shape}}")

# Check column consistency
train_cols = set(train.columns) - {{'target_column'}}
test_cols = set(test.columns)
assert train_cols == test_cols, "Column mismatch!"

# Target distribution (for classification)
print(train['target'].value_counts(normalize=True))
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3️⃣ ESSENTIAL EDA - What to check first
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Guide competitors through critical initial checks:

✓ Missing Values Analysis
```python
# Check for missing data
missing = train.isnull().sum()
print(missing[missing > 0])
# ⚠️ Highlight columns with >10% missing
```

✓ Feature Types Classification
- **Numerical**: List continuous features (Age, Price, etc.)
- **Categorical**: List discrete features (Sex, Category, etc.)  
- **Identifiers**: Note which columns are IDs (don't use for modeling!)
- **Dates/Text**: Special handling needed

✓ Target Variable Analysis (for supervised learning)
- Distribution (balanced/imbalanced?)
- Data type (binary, multiclass, continuous?)
- Any special characteristics

✓ Quick Correlation Check (for numerical features)
```python
# Which features correlate with target?
correlations = train.corr()['target'].sort_values(ascending=False)
print(correlations.head(10))
```

📌 KEY TAKEAWAY:
Provide 2-3 actionable insights about which features look most promising or what challenges to expect (heavy missing data, class imbalance, etc.)

Response:"""
        
        super().__init__(
            agent_name="DataSectionAgent",
            prompt_template=enhanced_data_prompt,
            section="data",
            llm=llm,
            retriever=retriever
        )
        
        self.enhanced_data_prompt = enhanced_data_prompt
    
    def run(self, structured_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        V2-compatible run method that matches BaseRAGRetrievalAgent interface.
        
        Args:
            structured_query: Dict with 'cleaned_query' and 'metadata'
        
        Returns:
            Dict with agent_name and response
        """
        try:
            # Extract query and metadata
            query = structured_query.get("cleaned_query", "")
            metadata = structured_query.get("metadata", {})
            competition = metadata.get("competition_slug", metadata.get("competition", "Unknown Competition"))
            
            # Fetch data description from ChromaDB
            chunks = self.fetch_sections(structured_query)
            
            # Extract file information and description from chunks
            files_info = self._extract_files_from_content(chunks)
            description = "\n\n".join([chunk.get("content", "") for chunk in chunks])
            
            # Generate summary using the retrieved data
            final_response = self.summarize_sections(chunks, metadata)
            
            return {"agent_name": self.name, "response": final_response}
        
        except Exception as e:
            return {"agent_name": self.name, "response": f"DataSectionAgent failed: {str(e)}"}
    
    def run_legacy(self, competition: str, files: List[Dict[str, Any]], 
            description: str = "", user_query: str = "") -> Dict[str, Any]:
        """
        LEGACY method for backward compatibility (direct Kaggle API usage).
        Use run() for V2 orchestrator compatibility.
        """
        if not files:
            return {
                "competition": competition,
                "files": [],
                "summary": "No data files found for this competition.",
                "status": "no_files"
            }
        
        # Format files for display
        formatted_files = self._format_files(files)
        
        # Generate summary using LLM
        if self.llm:
            summary = self._generate_summary(
                competition=competition,
                files_info=formatted_files,
                description=description or "No description available",
                user_query=user_query or "What data files are available?"
            )
        else:
            # Fallback to simple summary
            summary = self._simple_summary(files, description)
        
        return {
            "competition": competition,
            "files": files,
            "formatted_files": formatted_files,
            "description": description,
            "summary": summary,
            "status": "success"
        }
    
    def _extract_files_from_content(self, chunks: List[Dict[str, Any]]) -> str:
        """Extract file information from retrieved content."""
        # Look for file mentions in content
        file_keywords = ['train.csv', 'test.csv', 'sample_submission', '.csv', 'data file']
        relevant_content = []
        
        for chunk in chunks:
            content = chunk.get("content", "").lower()
            if any(keyword in content for keyword in file_keywords):
                relevant_content.append(chunk.get("content", ""))
        
        return "\n".join(relevant_content[:3])  # Top 3 relevant chunks
    
    def _format_files(self, files: List[Dict[str, Any]]) -> str:
        """Format file list for display."""
        if not files:
            return "No files available"
        
        lines = []
        for f in files:
            name = f.get('name', 'unknown')
            size = self._format_size(f.get('size', 0))
            desc = f.get('description', '')
            
            line = f"- **{name}** ({size})"
            if desc:
                line += f": {desc}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _format_size(self, bytes: int) -> str:
        """Convert bytes to human-readable format."""
        if bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        size = bytes
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _generate_summary(self, competition: str, files_info: str,
                         description: str, user_query: str) -> str:
        """Generate LLM-based summary of data files."""
        try:
            prompt = self.summary_prompt.format(
                competition=competition,
                user_query=user_query,
                files_info=files_info,
                description=description[:1000]  # Limit description length
            )
            
            # Use LLM to generate summary
            response = self.llm.invoke(prompt)
            
            # Extract text from response
            if hasattr(response, 'content'):
                return response.content.strip()
            elif isinstance(response, str):
                return response.strip()
            else:
                return str(response).strip()
        
        except Exception as e:
            print(f"[DataSectionAgent] Error generating summary: {e}")
            return self._simple_summary(files_info, description)
    
    def _simple_summary(self, files: List[Dict[str, Any]], description: str) -> str:
        """Fallback summary without LLM."""
        if not files:
            return "No data files available for this competition."
        
        file_names = [f.get('name', 'unknown') for f in files]
        total_size = sum(f.get('size', 0) for f in files)
        
        summary = f"**Data Files Overview**\n\n"
        summary += f"Found {len(files)} data file(s):\n"
        
        for f in files:
            name = f.get('name', 'unknown')
            size = self._format_size(f.get('size', 0))
            summary += f"- {name} ({size})\n"
        
        summary += f"\nTotal size: {self._format_size(total_size)}\n"
        
        # Add description if available
        if description and len(description) > 20:
            summary += f"\n**Description**:\n{description[:500]}"
            if len(description) > 500:
                summary += "..."
        
        return summary
    
    def analyze_file_types(self, files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize files by type (train, test, submission, etc.)."""
        categories = {
            "train": [],
            "test": [],
            "submission": [],
            "other": []
        }
        
        for f in files:
            name = f.get('name', '').lower()
            
            if 'train' in name:
                categories["train"].append(f.get('name'))
            elif 'test' in name:
                categories["test"].append(f.get('name'))
            elif 'submission' in name or 'sample' in name:
                categories["submission"].append(f.get('name'))
            else:
                categories["other"].append(f.get('name'))
        
        return categories
    
    def get_file_by_name(self, files: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
        """Get specific file metadata by name."""
        for f in files:
            if f.get('name', '').lower() == name.lower():
                return f
        return {}


if __name__ == "__main__":
    # Simple test
    agent = DataSectionAgent()
    
    test_files = [
        {"name": "train.csv", "size": 61194, "description": "Training data"},
        {"name": "test.csv", "size": 28629, "description": "Test data"},
        {"name": "sample_submission.csv", "size": 3258, "description": "Submission template"}
    ]
    
    result = agent.run(
        competition="titanic",
        files=test_files,
        description="Passenger survival data from the Titanic",
        user_query="What data files are available?"
    )
    
    print("=" * 70)
    print("DATA SECTION AGENT TEST")
    print("=" * 70)
    print(result["summary"])
    print("=" * 70)

