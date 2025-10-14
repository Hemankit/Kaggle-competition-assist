from .base_agent import BaseAgent
from typing import Optional, Dict, Any
import re

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


error_diagnosis_prompt = """
You are an expert Python error diagnostician for Kaggle competitions. Analyze the error message and code context to provide a clear diagnosis and actionable fix.

Error/Exception:
----------------
{error_message}

Code Context:
----------------
{code_context}

Competition Context:
----------------
{competition_context}

Provide:
1. **Error Type**: Identify the specific error (e.g., ValueError, KeyError, TypeError)
2. **Root Cause**: Explain what's causing the error in plain terms
3. **Specific Fix**: Provide exact code changes or debugging steps
4. **Prevention**: Suggest how to avoid this error in the future

Be concise but thorough. Focus on actionable solutions.
"""


class ErrorDiagnosisAgent(BaseAgent):
    """
    General-purpose error diagnosis agent for Python/Kaggle code.
    
    Features:
    - Parses Python tracebacks
    - Identifies error types and root causes
    - Provides specific, actionable fixes
    - Works standalone (without competition context)
    - Searches discussions when competition context provided
    """
    
    def __init__(self, llm=None):
        super().__init__(
            name="ErrorDiagnosisAgent",
            description="Diagnoses Python code errors and suggests specific fixes for Kaggle competitions"
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
        
        self.prompt = PromptTemplate.from_template(error_diagnosis_prompt)
        
        if self.llm:
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        else:
            self.chain = None

    def _extract_error_info(self, query: str) -> tuple:
        """
        Extract error message and code from query.
        
        Returns:
            (error_message, code_context) tuple
        """
        # Try to find traceback
        traceback_pattern = r'Traceback.*?(?=\n\n|$)'
        traceback_match = re.search(traceback_pattern, query, re.DOTALL)
        
        error_message = ""
        code_context = ""
        
        if traceback_match:
            error_message = traceback_match.group(0)
            # Try to find code after traceback
            remaining = query[traceback_match.end():]
            code_pattern = r'```python\s*(.*?)\s*```|```\s*(.*?)\s*```'
            code_match = re.search(code_pattern, remaining, re.DOTALL)
            if code_match:
                code_context = code_match.group(1) or code_match.group(2) or ""
        else:
            # No traceback, try to find error message and code separately
            code_pattern = r'```python\s*(.*?)\s*```|```\s*(.*?)\s*```'
            code_matches = re.findall(code_pattern, query, re.DOTALL)
            if code_matches:
                code_context = code_matches[0][0] or code_matches[0][1] or ""
            
            # Look for common error patterns
            error_patterns = [
                r'(ValueError:.*)',
                r'(TypeError:.*)',
                r'(KeyError:.*)',
                r'(IndexError:.*)',
                r'(AttributeError:.*)',
                r'(ImportError:.*)',
                r'(ModuleNotFoundError:.*)',
                r'(FileNotFoundError:.*)',
                r'(SyntaxError:.*)',
                r'(IndentationError:.*)',
            ]
            
            for pattern in error_patterns:
                match = re.search(pattern, query, re.MULTILINE)
                if match:
                    error_message = match.group(1)
                    break
            
            # If still no error message, use the whole query
            if not error_message:
                error_message = query
        
        return error_message.strip(), code_context.strip()

    def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Diagnose error and provide fix.
        
        Args:
            query: Error message/traceback with optional code context
            context: Optional competition context (discussions with solutions)
            
        Returns:
            Dict with agent_name, response, and updated_context
        """
        # Handle empty query
        if not query or not query.strip():
            return {
                "agent_name": self.name,
                "response": "Please provide an error message or traceback you'd like help with.",
                "updated_context": context
            }
        
        # Extract error info
        error_message, code_context = self._extract_error_info(query)
        
        # Prepare competition context string
        competition_context = ""
        if context:
            if 'competition' in context:
                competition_context += f"Competition: {context['competition']}\n"
            if 'discussions' in context:
                competition_context += f"Available discussions: {len(context['discussions'])} related topics\n"
            if 'common_errors' in context:
                competition_context += f"Known issues: {', '.join(context['common_errors'][:3])}\n"
        
        if not competition_context:
            competition_context = "No competition context provided (standalone diagnosis)"
        
        # Generate diagnosis using LLM
        if self.llm and self.chain:
            try:
                response = self.chain.run(
                    error_message=error_message,
                    code_context=code_context if code_context else "No code context provided",
                    competition_context=competition_context
                )
            except Exception as e:
                response = f"Error generating diagnosis: {e}\n\nFalling back to basic analysis..."
                response += "\n\n" + self._basic_error_diagnosis(error_message, code_context)
        else:
            # Fallback if no LLM available
            response = self._basic_error_diagnosis(error_message, code_context)
        
        return {
            "agent_name": self.name,
            "response": response,
            "updated_context": context
        }
    
    def _basic_error_diagnosis(self, error_message: str, code_context: str) -> str:
        """
        Basic error diagnosis without LLM (fallback for testing).
        
        Uses pattern matching to identify common errors.
        """
        diagnosis = "### Error Diagnosis\n\n"
        
        # Identify error type
        if "ValueError" in error_message:
            diagnosis += "**Error Type**: ValueError\n\n"
            
            if "Found array with 0 sample" in error_message or "0 sample(s)" in error_message:
                diagnosis += (
                    "**Root Cause**: Your data is empty (0 samples). This usually happens when:\n"
                    "- Data filtering removed all rows\n"
                    "- Train/test split resulted in empty sets\n"
                    "- DataFrame slicing went wrong\n\n"
                    "**Fix**:\n"
                    "1. Check your filtering conditions (e.g., `df[df['age'] > 100]` might be too restrictive)\n"
                    "2. Verify data is loaded correctly: `print(df.shape)` before splitting\n"
                    "3. Ensure `test_size` is valid (between 0 and 1)\n\n"
                    "**Prevention**: Always check dataframe shape after filtering: `assert len(df) > 0, \"No data left after filtering!\"`"
                )
            elif "invalid literal for int()" in error_message:
                diagnosis += (
                    "**Root Cause**: Trying to convert a non-numeric string to an integer.\n\n"
                    "**Fix**:\n"
                    "1. Check for non-numeric values: `df['column'].unique()`\n"
                    "2. Handle missing/invalid values: `df['column'] = pd.to_numeric(df['column'], errors='coerce')`\n"
                    "3. Or filter them out: `df = df[df['column'].str.isnumeric()]`\n\n"
                    "**Prevention**: Always inspect data types and handle edge cases before conversion."
                )
            else:
                diagnosis += (
                    "**Root Cause**: A value doesn't meet expected constraints.\n\n"
                    "**Fix**: Check the error message for specific value/constraint details and adjust your code accordingly."
                )
        
        elif "KeyError" in error_message:
            diagnosis += "**Error Type**: KeyError\n\n"
            # Extract column name if possible
            key_match = re.search(r"KeyError:\s*['\"]([^'\"]+)['\"]", error_message)
            missing_key = key_match.group(1) if key_match else "column"
            
            diagnosis += (
                f"**Root Cause**: The column/key `{missing_key}` doesn't exist in your DataFrame/dictionary.\n\n"
                "**Fix**:\n"
                f"1. Check column names: `print(df.columns.tolist())`\n"
                f"2. Look for typos or case mismatches (e.g., 'target' vs 'Target')\n"
                f"3. Ensure the column wasn't accidentally dropped\n"
                f"4. Use safe access: `df.get('{missing_key}', default_value)`\n\n"
                "**Prevention**: Always verify column existence before accessing: `assert 'column' in df.columns`"
            )
        
        elif "Shape" in error_message and "mismatch" in error_message.lower():
            diagnosis += "**Error Type**: Shape Mismatch (ValueError)\n\n"
            diagnosis += (
                "**Root Cause**: Array/DataFrame dimensions don't match expected shape.\n\n"
                "**Fix**:\n"
                "1. Check shapes: `print(X.shape, y.shape)`\n"
                "2. Ensure assignment length matches: `len(values) == len(df)`\n"
                "3. Verify all rows/columns are accounted for\n\n"
                "**Prevention**: Always check dimensions before operations:\n"
                "```python\n"
                "assert len(new_col) == len(df), f\"Length mismatch: {len(new_col)} vs {len(df)}\"\n"
                "```"
            )
        
        elif "ModuleNotFoundError" in error_message or "ImportError" in error_message:
            diagnosis += "**Error Type**: Import Error\n\n"
            module_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_message)
            missing_module = module_match.group(1) if module_match else "module"
            
            # Special case for sklearn
            if missing_module == "sklearn":
                install_cmd = "pip install scikit-learn"
            else:
                install_cmd = f"pip install {missing_module}"
            
            diagnosis += (
                f"**Root Cause**: The module `{missing_module}` is not installed.\n\n"
                f"**Fix**: Install the missing module:\n"
                f"```bash\n"
                f"{install_cmd}\n"
                f"```\n\n"
                "**Prevention**: Use requirements.txt to track dependencies."
            )
        
        elif "TypeError" in error_message:
            diagnosis += "**Error Type**: TypeError\n\n"
            if "unsupported operand type" in error_message:
                diagnosis += (
                    "**Root Cause**: Trying to perform an operation between incompatible types (e.g., int + str).\n\n"
                    "**Fix**: Convert types before operation:\n"
                    "```python\n"
                    "result = int(value1) + int(value2)  # Or str(value1) + str(value2)\n"
                    "```\n\n"
                    "**Prevention**: Check data types: `print(type(variable))`"
                )
            else:
                diagnosis += "**Root Cause**: Type incompatibility in your operation.\n\n**Fix**: Check types and convert as needed."
        
        else:
            # Generic diagnosis
            diagnosis += (
                "**Error Type**: Please provide the full error message for specific diagnosis.\n\n"
                "**General Debugging Steps**:\n"
                "1. Read the error message carefully (last line)\n"
                "2. Check the line number in the traceback\n"
                "3. Print variable values before the error: `print(variable)`\n"
                "4. Check data types: `print(type(variable))`\n"
                "5. Verify shapes: `print(array.shape)`\n"
            )
        
        return diagnosis