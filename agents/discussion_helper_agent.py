from .base_rag_retrieval_agent import BaseRAGRetrievalAgent
from typing import Optional, Dict, Any, List
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


# Prompt for listing discussions (show pinned, list recent, etc.)
list_discussions_prompt = """You are helping a user browse Kaggle competition discussions.

User Query: {user_query}
Competition: {competition}

Retrieved Discussions:
{discussions_list}

Format a clean, helpful response that:
1. Briefly acknowledges what they asked for
2. Lists the discussions with key metadata
3. Suggests how to get more details if interested

Keep it concise and well-formatted. Use markdown for readability.
"""


# Prompt for analyzing discussion content (when full content available)
analyze_discussion_prompt = """You are a Kaggle discussion information retrieval agent. Your role is to present FACTUAL information from discussions - NOT to give advice or strategic insights.

User Query: {user_query}
Competition: {competition}

Discussion Details:
Title: {title}
Author: {author}
Date: {date}
Comments: {comment_count}

Content:
{content}

Present the KEY FACTS from this discussion:
1. What topic/question is being discussed?
2. What information, solutions, or approaches are mentioned?
3. What specific details or data points are shared?
4. What is the community sentiment (if apparent)?

BE FACTUAL, not advisory. Present information that reasoning agents can use.

DO NOT:
- Explain why content is relevant
- Suggest takeaways or actions
- Give strategic recommendations
- Interpret or advise

DO:
- Summarize what was discussed
- List solutions/approaches mentioned
- Present facts and details shared
- Note community reactions

Keep it concise and informative.
"""


# Prompt for searching/synthesizing multiple discussions
search_discussions_prompt = """You are the Kaggle Discussion Intelligence Agent. Transform raw discussion data into COMMUNITY INSIGHTS and ACTIONABLE INTELLIGENCE!

Your goal is NOT to just list what people said - users can browse Kaggle! Instead, provide SYNTHESIS, PATTERNS, and STRATEGIC VALUE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User Query: {user_query}
Competition: {competition}

Retrieved Discussions:
{discussions_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRUCTURE YOUR RESPONSE:

1️⃣ DIRECT ANSWER

Answer the query directly:
- YES/NO if asking "Are there discussions about X?"
- Clear summary if asking "What are people discussing?"
- Synthesized findings, not raw facts

2️⃣ SYNTHESIZED FINDINGS

Group insights by theme, NOT by individual post:
- **Consensus Views**: What the community agrees on
- **Debated Topics**: Where opinions differ
- **Emerging Patterns**: New trends or techniques mentioned
- **Warnings/Pitfalls**: What to avoid (community learned lessons)

3️⃣ RELEVANT DISCUSSIONS

List 2-3 most relevant discussions with context:
- "Title" by Author
- KEY POINT: Main insight from this discussion
- WHY IT MATTERS: How it helps your competition strategy

4️⃣ IDENTIFIED PATTERNS

Synthesize across discussions:
- Common themes (e.g., "3 discussions emphasize feature engineering")
- Consensus vs experimentation
- Evolution of thinking (early vs recent posts)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 KEY TAKEAWAY:

[ONE sentence synthesizing the most important community insight]

CRITICAL RULES:
- SYNTHESIZE, don't just list ("Community consensus: X works better than Y")
- Show PATTERNS across multiple discussions
- Highlight CONTRADICTIONS (debates are valuable!)
- Identify CONSENSUS (what most agree on)
- Note EVOLUTION (how thinking changed over time)
- Be ACTIONABLE (what should user do with this info?)

Transform raw discussion data into competitive intelligence!
"""


