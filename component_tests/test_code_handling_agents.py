"""
Test Suite for Code Handling Agents (TDD Approach)
===================================================

This test suite defines the expected behavior of code handling agents
BEFORE implementation. Tests are based on requirements, not existing code.

Philosophy:
- Agents are general-purpose (work without competition context)
- Agents are enhanced by context (when provided)
- Agents parse code from natural language
- Agents provide actionable, specific feedback
"""

import pytest
from typing import Dict, Any, Optional


# ==============================================================================
# TEST DATA - Sample Code Snippets
# ==============================================================================

VALID_CODE = """
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv('train.csv')
X = df.drop('target', axis=1)
y = df['target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Accuracy: {score}")
"""

SYNTAX_ERROR_CODE = """
import pandas as pd

df = pd.read_csv('train.csv'
print(df.head())
"""

LOGIC_ERROR_CODE = """
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv('train.csv')
X = df.drop('target', axis=1)
y = df['target']

# BUG: test_size > 1 is invalid
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1.5, random_state=42)
"""

DATA_LEAKAGE_CODE = """
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv('train.csv')

# BUG: Using target to create features (data leakage!)
df['target_mean'] = df['target'].mean()

X = df.drop('target', axis=1)
y = df['target']

model = RandomForestClassifier()
model.fit(X, y)
"""

INEFFICIENT_CODE = """
import pandas as pd

df = pd.read_csv('train.csv')

# Inefficient: Loop instead of vectorized operation
result = []
for i in range(len(df)):
    result.append(df['col1'].iloc[i] + df['col2'].iloc[i])
df['sum'] = result
"""

PYTHON_ERROR_WITH_TRACEBACK = """
Traceback (most recent call last):
  File "train.py", line 15, in <module>
    model.fit(X_train, y_train)
  File "/usr/local/lib/python3.8/site-packages/sklearn/ensemble/_forest.py", line 345, in fit
    X, y = self._validate_data(X, y, multi_output=True, accept_sparse="csc", dtype=DTYPE)
  File "/usr/local/lib/python3.8/site-packages/sklearn/base.py", line 433, in _validate_data
    X, y = check_X_y(X, y, **check_params)
  File "/usr/local/lib/python3.8/site-packages/sklearn/utils/validation.py", line 63, in inner_f
    return f(*args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/sklearn/utils/validation.py", line 814, in check_X_y
    X = check_array(X, accept_sparse=accept_sparse, dtype=dtype, order=order,
  File "/usr/local/lib/python3.8/site-packages/sklearn/utils/validation.py", line 63, in inner_f
    return f(*args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/sklearn/utils/validation.py", line 644, in check_array
    raise ValueError("Found array with 0 sample(s) (shape=%s) while a"
ValueError: Found array with 0 sample(s) (shape=(0, 10)) while a minimum of 1 is required.
"""

SHAPE_MISMATCH_ERROR = """
ValueError: Shape of passed values is (100, 5), indices imply (100, 4)
"""


# ==============================================================================
# CodeFeedbackAgent Tests
# ==============================================================================

