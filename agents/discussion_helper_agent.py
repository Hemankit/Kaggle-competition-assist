from agents.base_agent import BaseAgent
from typing import Optional, Dict


from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Define the discussion prompt template
discussion_prompt = """Post Title: {post_title}
User Question: {user_question}
Provide a helpful and relevant discussion response based on the post title and user question.
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
        self.llm = llm
        self.chain = LLMChain(llm=self.llm, prompt=PromptTemplate.from_template(discussion_prompt))

    def format_prompt(self, post_title, user_question):
        if not post_title or post_title.strip() == "":
            post_title = "No relevant discussion found."
        return self.prompt_template.format(
            post_title=post_title,
            user_question=user_question
        )

    def run(self, post_title, user_question):
        prompt = self.format_prompt(post_title, user_question)
        return self.chain.run(post_title=post_title, user_question=user_question)