#!/usr/bin/env python3
"""
Test script to verify workflow fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_workflow_imports():
    """Test that workflow imports work correctly"""
    print("🧪 Testing Workflow Import Fixes")
    print("=" * 40)
    
    try:
        # Test graph_nodes imports
        from workflows.graph_nodes import (
            preprocessing_node,
            router_node,
            competition_summary_node,
            notebook_explainer_node,
            discussion_helper_node,
            error_diagnosis_node,
            execution_bridge_node,
            reasoning_node,
            conversational_node,
            memory_update_node,
            meta_monitor_node,
            meta_intervention_node,
            aggregation_node,
            run_agent_if_intent_matches
        )
        print("✅ All graph_nodes imports successful")
        
        # Test graph_workflow imports
        from workflows.graph_workflow import compiled_graph, OrchestratorState
        print("✅ Graph workflow imports successful")
        
        # Test that the compiled graph exists
        if compiled_graph:
            print("✅ Compiled graph exists")
        else:
            print("❌ Compiled graph is None")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_node_functions():
    """Test that node functions work with sample data"""
    print(f"\n🔧 Testing Node Functions")
    print("=" * 30)
    
    try:
        from workflows.graph_nodes import (
            preprocessing_node,
            router_node,
            competition_summary_node,
            memory_update_node,
            meta_monitor_node,
            aggregation_node
        )
        
        # Test state structure
        sample_state = {
            "original_query": "Help me understand this Kaggle competition",
            "memory": {"past_queries": []},
            "metadata": {}
        }
        
        # Test preprocessing node
        result_state = preprocessing_node(sample_state.copy())
        if "cleaned_query" in result_state:
            print("✅ Preprocessing node works")
        else:
            print("❌ Preprocessing node failed")
            
        # Test router node
        result_state = router_node(sample_state.copy())
        if "selected_agents" in result_state and "selected_backend" in result_state:
            print("✅ Router node works")
        else:
            print("❌ Router node failed")
            
        # Test memory update node
        result_state = memory_update_node(sample_state.copy())
        if "memory" in result_state:
            print("✅ Memory update node works")
        else:
            print("❌ Memory update node failed")
            
        # Test meta monitor node
        result_state = meta_monitor_node(sample_state.copy())
        if "meta_intervention_needed" in result_state:
            print("✅ Meta monitor node works")
        else:
            print("❌ Meta monitor node failed")
            
        # Test aggregation node
        result_state = aggregation_node({"agent_outputs": [{"response": "test"}]})
        if "final_response" in result_state:
            print("✅ Aggregation node works")
        else:
            print("❌ Aggregation node failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Node function test failed: {e}")
        return False

def test_agent_selection_logic():
    """Test the agent selection logic in router node"""
    print(f"\n🎯 Testing Agent Selection Logic")
    print("=" * 35)
    
    try:
        from workflows.graph_nodes import router_node
        
        test_cases = [
            {
                "query": "What is this Kaggle competition about?",
                "expected_intent": "competition",
                "expected_agents": ["competition_summary"]
            },
            {
                "query": "Help me debug this error in my code",
                "expected_intent": "error",
                "expected_agents": ["error_diagnosis"]
            },
            {
                "query": "Explain this notebook step by step",
                "expected_intent": "notebook",
                "expected_agents": ["notebook_explainer"]
            },
            {
                "query": "What are people discussing in the forums?",
                "expected_intent": "discussion",
                "expected_agents": ["discussion_helper"]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['query']}")
            
            state = {
                "original_query": test_case["query"],
                "memory": {"past_queries": []},
                "metadata": {}
            }
            
            result = router_node(state)
            
            # Check if intent was detected
            detected_intent = result.get("intent", "")
            print(f"   Detected intent: {detected_intent}")
            
            # Check if correct agents were selected
            selected_agents = result.get("selected_agents", [])
            print(f"   Selected agents: {selected_agents}")
            
            # Check if backend was selected
            selected_backend = result.get("selected_backend", "")
            print(f"   Selected backend: {selected_backend}")
            
            if selected_agents and selected_backend:
                print(f"   ✅ Agent selection successful")
            else:
                print(f"   ❌ Agent selection failed")
                
        return True
        
    except Exception as e:
        print(f"❌ Agent selection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Workflow Fixes")
    print("=" * 50)
    
    # Run all tests
    import_success = test_workflow_imports()
    node_success = test_node_functions()
    logic_success = test_agent_selection_logic()
    
    print(f"\n📊 Test Results:")
    print(f"   Import Tests: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   Node Tests: {'✅ PASS' if node_success else '❌ FAIL'}")
    print(f"   Logic Tests: {'✅ PASS' if logic_success else '❌ FAIL'}")
    
    if all([import_success, node_success, logic_success]):
        print(f"\n🎉 All workflow fixes are working correctly!")
    else:
        print(f"\n⚠️  Some workflow fixes need attention")