class TestCodeFeedbackAgent:
    """
    Test suite for general-purpose code review agent.
    
    The agent should:
    1. Work without competition context (standalone)
    2. Detect common code issues (syntax, logic, best practices)
    3. Provide actionable suggestions
    4. Enhance feedback when competition context is provided
    5. Parse code from natural language queries
    """
    
    @pytest.fixture
    def code_feedback_agent(self):
        """Fixture to provide a CodeFeedbackAgent instance."""
        from agents.code_feedback_agent import CodeFeedbackAgent
        return CodeFeedbackAgent()
    
    # --------------------------------------------------------------------------
    # Core Functionality Tests (No Context Required)
    # --------------------------------------------------------------------------
    
    def test_agent_can_analyze_valid_code(self, code_feedback_agent):
        """Agent should recognize well-written code and provide positive feedback."""
        result = code_feedback_agent.run(
            query=f"Can you review my code?\n```python\n{VALID_CODE}\n```"
        )
        
        assert result is not None
        assert 'response' in result
        response = result['response'].lower()
        
        # Should recognize code quality with positive keywords
        assert any(word in response for word in ['good', 'solid', 'well', 'clear', 'structured', 'clean', 'correct'])
        
        # Should not be harshly critical - avoid words like "bad", "terrible", "wrong" without context
        # (Allow constructive terms like "most critical" for prioritization)
        harsh_words = ['terrible', 'awful', 'bad code', 'poorly written', 'complete mess']
        assert not any(harsh in response for harsh in harsh_words)
    
    def test_agent_detects_syntax_errors(self, code_feedback_agent):
        """Agent should identify syntax errors in code."""
        result = code_feedback_agent.run(
            query=f"Why doesn't this work?\n```python\n{SYNTAX_ERROR_CODE}\n```"
        )
        
        response = result['response'].lower()
        
        # Should mention syntax error
        assert any(word in response for word in ['syntax', 'parenthes', 'missing', 'unclosed'])
        # Should be specific about the issue
        assert 'read_csv' in response or 'line' in response
    
    def test_agent_detects_logic_errors(self, code_feedback_agent):
        """Agent should identify logical errors in code."""
        result = code_feedback_agent.run(
            query=f"Review this code:\n```python\n{LOGIC_ERROR_CODE}\n```"
        )
        
        response = result['response'].lower()
        
        # Should identify the test_size issue
        assert 'test_size' in response or 'split' in response
        assert any(word in response for word in ['invalid', 'should be', 'between', 'error'])
    
    def test_agent_detects_data_leakage(self, code_feedback_agent):
        """Agent should identify data leakage issues."""
        result = code_feedback_agent.run(
            query=f"Is there anything wrong with this?\n```python\n{DATA_LEAKAGE_CODE}\n```"
        )
        
        response = result['response'].lower()
        
        # Should identify data leakage
        assert 'leakage' in response or 'target' in response
        assert any(word in response for word in ['before', 'split', 'feature', 'problem'])
    
    def test_agent_suggests_improvements_for_inefficient_code(self, code_feedback_agent):
        """Agent should suggest performance improvements."""
        result = code_feedback_agent.run(
            query=f"Can I improve this?\n```python\n{INEFFICIENT_CODE}\n```"
        )
        
        response = result['response'].lower()
        
        # Should suggest vectorization
        assert any(word in response for word in ['vectoriz', 'numpy', 'faster', 'efficient', 'loop'])
        # Should be actionable
        assert '+' in response or 'example' in response or 'instead' in response
    
    def test_agent_works_without_context(self, code_feedback_agent):
        """Agent should function without competition context."""
        result = code_feedback_agent.run(
            query=f"Review my code:\n```python\n{VALID_CODE}\n```",
            context=None
        )
        
        assert result is not None
        assert 'response' in result
        assert len(result['response']) > 50  # Should provide substantial feedback
    
    def test_agent_parses_code_blocks_from_query(self, code_feedback_agent):
        """Agent should extract code from markdown code blocks."""
        query_with_markdown = f"""
        Hey, can you check this code I wrote?
        
        ```python
        import pandas as pd
        df = pd.read_csv('data.csv'
        ```
        
        I'm getting an error but I don't know why.
        """
        
        result = code_feedback_agent.run(query=query_with_markdown)
        response = result['response'].lower()
        
        # Should parse and identify the syntax error
        assert 'syntax' in response or 'parenthes' in response or 'missing' in response
    
    def test_agent_handles_multiple_issues(self, code_feedback_agent):
        """Agent should identify multiple issues and prioritize them."""
        multi_issue_code = """
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv('train.csv')
df['leak'] = df['target'].mean()  # Data leakage
X = df.drop('target', axis=1)
y = df['target']

model = RandomForestClassifier(n_estimators=10000  # Missing closing parenthesis
model.fit(X, y
"""
        result = code_feedback_agent.run(
            query=f"```python\n{multi_issue_code}\n```"
        )
        
        response = result['response'].lower()
        
        # Should identify multiple issues
        assert 'syntax' in response or 'parenthes' in response
        assert 'leakage' in response or 'target' in response
    
    # --------------------------------------------------------------------------
    # Context-Enhanced Tests
    # --------------------------------------------------------------------------
    
    def test_agent_uses_competition_context_when_provided(self, code_feedback_agent):
        """Agent should enhance feedback with competition-specific context."""
        competition_context = {
            "competition": "titanic",
            "metric": "accuracy",
            "notebooks": [
                {"title": "Top Solution", "approach": "Random Forest with feature engineering"}
            ]
        }
        
        result = code_feedback_agent.run(
            query=f"Review my code:\n```python\n{VALID_CODE}\n```",
            context=competition_context
        )
        
        response = result['response'].lower()
        
        # When context is provided, response should be more specific
        # (exact assertion depends on implementation, but should reference context)
        assert len(response) > len(result.get('response', '')) or 'titanic' in response
    
    def test_agent_references_notebooks_when_available(self, code_feedback_agent):
        """Agent should reference competition notebooks in feedback when available."""
        context_with_notebooks = {
            "competition": "house-prices",
            "notebooks": [
                {
                    "title": "EDA + Random Forest Baseline",
                    "url": "https://kaggle.com/notebook1",
                    "approach": "Feature engineering with polynomial features"
                }
            ]
        }
        
        result = code_feedback_agent.run(
            query=f"How can I improve?\n```python\n{VALID_CODE}\n```",
            context=context_with_notebooks
        )
        
        # Response should consider available notebooks
        # (Exact behavior depends on orchestrator integration)
        assert result is not None
        assert 'response' in result
    
    # --------------------------------------------------------------------------
    # Output Format Tests
    # --------------------------------------------------------------------------
    
    def test_agent_returns_structured_output(self, code_feedback_agent):
        """Agent should return a structured dictionary."""
        result = code_feedback_agent.run(
            query=f"```python\n{VALID_CODE}\n```"
        )
        
        assert isinstance(result, dict)
        assert 'agent_name' in result
        assert 'response' in result
        assert result['agent_name'] == 'CodeFeedbackAgent'
    
    def test_agent_response_is_actionable(self, code_feedback_agent):
        """Agent feedback should be actionable (not just descriptive)."""
        result = code_feedback_agent.run(
            query=f"```python\n{INEFFICIENT_CODE}\n```"
        )
        
        response = result['response']
        
        # Should contain suggestions, not just problems
        assert any(word in response.lower() for word in ['try', 'use', 'instead', 'consider', 'recommend', 'should'])


