from agents.base_rag_retrieval_agent import BaseRAGRetrievalAgent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
notebook_prompt = """
You are an expert Kaggle competition assistant. Explain the following notebook or model section to a beginner user.

Section:
-----------------
{section_content}

Explanation (use friendly language, include purpose and any ML context):
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