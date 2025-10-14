

from .base_agent import BaseAgent
from typing import Optional, Dict, Any
import re

# CrewAI
from crewai import Agent

# AutoGen
from autogen import ConversableAgent

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Use llm_loader for proper LLM initialization
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from llms.llm_loader import get_llm_from_config
except ImportError:
    get_llm_from_config = None


class CodeFeedbackAgent(BaseAgent):
    """
    General-purpose code review agent for Kaggle competition code.
    
    Features:
    - Detects syntax errors, logic errors, data leakage, inefficiencies
    - Parses code from natural language queries (markdown code blocks)
    - Works standalone (without competition context)
    - Enhanced by competition context (notebooks, discussions, metrics)
    """
    
    def __init__(self, llm=None):
        super().__init__(
            name="CodeFeedbackAgent",
            description=(
                "Provides expert-level feedback on Kaggle competition code, including notebooks and modular scripts. "
                "Identifies bugs, inefficiencies, and code smells. Highlights missing best practices such as reproducibility, "
                "feature leakage checks, modular structure, and experiment tracking. Encourages clarity, scalability, and top-performing practices."
            )
        )
        
        # Use provided LLM or load from config (code_handling section for Groq)
        if llm:
            self.llm = llm
        elif get_llm_from_config:
            try:
                self.llm = get_llm_from_config(section="code_handling")
            except Exception as e:
                print(f"Warning: Could not load LLM from config: {e}")
                self.llm = None
        else:
            self.llm = None
        
        # Prompt template for code review
        self.prompt = PromptTemplate.from_template(
            """You are an expert Kaggle code reviewer. Analyze the following code and provide specific, actionable feedback.

Focus on:
1. **Syntax Errors**: Missing parentheses, brackets, incorrect indentation
2. **Logic Errors**: Invalid parameters, wrong data types, incorrect method usage
3. **Data Leakage**: Using target variable in feature engineering, improper train/test splitting
4. **Inefficiencies**: Loops instead of vectorization, redundant operations
5. **Best Practices**: Reproducibility (random seeds), modular code, error handling

User Query:
{query}

Code Provided:
{code}

Competition Context (if available):
{context}

Provide:
- Clear identification of issues (if any)
- Specific line references when possible
- Actionable suggestions for improvement
- Positive feedback for well-written code

Be concise but thorough. Prioritize the most impactful issues first.
"""
        )
        
        if self.llm:
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        else:
            self.chain = None

    def _extract_code_from_query(self, query: str) -> str:
        """
        Extract Python code from markdown code blocks or raw code in query.
        
        Args:
            query: User query potentially containing code
            
        Returns:
            Extracted code string (or empty if no code found)
        """
        # Try to find markdown code blocks (```python ... ``` or ``` ... ```)
        patterns = [
            r'```python\s*(.*?)\s*```',  # ```python ... ```
            r'```\s*(.*?)\s*```',         # ``` ... ```
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query, re.DOTALL)
            if matches:
                return matches[0].strip()
        
        # If no markdown blocks, check if query looks like code (heuristic)
        # Has imports, indentation, or function definitions
        if any(keyword in query for keyword in ['import ', 'def ', 'class ', 'if __name__']):
            return query.strip()
        
        return ""

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze code and provide feedback.
        
        Args:
            query: User query with code to review
            context: Optional competition context (notebooks, metrics, etc.)
            
        Returns:
            Dict with agent_name, response, and updated_context
        """
        # Handle empty query
        if not query or not query.strip():
            return {
                "agent_name": self.name,
                "response": "Please provide some code to review. You can paste it directly or use markdown code blocks (```python ... ```).",
                "updated_context": context
            }
        
        # Extract code from query
        code = self._extract_code_from_query(query)
        
        # Handle no code found
        if not code:
            return {
                "agent_name": self.name,
                "response": (
                    "I didn't find any code in your query. Could you please provide the code you'd like me to review? "
                    "You can paste it in a markdown code block like this:\n\n"
                    "```python\n"
                    "# Your code here\n"
                    "```"
                ),
                "updated_context": context
            }
        
        # Prepare context string
        context_str = ""
        if context:
            if 'competition' in context:
                context_str += f"Competition: {context['competition']}\n"
            if 'metric' in context:
                context_str += f"Metric: {context['metric']}\n"
            if 'notebooks' in context:
                context_str += f"Available notebooks: {len(context['notebooks'])} top solutions\n"
        
        if not context_str:
            context_str = "No competition context provided (standalone review)"
        
        # Generate feedback using LLM
        if self.llm and self.chain:
            try:
                response = self.chain.run(
                    query=query,
                    code=code,
                    context=context_str
                )
            except Exception as e:
                response = f"Error generating feedback: {e}\n\nCode received:\n{code[:500]}..."
        else:
            # Fallback if no LLM available
            response = self._basic_code_analysis(code, query)
        
        return {
            "agent_name": self.name,
            "response": response,
            "updated_context": context
        }
    
    def _basic_code_analysis(self, code: str, query: str) -> str:
        """
        Basic code analysis without LLM (fallback for testing).
        
        Detects common issues using simple pattern matching.
        """
        issues = []
        
        # Check for syntax errors (basic detection)
        if code.count('(') != code.count(')'):
            issues.append("⚠️ **Syntax Error**: Mismatched parentheses detected.")
        
        if code.count('[') != code.count(']'):
            issues.append("⚠️ **Syntax Error**: Mismatched brackets detected.")
        
        # Check for data leakage patterns
        if 'target' in code and any(word in code for word in ['.mean()', '.sum()', '.max()', '.min()']):
            if 'train_test_split' not in code or code.index('train_test_split') > code.index('.mean()'):
                issues.append(
                    "⚠️ **Data Leakage**: Using target variable to create features before splitting. "
                    "This can cause overfitting and inflated validation scores."
                )
        
        # Check for inefficient loops
        if 'for i in range(len(' in code:
            issues.append(
                "💡 **Efficiency**: Consider using vectorized operations instead of loops. "
                "Pandas/NumPy operations are much faster. Try using `.apply()` or direct column operations."
            )
        
        # Check for test_size issues
        if 'test_size=' in code:
            # Extract test_size value
            match = re.search(r'test_size\s*=\s*([\d.]+)', code)
            if match:
                test_size = float(match.group(1))
                if test_size > 1:
                    issues.append(
                        f"⚠️ **Logic Error**: `test_size={test_size}` is invalid. "
                        f"It should be between 0 and 1 (e.g., 0.2 for 20% test split)."
                    )
        
        # Check for best practices
        if 'random_state' not in code and 'RandomForest' in code:
            issues.append(
                "💡 **Reproducibility**: Consider adding `random_state` parameter for reproducible results."
            )
        
        # Compile response
        if issues:
            response = "### Code Review Feedback\n\n"
            response += "\n\n".join(issues)
            response += "\n\n**Next Steps**: Address these issues to improve your code quality and competition performance."
        else:
            response = (
                "### Code Review Feedback\n\n"
                "✅ **Overall**: Your code looks solid! No major issues detected.\n\n"
                "**Suggestions for Excellence**:\n"
                "- Ensure reproducibility with random seeds\n"
                "- Add error handling for edge cases\n"
                "- Consider modularizing code into reusable functions\n"
                "- Track experiments and results systematically"
            )
        
        return response

    def to_crewai(self) -> Agent:
        return Agent(
            role="Code Reviewer",
            goal="Review code from Kaggle notebooks or models and provide suggestions for improvement.",
            backstory=self.description,
            allow_delegation=False,
            verbose=True,
            tools=[],
        )

    def to_autogen(self, llm_config: Optional[Dict[str, Any]] = None) -> ConversableAgent:
        config = llm_config or {"config_list": [{"model": "gpt-4", "temperature": 0.2}]}
        system_message = (
            "You are an expert Kaggle code reviewer. You provide high-quality, constructive feedback on user code "
            "submitted for machine learning competitions. You are especially skilled at spotting:\n"
            "- Code that is not modular (e.g., all logic in notebooks instead of reusable scripts)\n"
            "- Missing or weak cross-validation strategies\n"
            "- Data leakage issues (e.g., using target info in features or validation folds)\n"
            "- Lack of reproducibility (e.g., missing seeds, no config tracking)\n"
            "- Inefficient or non-scalable code (e.g., repeated feature generation)\n"
            "- Missing experiment tracking (e.g., no logging of metrics or version control)\n"
            "- Poor code hygiene (e.g., no docstrings, hardcoded paths, no type hints)\n"
            "- Incomplete or unclear comments/markdown in notebooks\n\n"
            "When giving feedback:\n"
            "- Be constructive and concise\n"
            "- Highlight strengths if any\n"
            "- Suggest next steps clearly\n"
            "- Avoid overwhelming the user; prioritize the most impactful issues first\n\n"
            "Assume the user is trying to improve their code quality to reach the top 5% in a Kaggle competition."
        )
        return ConversableAgent(
            name=self.name,
            llm_config=config,
            system_message=system_message,
            human_input_mode="NEVER",
        )