class DiscussionHelperAgent(BaseRAGRetrievalAgent):
    """
    Agent for helping users navigate and understand Kaggle competition discussions.
    
    Handles:
    - Listing discussions (pinned, recent, etc.)
    - Searching discussions by topic
    - Analyzing specific discussion posts
    """
    
    def __init__(self, retriever=None, llm=None):
        super().__init__(
            agent_name="DiscussionHelperAgent",
            prompt_template=list_discussions_prompt,  # Default for list queries
            section="discussion",
            retriever=retriever,
            llm=llm
        )
        self.llm = llm
        
        # Create chains for different query types
        self.list_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(list_discussions_prompt)
        )
        self.analyze_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(analyze_discussion_prompt)
        )
        self.search_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(search_discussions_prompt)
        )
    
    def format_discussions_list(self, discussions: List[Dict[str, Any]]) -> str:
        """Format multiple discussions for display."""
        if not discussions:
            return "No discussions found."
        
        formatted = []
        for i, disc in enumerate(discussions, 1):
            metadata = disc.get('metadata', {})
            
            title = metadata.get('title', 'Unknown')
            author = metadata.get('author', 'Unknown')
            date = metadata.get('date', 'Unknown')
            is_pinned = metadata.get('is_pinned', False)
            comment_count = metadata.get('comment_count', 0)
            url = metadata.get('url', '')
            
            pin_icon = "[PINNED] " if is_pinned else ""
            
            disc_info = f"{i}. {pin_icon}{title}\n"
            disc_info += f"   By: {author}"
            if date and date != 'Unknown':
                disc_info += f" | {date}"
            if comment_count > 0:
                disc_info += f" | {comment_count} comments"
            if url:
                disc_info += f"\n   URL: {url}"
            
            formatted.append(disc_info)
        
        return "\n\n".join(formatted)
    
    def list_discussions(
        self,
        discussions: List[Dict[str, Any]],
        user_query: str,
        competition: str
    ) -> str:
        """
        Format and present a list of discussions.
        For queries like: "Show pinned discussions", "List recent discussions"
        """
        discussions_list = self.format_discussions_list(discussions)
        
        # Use LLM to create a helpful response
        response = self.list_chain.run(
            user_query=user_query,
            competition=competition,
            discussions_list=discussions_list
        )
        
        return response
    
    def analyze_discussion(
        self,
        discussion: Dict[str, Any],
        user_query: str,
        competition: str
    ) -> str:
        """
        Analyze a specific discussion in detail.
        For queries like: "Explain this post", "Summarize discussion about X"
        """
        metadata = discussion.get('metadata', {})
        content = discussion.get('content', '')
        
        # If no full content yet, indicate this
        has_full_content = metadata.get('has_full_content', False)
        if not has_full_content or not content or len(content.strip()) < 100:
            # Metadata-only response
            title = metadata.get('title', 'Unknown')
            author = metadata.get('author', 'Unknown')
            date = metadata.get('date', 'Unknown')
            comment_count = metadata.get('comment_count', 0)
            url = metadata.get('url', '')
            
            base_response = f"""**Discussion:** {title}
**Author:** {author}
**Date:** {date}
**Comments:** {comment_count}

[Note: Full content not yet available. This discussion would need to be deep-scraped for detailed analysis.]

**URL:** {url}

To get detailed analysis, the system would need to fetch the full post content, including comments and any screenshots.
"""
            
            # Add engagement tip if relevant
            engagement_tip = self._generate_engagement_tip(discussion, user_query)
            return base_response + engagement_tip
        
        # Full analysis with content
        response = self.analyze_chain.run(
            user_query=user_query,
            competition=competition,
            title=metadata.get('title', 'Unknown'),
            author=metadata.get('author', 'Unknown'),
            date=metadata.get('date', 'Unknown'),
            comment_count=metadata.get('comment_count', 0),
            content=content[:2000]  # Limit to prevent token overflow
        )
        
        # Add engagement tip if relevant
        engagement_tip = self._generate_engagement_tip(discussion, user_query)
        return response + engagement_tip
    
    def search_discussions(
        self,
        discussions: List[Dict[str, Any]],
        user_query: str,
        competition: str
    ) -> str:
        """
        Search and synthesize findings from multiple discussions.
        For queries like: "Are there discussions about X?", "Find discussions about Y"
        """
        # Format discussions with content for LLM analysis
        discussions_content = []
        for i, disc in enumerate(discussions, 1):
            metadata = disc.get('metadata', {})
            content = disc.get('content', '')
            
            title = metadata.get('title', 'Unknown')
            author = metadata.get('author', 'Unknown')
            date = metadata.get('date', 'Unknown')
            
            disc_text = f"""**Discussion {i}: {title}**
By: {author} | {date}
Content Preview: {content[:500]}...
"""
            discussions_content.append(disc_text)
        
        formatted_content = "\n\n".join(discussions_content)
        
        # Use LLM to synthesize findings
        response = self.search_chain.run(
            user_query=user_query,
            competition=competition,
            discussions_content=formatted_content
        )
        
        return response
    
    def _generate_engagement_tip(
        self,
        discussion: Dict[str, Any],
        user_query: str
    ) -> str:
        """
        Generate contextual engagement tips based on discussion metadata.
        
        Only suggests engagement when:
        1. User has a problem/question (not just browsing)
        2. Discussion is active (recent, has comments)
        3. Engagement would likely be helpful
        
        This is Phase 2: Simple, metadata-based suggestions.
        Phase 5 will add multi-agent feedback loop for response handling.
        """
        metadata = discussion.get('metadata', {})
        
        # Extract metadata
        author = metadata.get('author', 'Unknown')
        comment_count = metadata.get('comment_count', 0)
        date = metadata.get('date', 'Unknown')
        title = metadata.get('title', 'Unknown')
        url = metadata.get('url', '')
        
        # Check if user has a problem/question
        problem_keywords = [
            'stuck', 'help', 'issue', 'error', 'problem', 'struggling',
            'confused', 'question', 'how to', 'how do', 'why',
            'not working', 'failed', 'fails', 'cannot', "can't"
        ]
        query_lower = user_query.lower()
        has_problem = any(keyword in query_lower for keyword in problem_keywords)
        
        # Check if discussion is active
        is_recent = any(indicator in date.lower() for indicator in ['ago', 'hour', 'day', 'week'])
        has_activity = comment_count > 0
        is_active = is_recent and has_activity
        
        # Don't suggest engagement if:
        # - Just browsing (no problem)
        # - Discussion is inactive
        # - No author info
        if not has_problem or not is_active or author == 'Unknown':
            return ""
        
        # Generate specific engagement tip
        tip = f"""

---
### Community Engagement Tip

This discussion has **{comment_count} comments** and appears active. If you need specific guidance on your challenge, consider engaging with **{author}** or other contributors.

**Tips for effective engagement:**
- Be specific about your issue and what you've tried
- Share relevant code snippets or error messages
- Ask focused questions rather than general requests

**Example question:**
"I'm facing [specific issue]. I tried [your approach] but encountered [specific problem]. Any suggestions?"

Clear, specific questions typically get better responses from the community!
"""
        
        return tip
    
    def run(self, structured_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        V2-compatible run method that fetches discussions from ChromaDB.
        
        Args:
            structured_query: Query with metadata (V2.0 format)
            
        Returns:
            Dict with agent response
        """
        try:
            # Extract query and metadata
            query = structured_query.get("cleaned_query", structured_query.get("query", ""))
            metadata = structured_query.get("metadata", {})
            competition = metadata.get("competition_slug", metadata.get("competition", "Unknown"))
            
            # Fetch discussions from ChromaDB
            chunks = self.fetch_sections(structured_query)
            
            # Convert chunks to discussions format
            discussions = []
            for chunk in chunks:
                discussions.append({
                    'content': chunk.get('content', ''),
                    'metadata': chunk.get('metadata', {})
                })
            
            # Call legacy run method
            return self.run_legacy(discussions, query, competition, query_type="search")
            
        except Exception as e:
            return {
                "agent_name": self.name,
                "response": f"Discussion analysis failed: {str(e)}"
            }
    
    def run_legacy(
        self,
        discussions: List[Dict[str, Any]],
        user_query: str,
        competition: str = "Unknown",
        query_type: str = "list"
    ) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        
        Args:
            discussions: Retrieved discussions from ChromaDB
            user_query: User's question
            competition: Competition name/slug
            query_type: "list", "search", or "analyze"
        
        Returns:
            Dict with agent response
        """
        try:
            if not discussions:
                response = f"No discussions found for your query: '{user_query}'"
            elif query_type == "analyze":
                # Single discussion deep dive
                response = self.analyze_discussion(discussions[0], user_query, competition)
            elif query_type == "search":
                # Search and synthesize multiple discussions
                response = self.search_discussions(discussions, user_query, competition)
            else:
                # List query (browsing)
                response = self.list_discussions(discussions, user_query, competition)
            
            return {
                "agent_name": self.name,
                "response": response,
                "discussions_count": len(discussions)
            }
            
        except Exception as e:
            return {
                "agent_name": self.name,
                "response": f"Error processing discussions: {str(e)}",
                "discussions_count": 0
            }