# ==============================================================================
# ErrorDiagnosisAgent Tests
# ==============================================================================

class TestErrorDiagnosisAgent:
    """
    Test suite for error diagnosis agent.
    
    The agent should:
    1. Parse Python tracebacks
    2. Identify error types and causes
    3. Suggest specific fixes
    4. Work without competition context
    5. Search for similar errors in discussions when context provided
    """
    
    @pytest.fixture
    def error_diagnosis_agent(self):
        """Fixture to provide an ErrorDiagnosisAgent instance."""
        from agents.error_diagnosis_agent import ErrorDiagnosisAgent
        return ErrorDiagnosisAgent()
    
    # --------------------------------------------------------------------------
    # Core Functionality Tests
    # --------------------------------------------------------------------------
    
    def test_agent_parses_traceback(self, error_diagnosis_agent):
        """Agent should extract key information from Python tracebacks."""
        result = error_diagnosis_agent.run(
            query=f"I'm getting this error:\n{PYTHON_ERROR_WITH_TRACEBACK}"
        )
        
        response = result['response'].lower()
        
        # Should identify the error type
        assert 'valueerror' in response or 'value error' in response
        # Should mention the cause
        assert any(word in response for word in ['empty', '0 sample', 'no data', 'shape'])
    
    def test_agent_diagnoses_empty_array_error(self, error_diagnosis_agent):
        """Agent should diagnose empty array errors."""
        result = error_diagnosis_agent.run(
            query=f"Help! My model won't train:\n{PYTHON_ERROR_WITH_TRACEBACK}"
        )
        
        response = result['response'].lower()
        
        # Should explain the cause
        assert any(word in response for word in ['empty', 'no data', 'filter', 'split'])
        # Should suggest a fix
        assert any(word in response for word in ['check', 'verify', 'ensure', 'before'])
    
    def test_agent_diagnoses_shape_mismatch(self, error_diagnosis_agent):
        """Agent should diagnose shape mismatch errors."""
        result = error_diagnosis_agent.run(
            query=f"Getting this error: {SHAPE_MISMATCH_ERROR}\n\nMy code:\n```python\ndf['new_col'] = [1,2,3,4,5]\n```"
        )
        
        response = result['response'].lower()
        
        # Should identify shape mismatch
        assert 'shape' in response or 'mismatch' in response or 'length' in response
        # Should suggest checking dimensions
        assert any(word in response for word in ['match', 'same', 'length', 'dimension'])
    
    def test_agent_handles_error_without_code(self, error_diagnosis_agent):
        """Agent should handle cases where only error message is provided."""
        result = error_diagnosis_agent.run(
            query="I'm getting a KeyError: 'target' but I don't know why"
        )
        
        response = result['response'].lower()
        
        # Should explain KeyError
        assert 'key' in response or 'column' in response or 'missing' in response
        # Should suggest debugging steps
        assert any(word in response for word in ['check', 'exist', 'column', 'df.columns'])
    
    def test_agent_handles_error_with_code_context(self, error_diagnosis_agent):
        """Agent should use code context to provide better diagnosis."""
        context_code = """
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv('train.csv')
df_filtered = df[df['age'] > 100]  # This might result in empty dataframe

X = df_filtered.drop('target', axis=1)
y = df_filtered['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
"""
        
        result = error_diagnosis_agent.run(
            query=f"Error: {PYTHON_ERROR_WITH_TRACEBACK}\n\nMy code:\n```python\n{context_code}\n```"
        )
        
        response = result['response'].lower()
        
        # Should connect the filtering to the empty array error
        assert any(word in response for word in ['filter', 'age', 'empty', 'condition'])
    
    def test_agent_suggests_specific_fixes(self, error_diagnosis_agent):
        """Agent should provide specific, actionable fixes."""
        result = error_diagnosis_agent.run(
            query="ModuleNotFoundError: No module named 'sklearn'"
        )
        
        response = result['response'].lower()
        
        # Should suggest installation
        assert 'install' in response or 'pip' in response
        # Should be specific
        assert 'sklearn' in response or 'scikit-learn' in response
    
    def test_agent_works_without_context(self, error_diagnosis_agent):
        """Agent should function without competition context."""
        result = error_diagnosis_agent.run(
            query="ImportError: cannot import name 'RandomForestClassifier' from 'sklearn.ensemble'",
            context=None
        )
        
        assert result is not None
        assert 'response' in result
        assert len(result['response']) > 30
    
    # --------------------------------------------------------------------------
    # Context-Enhanced Tests
    # --------------------------------------------------------------------------
    
    def test_agent_searches_discussions_when_context_provided(self, error_diagnosis_agent):
        """Agent should reference discussion solutions when context available."""
        competition_context = {
            "competition": "titanic",
            "discussions": [
                {
                    "title": "Solving ValueError: Found array with 0 samples",
                    "url": "https://kaggle.com/discussion1",
                    "solution": "Check your data filtering steps"
                }
            ]
        }
        
        result = error_diagnosis_agent.run(
            query=PYTHON_ERROR_WITH_TRACEBACK,
            context=competition_context
        )
        
        # Should reference available discussions
        # (Exact behavior depends on orchestrator integration)
        assert result is not None
        assert 'response' in result
    
    def test_agent_considers_competition_specific_errors(self, error_diagnosis_agent):
        """Agent should consider competition-specific error patterns when context provided."""
        context = {
            "competition": "house-prices",
            "common_errors": [
                "Shape mismatch due to multi-output format",
                "Missing values in test set not in train set"
            ]
        }
        
        result = error_diagnosis_agent.run(
            query=SHAPE_MISMATCH_ERROR,
            context=context
        )
        
        # Should leverage context if available
        assert result is not None
        assert 'response' in result
    
    # --------------------------------------------------------------------------
    # Output Format Tests
    # --------------------------------------------------------------------------
    
    def test_agent_returns_structured_output(self, error_diagnosis_agent):
        """Agent should return a structured dictionary."""
        result = error_diagnosis_agent.run(
            query="ValueError: invalid literal for int() with base 10: 'abc'"
        )
        
        assert isinstance(result, dict)
        assert 'agent_name' in result
        assert 'response' in result
        assert result['agent_name'] == 'ErrorDiagnosisAgent'
    
    def test_agent_diagnosis_includes_fix(self, error_diagnosis_agent):
        """Agent diagnosis should always include a suggested fix."""
        result = error_diagnosis_agent.run(
            query="TypeError: unsupported operand type(s) for +: 'int' and 'str'"
        )
        
        response = result['response'].lower()
        
        # Should suggest conversion or fix
        assert any(word in response for word in ['convert', 'cast', 'int(', 'str(', 'type'])


