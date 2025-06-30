from agents.base_rag_retrieval_agent import BaseRAGRetrievalAgent

discussion_prompt = """
You are a helpful assistant for Kaggle competitions. Given a chunk from the discussion section, summarize the key points or provide a direct answer to the user’s question.

Discussion Section:
-----------------
{section_content}

Answer (be concise, helpful, and competition-aware):
"""

class DiscussionHelperAgent(BaseRAGRetrievalAgent):
    def __init__(self, retriever=None, llm=None):
        super().__init__(
            agent_name="DiscussionHelperAgent",
            prompt_template=discussion_prompt,
            section="discussion",
            retriever=retriever,
            llm=llm
        )