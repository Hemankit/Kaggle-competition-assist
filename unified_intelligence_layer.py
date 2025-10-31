"""
Unified Intelligence Layer - V2.0 Query Analysis and Classification
Wraps existing routing/intent_router functionality with a clean interface
"""

from typing import Dict, Any, Optional
from routing.intent_router import parse_user_intent, route_to_agents

class UnifiedIntelligenceLayer:
    """
    Unified Intelligence Layer for query analysis and classification.
    Determines query complexity, category, and optimal routing strategy.
    """
    
    def __init__(self, llm=None):
        """
        Initialize with optional LLM (will use default from config if not provided)
        """
        self.llm = llm
    
    def analyze_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze query to determine complexity, category, and routing strategy.
        
        Args:
            query: User query string
            context: Optional context (competition_slug, user_level, etc.)
        
        Returns:
            {
                'complexity': 'low' | 'medium' | 'high',
                'category': 'RAG' | 'CODE' | 'REASONING' | 'HYBRID' | 'EXTERNAL',
                'intent': Main intent from router,
                'sub_intents': Sub-intents from router,
                'recommended_mode': Suggested orchestration mode
            }
        """
        # Use existing intent router
        parsed = parse_user_intent(query, self.llm)
        
        # Map to our complexity levels
        complexity = self._determine_complexity(parsed, query)
        
        # Map to our categories
        category = self._determine_category(parsed, query)
        
        return {
            'complexity': complexity,
            'category': category,
            'intent': parsed.get('intent', 'general'),
            'sub_intents': parsed.get('sub_intents', []),
            'recommended_mode': parsed.get('recommended_mode', 'langgraph'),
            'reasoning_style': parsed.get('reasoning_style', 'fast'),
            'metadata_flags': parsed.get('metadata_flags', {}),
            'raw_analysis': parsed
        }
    
    def _determine_complexity(self, parsed: Dict, query: str) -> str:
        """
        Determine query complexity based on intent analysis and keywords.
        """
        sub_intents = parsed.get('sub_intents', [])
        reasoning_style = parsed.get('reasoning_style', '').lower()
        
        # High complexity indicators
        high_complexity_keywords = [
            'ideas', 'improve', 'optimize', 'strategy', 'approach',
            'better', 'should i', 'recommend', 'suggest', 'create',
            'build', 'develop', 'implement', 'analyze all'
        ]
        
        # Low complexity indicators
        low_complexity_keywords = [
            'what is', 'show me', 'display', 'get', 'find',
            'list', 'evaluation metric', 'overview', 'summary'
        ]
        
        query_lower = query.lower()
        
        # Check for high complexity
        if reasoning_style in ['multi-hop', 'conversational']:
            return 'high'
        
        if len(sub_intents) >= 3:
            return 'high'
        
        if any(keyword in query_lower for keyword in high_complexity_keywords):
            return 'high'
        
        # Check for low complexity
        if any(keyword in query_lower for keyword in low_complexity_keywords):
            if len(sub_intents) <= 1:
                return 'low'
        
        # Default to medium
        return 'medium'
    
    def _determine_category(self, parsed: Dict, query: str) -> str:
        """
        Determine query category based on intent and content.
        """
        intent = parsed.get('intent', '').lower()
        sub_intents = parsed.get('sub_intents', [])
        query_lower = query.lower()
        
        # CODE category
        code_keywords = ['code', 'function', 'class', 'error', 'bug', 'debug', 
                        'implementation', 'syntax', 'fix', 'review']
        if intent in ['error', 'code_feedback'] or any(k in query_lower for k in code_keywords):
            return 'CODE'
        
        # EXTERNAL category (requires web search)
        external_keywords = ['latest', 'recent', 'current', 'best practices', 
                            'state of the art', 'trending', 'new']
        if any(k in query_lower for k in external_keywords):
            return 'EXTERNAL'
        
        # REASONING category (complex multi-step)
        if parsed.get('reasoning_style') in ['multi-hop', 'conversational']:
            return 'REASONING'
        
        # HYBRID category (multiple intents)
        if len(sub_intents) >= 3:
            return 'HYBRID'
        
        # RAG category (retrieval-based)
        rag_intents = ['overview', 'discussion', 'notebook', 'data', 'meta']
        if intent in rag_intents:
            return 'RAG'
        
        # Default
        return 'GENERAL'


# Backwards compatibility
def analyze_query(query: str, llm=None, context: Dict = None) -> Dict[str, Any]:
    """
    Standalone function for query analysis (backwards compatibility)
    """
    layer = UnifiedIntelligenceLayer(llm=llm)
    return layer.analyze_query(query, context)
