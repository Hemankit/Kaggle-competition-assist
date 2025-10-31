"""
Response Formatter - Formats responses from different agents
Ensures consistent, well-structured responses regardless of agent type.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """
    Formats responses from different agents into a consistent structure.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def format_response(self, processed_response: Dict[str, Any], 
                       query: str, agent_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the processed response into a consistent structure.
        
        Args:
            processed_response: Response from the agent
            query: Original user query
            agent_decision: Agent selection decision
            
        Returns:
            Formatted response
        """
        try:
            # Extract base information
            response_text = processed_response.get("response", "")
            agent_type = processed_response.get("type", "unknown")
            confidence = processed_response.get("confidence", 0.5)
            
            # Create base formatted response
            formatted = {
                "query": query,
                "response": response_text,
                "agent_type": agent_type,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "reasoning": agent_decision.get("reasoning", ""),
                    "data_used": processed_response.get("data_used", {}),
                    "reasoning_steps": processed_response.get("reasoning_steps", [])
                }
            }
            
            # Add agent-specific formatting
            if agent_type == "conversation":
                formatted = self._format_conversation_response(formatted, processed_response)
            elif agent_type == "reasoning":
                formatted = self._format_reasoning_response(formatted, processed_response)
            else:
                formatted = self._format_generic_response(formatted, processed_response)
            
            # Add quality indicators
            formatted["quality_indicators"] = self._assess_response_quality(formatted)
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return self._create_error_response(query, str(e))

    def _format_conversation_response(self, formatted: Dict[str, Any], 
                                    processed_response: Dict[str, Any]) -> Dict[str, Any]:
        """Format conversation agent response."""
        # Add conversation-specific metadata
        formatted["metadata"]["response_type"] = "conversational"
        formatted["metadata"]["complexity"] = "simple"
        
        # Ensure response is conversational
        response_text = formatted["response"]
        if not response_text.endswith(('.', '!', '?')):
            response_text += "."
        formatted["response"] = response_text
        
        return formatted

    def _format_reasoning_response(self, formatted: Dict[str, Any], 
                                 processed_response: Dict[str, Any]) -> Dict[str, Any]:
        """Format reasoning agent response."""
        # Add reasoning-specific metadata
        formatted["metadata"]["response_type"] = "analytical"
        formatted["metadata"]["complexity"] = "complex"
        formatted["metadata"]["method"] = processed_response.get("method", "unknown")
        
        # Structure reasoning steps
        reasoning_steps = processed_response.get("reasoning_steps", [])
        if reasoning_steps:
            formatted["metadata"]["reasoning_steps"] = reasoning_steps
            
        # Add reasoning summary
        if "reasoning_steps" in formatted["metadata"]:
            formatted["metadata"]["reasoning_summary"] = self._create_reasoning_summary(
                formatted["response"], reasoning_steps
            )
        
        return formatted

    def _format_generic_response(self, formatted: Dict[str, Any], 
                               processed_response: Dict[str, Any]) -> Dict[str, Any]:
        """Format generic response."""
        formatted["metadata"]["response_type"] = "generic"
        formatted["metadata"]["complexity"] = "unknown"
        
        return formatted

    def _assess_response_quality(self, formatted: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of the formatted response."""
        response_text = formatted["response"]
        confidence = formatted["confidence"]
        
        # Length assessment
        word_count = len(response_text.split())
        if word_count < 10:
            length_quality = "too_short"
        elif word_count < 50:
            length_quality = "short"
        elif word_count < 200:
            length_quality = "good"
        else:
            length_quality = "detailed"
        
        # Confidence assessment
        if confidence >= 0.8:
            confidence_quality = "high"
        elif confidence >= 0.6:
            confidence_quality = "medium"
        else:
            confidence_quality = "low"
        
        # Completeness assessment
        completeness_indicators = [
            "based on", "according to", "the data shows", "analysis reveals",
            "recommendation", "suggestion", "next step"
        ]
        
        response_lower = response_text.lower()
        completeness_score = sum(1 for indicator in completeness_indicators 
                               if indicator in response_lower)
        
        if completeness_score >= 3:
            completeness_quality = "comprehensive"
        elif completeness_score >= 1:
            completeness_quality = "adequate"
        else:
            completeness_quality = "basic"
        
        return {
            "length": length_quality,
            "confidence": confidence_quality,
            "completeness": completeness_quality,
            "word_count": word_count,
            "completeness_score": completeness_score
        }

    def _create_reasoning_summary(self, response: str, reasoning_steps: List[str]) -> str:
        """Create a summary of the reasoning process."""
        if not reasoning_steps:
            return "No specific reasoning steps identified"
            
        summary_parts = [f"Analysis followed {len(reasoning_steps)} steps:"]
        for i, step in enumerate(reasoning_steps, 1):
            summary_parts.append(f"{i}. {step}")
            
        return "\n".join(summary_parts)

    def _create_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "query": query,
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "agent_type": "error",
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "error": error,
                "response_type": "error",
                "complexity": "unknown"
            },
            "quality_indicators": {
                "length": "short",
                "confidence": "low",
                "completeness": "basic",
                "word_count": 0,
                "completeness_score": 0
            }
        }

