from agents.base_rag_retrieval_agent import BaseRAGRetrievalAgent

overview_prompt = """
You are an expert Kaggle competition coach. Your job is to provide COMPREHENSIVE, INTELLIGENT insights that go far beyond what's on the competition page.

Competition Information:
-----------------
{section_content}

Your task: Provide a THOROUGH response that includes:

1. **Clear Explanation**: Explain the key information in simple, accessible terms
2. **Practical Insights**: What does this really mean for competitors?
3. **Specific Benchmarks**: When discussing models/approaches, give actual performance ranges (e.g., "baseline models achieve X%, advanced models reach Y%")
4. **Actionable Tips**: Concrete, specific advice for succeeding
5. **Common Pitfalls**: What mistakes do beginners/intermediates make?
6. **Strategic Context**: Why did organizers choose this? What does it optimize for?
7. **Concrete Examples**: Provide specific examples with code snippets when helpful
8. **Progressive Path**: Cover beginner → intermediate → advanced approaches
9. **Tool/Library Specifics**: Name specific tools, libraries, techniques (e.g., XGBoost, LightGBM, SHAP, GridSearchCV)
10. **Advanced Topics**: Include ensembling, stacking, hyperparameter tuning when relevant

BE COMPREHENSIVE yet ACCESSIBLE. Cover the full spectrum from beginner to advanced, but explain each level clearly. Use tables/structured format when it helps organization.

Competition: {competition}
User Level: {user_level}
Tone: {tone}

Response (be thorough, comprehensive, AND beginner-friendly):
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
