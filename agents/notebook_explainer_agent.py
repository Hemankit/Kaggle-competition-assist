from agents.base_rag_retrieval_agent import BaseRAGRetrievalAgent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

notebook_prompt = """
You are an expert Kaggle competition analyst. Analyze the following notebook(s) and provide strategic insights.

Context:
- Competition: {competition}
- User Level: {user_level}
- Analysis Goal: {tone}

Notebook Content:
-----------------
{section_content}

Provide a comprehensive analysis that includes:

1. **Key Techniques Identified:**
   - What algorithms/models are used?
   - What feature engineering approaches?
   - What data preprocessing steps?

2. **Why This Approach Works:**
   - What makes this notebook highly voted?
   - What competitive advantages does it provide?
   - What best practices are demonstrated?

3. **Actionable Insights:**
   - What can users learn from this?
   - What techniques should they try?
   - What pitfalls to avoid?

4. **Code Quality Observations:**
   - Is the code well-structured?
   - Are there reusable patterns?
   - Any performance optimizations?

Keep your analysis concise, practical, and focused on helping the user improve their submission.
"""

class NotebookExplainerAgent(BaseRAGRetrievalAgent):
    def __init__(self, retriever=None, llm=None):
        super().__init__(
            agent_name="NotebookExplainerAgent",
            prompt_template=notebook_prompt,
            section="code",
            retriever=retriever,
            llm=llm
        )