
from langchain_core.prompts import ChatPromptTemplate

# 🤖 Prompt used to decide whether to deep scrape an item
deep_scrape_decision_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert content retriever. Based on the user’s query and the content metadata, decide if a deeper scrape is needed."),
    ("human", 
     """User query: {query}
Section: {section}
Item title: {title}
Has image: {has_image}
Is pinned: {pinned}
Brief content: {content_snippet}

Should this be deep scraped? Answer YES or NO and briefly explain.""")
])
