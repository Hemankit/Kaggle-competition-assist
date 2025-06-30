# hybrid_scraping_routing/chain_builders.py

from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import ChatGroq
from langchain_core.runnables import Runnable
from .prompt_templates import deep_scrape_decision_prompt

def build_deep_scrape_decision_chain(llm=None) -> Runnable:
    """
    Creates a LangChain decision chain for determining whether an item should be deep scraped.
    """
    if llm is None:
        llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)  # Default fallback

    return deep_scrape_decision_prompt | llm | StrOutputParser()