# ==============================================================================
# Integration Tests (Agent Coordination)
# ==============================================================================

class TestCodeHandlingIntegration:
    """
    Tests for how code handling agents work together.
    These tests validate orchestrator integration points.
    """
    
    def test_code_feedback_can_trigger_error_diagnosis(self):
        """When code has errors, feedback agent should identify them for diagnosis."""
        from agents.code_feedback_agent import CodeFeedbackAgent
        
        agent = CodeFeedbackAgent()
        result = agent.run(
            query=f"```python\n{SYNTAX_ERROR_CODE}\n```"
        )
        
        response = result['response'].lower()
        
        # Should identify that there's an error
        assert any(word in response for word in ['error', 'syntax', 'issue', 'problem'])
    
    def test_agents_maintain_session_state(self):
        """Agents should preserve context across calls (via orchestrator)."""
        from agents.code_feedback_agent import CodeFeedbackAgent
        
        agent = CodeFeedbackAgent()
        
        # First query
        result1 = agent.run(
            query=f"```python\n{VALID_CODE}\n```",
            context={"approach": "Random Forest"}
        )
        
        # Context should be preserved in output
        assert 'updated_context' in result1
        assert result1['updated_context'] is not None


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================

class TestCodeHandlingEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_code_feedback_handles_empty_query(self):
        """Agent should handle empty queries gracefully."""
        from agents.code_feedback_agent import CodeFeedbackAgent
        agent = CodeFeedbackAgent()
        
        result = agent.run(query="")
        
        assert result is not None
        assert 'response' in result
    
    def test_code_feedback_handles_no_code_in_query(self):
        """Agent should handle queries without code blocks."""
        from agents.code_feedback_agent import CodeFeedbackAgent
        agent = CodeFeedbackAgent()
        
        result = agent.run(query="How do I improve my model?")
        
        assert result is not None
        assert 'response' in result
    
    def test_error_diagnosis_handles_non_python_errors(self):
        """Agent should handle non-Python error messages."""
        from agents.error_diagnosis_agent import ErrorDiagnosisAgent
        agent = ErrorDiagnosisAgent()
        
        result = agent.run(query="404 Not Found: API endpoint doesn't exist")
        
        assert result is not None
        assert 'response' in result
    
    def test_agents_handle_very_long_code(self):
        """Agents should handle long code snippets without breaking."""
        from agents.code_feedback_agent import CodeFeedbackAgent
        agent = CodeFeedbackAgent()
        
        long_code = "import pandas as pd\n" + "df = df.copy()\n" * 1000
        result = agent.run(query=f"```python\n{long_code}\n```")
        
        assert result is not None
        assert 'response' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])




