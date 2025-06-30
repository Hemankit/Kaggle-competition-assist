from agents.base_rag_retrieval_agent import BaseRAGRetrievalAgent

overview_prompt = """
You are a Kaggle competition assistant. Use the overview section to answer the user's question or explain competition details clearly.

Overview Section:
-----------------
{section_content}

Response (include relevant rules, objectives, or dataset info):
"""

class CompetitionOverviewAgent(BaseRAGRetrievalAgent):
    def __init__(self, retriever=None, llm=None):
        super().__init__(
            agent_name="CompetitionOverviewAgent",
            prompt_template=overview_prompt,
            section="overview",
            retriever=retriever,
            llm=llm
        )
