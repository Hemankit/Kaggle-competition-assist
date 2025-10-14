#!/usr/bin/env python3
"""
Simplified Multi-Agent System Test
Tests structure without LLM dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_agent_files_exist():
    """Test that all agent files exist and have correct structure"""
    print("🤖 Testing Agent Files Structure")
    print("=" * 35)
    
    agent_files = [
        "agents/competition_summary_agent.py",
        "agents/notebook_explainer_agent.py", 
        "agents/discussion_helper_agent.py",
        "agents/error_diagnosis_agent.py",
        "agents/timeline_coach_agent.py",
        "agents/code_feedback_agent.py",
        "agents/multihop_reasoning_agent.py",
        "agents/progress_monitor_agent.py",
        "agents/base_agent.py",
        "agents/base_rag_retrieval_agent.py"
    ]
    
    all_exist = True
    for agent_file in agent_files:
        if os.path.exists(agent_file):
            print(f"✅ {agent_file} exists")
        else:
            print(f"❌ {agent_file} missing")
            all_exist = False
    
    return all_exist

def test_routing_files_exist():
    """Test that all routing files exist"""
    print(f"\n🎯 Testing Routing Files Structure")
    print("=" * 35)
    
    routing_files = [
        "routing/dynamic_orchestrator.py",
        "routing/intent_router.py",
        "routing/capability_scoring.py",
        "routing/registry.py"
    ]
    
    all_exist = True
    for routing_file in routing_files:
        if os.path.exists(routing_file):
            print(f"✅ {routing_file} exists")
        else:
            print(f"❌ {routing_file} missing")
            all_exist = False
    
    return all_exist

def test_orchestrator_files_exist():
    """Test that all orchestrator files exist"""
    print(f"\n🎼 Testing Orchestrator Files Structure")
    print("=" * 40)
    
    orchestrator_files = [
        "orchestrators/component_orchestrator.py",
        "orchestrators/reasoning_orchestrator.py",
        "orchestrators/expert_orchestrator_langgraph.py",
        "orchestrators/orchestrator_base.py"
    ]
    
    all_exist = True
    for orchestrator_file in orchestrator_files:
        if os.path.exists(orchestrator_file):
            print(f"✅ {orchestrator_file} exists")
        else:
            print(f"❌ {orchestrator_file} missing")
            all_exist = False
    
    return all_exist

def test_workflow_files_exist():
    """Test that all workflow files exist"""
    print(f"\n🔄 Testing Workflow Files Structure")
    print("=" * 35)
    
    workflow_files = [
        "workflows/graph_workflow.py",
        "workflows/graph_nodes.py",
        "workflows/graph_visual.py",
        "workflows/graph_utils.py"
    ]
    
    all_exist = True
    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            print(f"✅ {workflow_file} exists")
        else:
            print(f"❌ {workflow_file} missing")
            all_exist = False
    
    return all_exist

def test_agent_class_definitions():
    """Test that agent classes are properly defined (without importing LLMs)"""
    print(f"\n🔍 Testing Agent Class Definitions")
    print("=" * 40)
    
    try:
        # Test that we can read agent files and find class definitions
        agent_files = [
            ("agents/competition_summary_agent.py", "CompetitionOverviewAgent"),
            ("agents/notebook_explainer_agent.py", "NotebookExplainerAgent"),
            ("agents/discussion_helper_agent.py", "DiscussionHelperAgent"),
            ("agents/error_diagnosis_agent.py", "ErrorDiagnosisAgent"),
            ("agents/base_agent.py", "BaseAgent"),
            ("agents/base_rag_retrieval_agent.py", "BaseRAGRetrievalAgent")
        ]
        
        all_found = True
        for file_path, expected_class in agent_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    if f"class {expected_class}" in content:
                        print(f"✅ {expected_class} found in {file_path}")
                    else:
                        print(f"❌ {expected_class} not found in {file_path}")
                        all_found = False
            else:
                print(f"❌ {file_path} not found")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Agent class definition test failed: {e}")
        return False

def test_routing_structure():
    """Test routing system structure without LLM imports"""
    print(f"\n🎯 Testing Routing System Structure")
    print("=" * 40)
    
    try:
        # Test registry structure
        with open("routing/registry.py", 'r') as f:
            registry_content = f.read()
            
        if "AGENT_CAPABILITY_REGISTRY" in registry_content:
            print("✅ AGENT_CAPABILITY_REGISTRY found in registry.py")
        else:
            print("❌ AGENT_CAPABILITY_REGISTRY not found")
            return False
            
        if "get_agent" in registry_content:
            print("✅ get_agent function found in registry.py")
        else:
            print("❌ get_agent function not found")
            return False
        
        # Test capability scoring structure
        with open("routing/capability_scoring.py", 'r') as f:
            scoring_content = f.read()
            
        if "find_agents_by_subintent" in scoring_content:
            print("✅ find_agents_by_subintent function found")
        else:
            print("❌ find_agents_by_subintent function not found")
            return False
        
        # Test dynamic orchestrator structure
        with open("routing/dynamic_orchestrator.py", 'r') as f:
            orchestrator_content = f.read()
            
        if "DynamicCrossFrameworkOrchestrator" in orchestrator_content:
            print("✅ DynamicCrossFrameworkOrchestrator class found")
        else:
            print("❌ DynamicCrossFrameworkOrchestrator class not found")
            return False
            
        if "InteractionPattern" in orchestrator_content:
            print("✅ InteractionPattern enum found")
        else:
            print("❌ InteractionPattern enum not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Routing structure test failed: {e}")
        return False

def test_orchestrator_structure():
    """Test orchestrator structure without LLM imports"""
    print(f"\n🎼 Testing Orchestrator Structure")
    print("=" * 35)
    
    try:
        # Test component orchestrator
        with open("orchestrators/component_orchestrator.py", 'r') as f:
            component_content = f.read()
            
        if "ComponentOrchestrator" in component_content:
            print("✅ ComponentOrchestrator class found")
        else:
            print("❌ ComponentOrchestrator class not found")
            return False
            
        if "run" in component_content:
            print("✅ run method found in ComponentOrchestrator")
        else:
            print("❌ run method not found")
            return False
        
        # Test reasoning orchestrator
        with open("orchestrators/reasoning_orchestrator.py", 'r') as f:
            reasoning_content = f.read()
            
        if "MultiAgentReasoningOrchestrator" in reasoning_content:
            print("✅ MultiAgentReasoningOrchestrator class found")
        else:
            print("❌ MultiAgentReasoningOrchestrator class not found")
            return False
        
        # Test expert orchestrator
        with open("orchestrators/expert_orchestrator_langgraph.py", 'r') as f:
            expert_content = f.read()
            
        if "ExpertSystemOrchestratorLangGraph" in expert_content:
            print("✅ ExpertSystemOrchestratorLangGraph class found")
        else:
            print("❌ ExpertSystemOrchestratorLangGraph class not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator structure test failed: {e}")
        return False

def test_workflow_structure():
    """Test workflow structure without LLM imports"""
    print(f"\n🔄 Testing Workflow Structure")
    print("=" * 30)
    
    try:
        # Test graph workflow
        with open("workflows/graph_workflow.py", 'r') as f:
            workflow_content = f.read()
            
        if "compiled_graph" in workflow_content:
            print("✅ compiled_graph found in graph_workflow.py")
        else:
            print("❌ compiled_graph not found")
            return False
            
        if "OrchestratorState" in workflow_content:
            print("✅ OrchestratorState found")
        else:
            print("❌ OrchestratorState not found")
            return False
        
        # Test graph nodes
        with open("workflows/graph_nodes.py", 'r') as f:
            nodes_content = f.read()
            
        node_functions = [
            "preprocessing_node",
            "router_node", 
            "competition_summary_node",
            "aggregation_node"
        ]
        
        for node_func in node_functions:
            if f"def {node_func}" in nodes_content:
                print(f"✅ {node_func} function found")
            else:
                print(f"❌ {node_func} function not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow structure test failed: {e}")
        return False

def test_cross_component_integration():
    """Test that components reference each other correctly"""
    print(f"\n🔗 Testing Cross-Component Integration")
    print("=" * 40)
    
    try:
        # Test that component orchestrator references other orchestrators
        with open("orchestrators/component_orchestrator.py", 'r') as f:
            component_content = f.read()
            
        if "DynamicCrossFrameworkOrchestrator" in component_content:
            print("✅ Component orchestrator references dynamic orchestrator")
        else:
            print("❌ Component orchestrator missing dynamic orchestrator reference")
            return False
        
        # Test that dynamic orchestrator references routing components
        with open("routing/dynamic_orchestrator.py", 'r') as f:
            dynamic_content = f.read()
            
        if "parse_user_intent" in dynamic_content:
            print("✅ Dynamic orchestrator references intent router")
        else:
            print("❌ Dynamic orchestrator missing intent router reference")
            return False
        
        # Test that workflows reference orchestrators
        with open("workflows/graph_nodes.py", 'r') as f:
            nodes_content = f.read()
            
        if "ExpertSystemOrchestratorLangGraph" in nodes_content:
            print("✅ Workflow nodes reference expert orchestrator")
        else:
            print("❌ Workflow nodes missing expert orchestrator reference")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cross-component integration test failed: {e}")
        return False

def main():
    """Run all simplified multi-agent system tests"""
    print("🚀 Starting Simplified Multi-Agent System Tests\n")
    
    tests = [
        ("Agent Files Structure", test_agent_files_exist),
        ("Routing Files Structure", test_routing_files_exist),
        ("Orchestrator Files Structure", test_orchestrator_files_exist),
        ("Workflow Files Structure", test_workflow_files_exist),
        ("Agent Class Definitions", test_agent_class_definitions),
        ("Routing System Structure", test_routing_structure),
        ("Orchestrator Structure", test_orchestrator_structure),
        ("Workflow Structure", test_workflow_structure),
        ("Cross-Component Integration", test_cross_component_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append(False)
    
    total_passed = sum(results)
    total_tests = len(results)
    
    print(f"\n📊 Simplified Multi-Agent System Test Results:")
    print(f"📈 Overall Results: {total_passed}/{total_tests} components passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL MULTI-AGENT COMPONENT STRUCTURES ARE CORRECT! Ready for LLM integration.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} component structures need attention before LLM integration.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



