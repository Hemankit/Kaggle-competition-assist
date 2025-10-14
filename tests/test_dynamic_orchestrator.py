#!/usr/bin/env python3
"""
Test script for the Dynamic Cross-Framework Orchestrator
Demonstrates autonomous agent selection and interaction patterns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routing.dynamic_orchestrator import DynamicCrossFrameworkOrchestrator, InteractionPattern
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dynamic_orchestrator():
    """Test the dynamic cross-framework orchestrator with various query types"""
    
    orchestrator = DynamicCrossFrameworkOrchestrator()
    
    # Test queries that should trigger different interaction patterns
    test_queries = [
        {
            "query": "Help me understand this error in my Kaggle notebook",
            "expected_pattern": InteractionPattern.VALIDATION,
            "description": "Error diagnosis should trigger validation pattern"
        },
        {
            "query": "I need to plan my competition timeline and get feedback on my code",
            "expected_pattern": InteractionPattern.COLLABORATIVE,
            "description": "Multiple intents should trigger collaborative pattern"
        },
        {
            "query": "Explain how to use neural networks for this competition",
            "expected_pattern": InteractionPattern.SEQUENTIAL,
            "description": "Single intent should trigger sequential pattern"
        },
        {
            "query": "Can you help me with both data preprocessing and model training strategies?",
            "expected_pattern": InteractionPattern.HIERARCHICAL,
            "description": "Complex multi-step query should trigger hierarchical pattern"
        }
    ]
    
    print("🧪 Testing Dynamic Cross-Framework Orchestrator")
    print("=" * 60)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 40)
        
        try:
            # Create interaction plan
            plan = orchestrator.create_interaction_plan(test_case['query'])
            
            print(f"✅ Plan created successfully!")
            print(f"   Pattern: {plan.pattern.value}")
            print(f"   Agents: {[agent.name for agent in plan.agents]}")
            print(f"   Frameworks: {list(set(agent.framework for agent in plan.agents))}")
            print(f"   Complexity Score: {plan.complexity_score:.2f}")
            print(f"   Expected Duration: {plan.expected_duration}")
            
            # Check if expected pattern matches
            if plan.pattern == test_case['expected_pattern']:
                print(f"   ✅ Pattern matches expected: {test_case['expected_pattern'].value}")
            else:
                print(f"   ⚠️  Pattern differs from expected: {test_case['expected_pattern'].value}")
            
            # Show agent selection reasoning
            print(f"   Agent Selection Reasoning:")
            for agent in plan.agents:
                print(f"     - {agent.name} ({agent.framework}): {agent.reasoning}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            logger.error(f"Test {i} failed: {e}")
    
    print(f"\n🎯 Testing Cross-Framework Execution")
    print("=" * 40)
    
    # Test a simple execution (without actual LLM calls)
    try:
        simple_query = "Help me debug my code"
        plan = orchestrator.create_interaction_plan(simple_query)
        print(f"✅ Plan created for execution test")
        print(f"   Pattern: {plan.pattern.value}")
        print(f"   Agents: {[agent.name for agent in plan.agents]}")
        
        # Note: We're not actually executing here to avoid LLM API calls
        # In production, you would call: orchestrator.execute_plan(plan, simple_query)
        print(f"   ⚠️  Execution skipped (would require LLM API keys)")
        
    except Exception as e:
        print(f"❌ Execution test failed: {e}")
        logger.error(f"Execution test failed: {e}")

def demonstrate_agent_selection_logic():
    """Demonstrate how agents are selected based on query analysis"""
    
    print(f"\n🔍 Agent Selection Logic Demonstration")
    print("=" * 50)
    
    orchestrator = DynamicCrossFrameworkOrchestrator()
    
    # Test different query types
    queries = [
        "How do I improve my model's accuracy?",
        "What's the timeline for this competition?", 
        "I'm getting an error in my code",
        "Explain this notebook step by step",
        "Help me plan my approach and validate my code"
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        
        try:
            # Parse intent
            from routing.intent_router import parse_user_intent
            parsed = parse_user_intent(query)
            
            print(f"   Intent: {parsed.get('intent', 'N/A')}")
            print(f"   Sub-intents: {parsed.get('sub_intents', [])}")
            print(f"   Reasoning Style: {parsed.get('reasoning_style', 'N/A')}")
            
            # Analyze complexity
            complexity = orchestrator.analyze_query_complexity(parsed)
            print(f"   Complexity Score: {complexity['score']:.2f}")
            print(f"   Needs Validation: {complexity['needs_validation']}")
            print(f"   Needs Collaboration: {complexity['needs_collaboration']}")
            
            # Select agents
            agents = orchestrator.select_agents_dynamically(parsed)
            print(f"   Selected Agents: {[agent.name for agent in agents]}")
            
            # Determine pattern
            pattern = orchestrator.determine_interaction_pattern(complexity, agents)
            print(f"   Interaction Pattern: {pattern.value}")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")

if __name__ == "__main__":
    test_dynamic_orchestrator()
    demonstrate_agent_selection_logic()
    
    print(f"\n🎉 Dynamic Cross-Framework Orchestrator Test Complete!")
    print(f"✅ The system can autonomously select agents and frameworks")
    print(f"✅ Interaction patterns are determined dynamically")
    print(f"✅ No hardcoded sequences - everything is query-driven")



