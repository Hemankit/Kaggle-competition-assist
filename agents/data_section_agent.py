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
        
        # Simple prompt for data summarization
        summary_prompt = """You are a Kaggle competition data expert. 
Analyze the provided data file information and create a clear, concise summary.

Competition: {competition}
User Query: {user_query}

Data Files:
{files_info}

Data Description (from competition page):
{description}

Provide a summary that includes:
1. Overview of available files (train, test, submission templates)
2. Key insights about file sizes and formats
3. Important notes about data structure or missing information
4. Actionable recommendations for data loading/exploration

Keep it concise and practical."""
        
        super().__init__(
            agent_name="DataSectionAgent",
            prompt_template=summary_prompt,
            section="data",
            llm=llm,
            retriever=retriever
        )
        
        self.summary_prompt = summary_prompt
    
    def run(self, competition: str, files: List[Dict[str, Any]], 
            description: str = "", user_query: str = "") -> Dict[str, Any]:
        """
        Analyze competition data files and provide summary.
        
        Args:
            competition: Competition slug
            files: List of file metadata dicts from Kaggle API
            description: Data description text (from scraping or cache)
            user_query: User's original query
        
        Returns:
            Dict with structured response about data files
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

