from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

class ScrapingDecider:
    """
    This class builds the LLM-based decision chain that determines
    whether a given item should be deep scraped based on query + metadata.
    """

    def __init__(self, llm):
        self.llm = llm
        self.chain = self._build_chain()

    def _build_chain(self) -> Runnable:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert content retriever. Based on the user’s query and the content metadata, decide if a deeper scrape is needed."),
            ("human", """User query: {query}
Section: {section}
Item title: {title}
Has image: {has_image}
Is pinned: {pinned}
Brief content: {content_snippet}

Should this be deep scraped? Answer YES or NO and briefly explain.""")
        ])

        return prompt | self.llm | StrOutputParser()

    def should_scrape(self, metadata: dict) -> str:
        """
        metadata = {
            "query": str,
            "section": str,
            "title": str,
            "has_image": bool,
            "pinned": bool,
            "content_snippet": str
        }
        Returns a string like: "YES - snippet seems vague and user query requires detail"
        """
        return self.chain.invoke(metadata)