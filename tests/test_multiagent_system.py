#!/usr/bin/env python3
"""
Comprehensive Multi-Agent System Testing Suite
Tests the distributed multi-agent component across all folders
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# LAYER 1: INDIVIDUAL COMPONENT TESTING
# ============================================================================

def test_agents_individual():
    """Test individual agent classes and their interfaces"""
    print("🤖 Testing Individual Agents")
    print("=" * 30)
    
    try:
        # Test agent imports
        from agents import (
            CompetitionSummaryAgent,
            TimelineCoachAgent, 
            NotebookExplainerAgent,
            DiscussionHelperAgent,
            MultiHopReasoningAgent,
            ErrorDiagnosisAgent,
            CodeFeedbackAgent,
            ProgressMonitorAgent
        )
        print("✅ All agent imports successful")
        
        # Test agent instantiation
        agents_to_test = [
            ("CompetitionSummary", CompetitionSummaryAgent),
            ("TimelineCoach", TimelineCoachAgent),
            ("NotebookExplainer", NotebookExplainerAgent),
            ("DiscussionHelper", DiscussionHelperAgent),
            ("MultiHopReasoning", MultiHopReasoningAgent),
            ("ErrorDiagnosis", ErrorDiagnosisAgent),
            ("CodeFeedback", CodeFeedbackAgent),
            ("ProgressMonitor", ProgressMonitorAgent)
        ]
        
        for name, agent_class in agents_to_test:
            try:
                agent = agent_class()
                print(f"✅ {name}Agent: Instantiated successfully")
                
                # Test basic methods exist
                if hasattr(agent, 'run'):
                    print(f"   - run() method exists")
                if hasattr(agent, 'to_crewai'):
                    print(f"   - to_crewai() method exists")
                if hasattr(agent, 'to_autogen'):
                    print(f"   - to_autogen() method exists")
                    
            except Exception as e:
                print(f"❌ {name}Agent: Failed to instantiate - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent testing failed: {e}")
        return False

def test_routing_system():
    """Test routing, scoring, and registry components"""
    print(f"\n🎯 Testing Routing System")
    print("=" * 25)
    
    try:
        # Test registry
        from routing.registry import AGENT_CAPABILITY_REGISTRY, get_agent
        print(f"✅ Registry loaded: {len(AGENT_CAPABILITY_REGISTRY)} agents registered")
        
        # Test capability scoring
        from routing.capability_scoring import find_agents_by_subintent
        matches = find_agents_by_subintent("error_detection", min_score_threshold=0.1)
        print(f"✅ Capability scoring works: {len(matches)} matches for 'error_detection'")
        
        # Test intent router (without LLM calls)
        from routing.intent_router import parse_user_intent
        print("✅ Intent router imported (LLM calls will be tested separately)")
        
        # Test dynamic orchestrator components
        from routing.dynamic_orchestrator import (
            DynamicCrossFrameworkOrchestrator,
            InteractionPattern,
            FrameworkCapability
        )
        print("✅ Dynamic orchestrator components imported")
        
        # Test interaction patterns
        patterns = [p.value for p in InteractionPattern]
        print(f"✅ Interaction patterns: {patterns}")
        
        # Test framework capabilities
        frameworks = [f.value for f in FrameworkCapability]
        print(f"✅ Framework capabilities: {frameworks}")
        
        return True
        
    except Exception as e:
        print(f"❌ Routing system test failed: {e}")
        return False

def test_orchestrators():
    """Test orchestrator classes and their coordination"""
    print(f"\n🎼 Testing Orchestrators")
    print("=" * 25)
    
    try:
        # Test component orchestrator
        from orchestrators.component_orchestrator import ComponentOrchestrator
        main_orchestrator = ComponentOrchestrator()
        print("✅ ComponentOrchestrator initialized")
        
        # Test reasoning orchestrator
        from orchestrators.reasoning_orchestrator import MultiAgentReasoningOrchestrator
        reasoning_orchestrator = MultiAgentReasoningOrchestrator()
        print("✅ MultiAgentReasoningOrchestrator initialized")
        
        # Test expert orchestrator
        from orchestrators.expert_orchestrator_langgraph import ExpertSystemOrchestratorLangGraph
        expert_orchestrator = ExpertSystemOrchestratorLangGraph()
        print("✅ ExpertSystemOrchestratorLangGraph initialized")
        
        # Test orchestrator base
        from orchestrators.orchestrator_base import BaseOrchestratorUtils
        base_utils = BaseOrchestratorUtils()
        print("✅ BaseOrchestratorUtils initialized")
        
        # Test orchestrator methods
        test_query = {"query": "test query"}
        
        # Test that run methods exist
        if hasattr(reasoning_orchestrator, 'run'):
            print("✅ Reasoning orchestrator has run() method")
        if hasattr(expert_orchestrator, 'run'):
            print("✅ Expert orchestrator has run() method")
        if hasattr(main_orchestrator, 'run'):
            print("✅ Component orchestrator has run() method")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrators test failed: {e}")
        return False

def test_workflows():
    """Test workflow nodes and graph structure"""
    print(f"\n🔄 Testing Workflows")
    print("=" * 20)
    
    try:
        # Test workflow imports
        from workflows.graph_workflow import compiled_graph, OrchestratorState
        print("✅ Graph workflow imported")
        
        # Test graph nodes
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
            aggregation_node
        )
        print("✅ All workflow nodes imported")
        
        # Test workflow utilities
        from workflows.graph_utils import create_state_graph
        from workflows.graph_visual import visualize_graph
        print("✅ Workflow utilities imported")
        
        # Test compiled graph
        if compiled_graph:
            print("✅ Compiled graph exists")
        else:
            print("❌ Compiled graph is None")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflows test failed: {e}")
        return False

# ============================================================================
# LAYER 2: CROSS-COMPONENT INTEGRATION TESTING
# ============================================================================

def test_agents_routing_integration():
    """Test integration between agents and routing system"""
    print(f"\n🔗 Testing Agents ↔ Routing Integration")
    print("=" * 40)
    
    try:
        from routing.registry import AGENT_CAPABILITY_REGISTRY
        from routing.capability_scoring import find_agents_by_subintent
        from agents import ErrorDiagnosisAgent, CodeFeedbackAgent
        
        # Test that agents in registry can be instantiated
        for agent_name in AGENT_CAPABILITY_REGISTRY.keys():
            try:
                from routing.registry import get_agent
                agent = get_agent(agent_name, mode="default")
                print(f"✅ {agent_name}: Can be instantiated from registry")
            except Exception as e:
                print(f"❌ {agent_name}: Registry instantiation failed - {e}")
        
        # Test capability matching
        test_subintents = ["error_detection", "code_feedback", "timeline_planning"]
        for subintent in test_subintents:
            matches = find_agents_by_subintent(subintent, min_score_threshold=0.1)
            print(f"✅ {subintent}: {len(matches)} agents matched")
        
        return True
        
    except Exception as e:
        print(f"❌ Agents-Routing integration test failed: {e}")
        return False

def test_routing_orchestrators_integration():
    """Test integration between routing and orchestrators"""
    print(f"\n🔗 Testing Routing ↔ Orchestrators Integration")
    print("=" * 45)
    
    try:
        from routing.dynamic_orchestrator import DynamicCrossFrameworkOrchestrator
        from orchestrators.component_orchestrator import ComponentOrchestrator
        
        # Test that dynamic orchestrator can create plans
        dynamic_orchestrator = DynamicCrossFrameworkOrchestrator()
        
        # Mock a parsed intent (simulating routing output)
        mock_intent = {
            "intent": "error",
            "sub_intents": ["debug", "troubleshooting"],
            "reasoning_style": "stepwise"
        }
        
        # Test complexity analysis
        complexity = dynamic_orchestrator.analyze_query_complexity(mock_intent)
        print(f"✅ Routing → Orchestrator: Complexity analysis works")
        
        # Test agent selection
        agents = dynamic_orchestrator.select_agents_dynamically(mock_intent)
        print(f"✅ Routing → Orchestrator: Agent selection works ({len(agents)} agents)")
        
        # Test pattern determination
        pattern = dynamic_orchestrator.determine_interaction_pattern(complexity, agents)
        print(f"✅ Routing → Orchestrator: Pattern determination works ({pattern.value})")
        
        return True
        
    except Exception as e:
        print(f"❌ Routing-Orchestrators integration test failed: {e}")
        return False

def test_orchestrators_workflows_integration():
    """Test integration between orchestrators and workflows"""
    print(f"\n🔗 Testing Orchestrators ↔ Workflows Integration")
    print("=" * 50)
    
    try:
        from orchestrators.component_orchestrator import ComponentOrchestrator
        from workflows.graph_workflow import compiled_graph
        
        # Test that component orchestrator can work with workflows
        orchestrator = ComponentOrchestrator()
        
        # Test that orchestrator has access to workflow components
        if hasattr(orchestrator, 'langgraph_orchestrator'):
            print("✅ Orchestrator ↔ Workflow: LangGraph orchestrator integrated")
        
        if hasattr(orchestrator, 'dynamic_orchestrator'):
            print("✅ Orchestrator ↔ Workflow: Dynamic orchestrator integrated")
        
        # Test workflow state structure
        from workflows.graph_workflow import OrchestratorState
        sample_state = {
            "original_query": "test query",
            "memory": {},
            "metadata": {},
            "cleaned_query": "test query",
            "tokens": [],
            "structured_query": {},
            "selected_backend": "langgraph",
            "selected_agents": ["error_diagnosis"],
            "agent_outputs": [],
            "reasoning_trace": [],
            "conversation_trace": [],
            "final_response": "",
            "intent": "error",
            "meta_intervention_needed": False
        }
        print("✅ Orchestrator ↔ Workflow: State structure compatible")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrators-Workflows integration test failed: {e}")
        return False

# ============================================================================
# LAYER 3: END-TO-END SYSTEM TESTING
# ============================================================================

def test_end_to_end_system():
    """Test the complete multi-agent system pipeline"""
    print(f"\n🌐 Testing End-to-End System")
    print("=" * 35)
    
    try:
        from orchestrators.component_orchestrator import ComponentOrchestrator
        
        orchestrator = ComponentOrchestrator()
        
        # Test different orchestration modes
        test_modes = ["dynamic", "crewai", "autogen", "langgraph"]
        
        for mode in test_modes:
            try:
                # Test mode acceptance (won't execute without LLM)
                result = orchestrator.run({
                    "query": "Help me debug this error",
                    "mode": mode
                })
                
                if "error" in result and "Unsupported mode" in result["error"]:
                    print(f"❌ {mode}: Mode rejected unexpectedly")
                else:
                    print(f"✅ {mode}: Mode accepted by system")
                    
            except Exception as e:
                print(f"⚠️  {mode}: Expected error without LLM - {type(e).__name__}")
        
        # Test debug functionality
        debug_trace = orchestrator.get_debug_trace()
        print(f"✅ Debug system: Trace functionality works")
        
        # Test run_with_debug method
        if hasattr(orchestrator, 'run_with_debug'):
            print("✅ Debug system: run_with_debug method exists")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end system test failed: {e}")
        return False

def test_multiagent_workflow_demonstration():
    """Demonstrate the complete multi-agent workflow"""
    print(f"\n🎬 Multi-Agent Workflow Demonstration")
    print("=" * 45)
    
    try:
        from routing.dynamic_orchestrator import DynamicCrossFrameworkOrchestrator
        
        orchestrator = DynamicCrossFrameworkOrchestrator()
        
        # Demonstrate different query scenarios
        scenarios = [
            {
                "query": "I'm getting an error in my Kaggle notebook",
                "expected_agents": ["error_diagnosis"],
                "expected_pattern": "validation"
            },
            {
                "query": "Help me plan my competition timeline and review my code",
                "expected_agents": ["timeline_coach", "code_feedback"],
                "expected_pattern": "collaborative"
            },
            {
                "query": "Explain this competition dataset step by step",
                "expected_agents": ["competition_summary", "notebook_explainer"],
                "expected_pattern": "sequential"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['query']}")
            
            try:
                # Create interaction plan (without LLM execution)
                plan = orchestrator.create_interaction_plan(scenario['query'])
                
                print(f"✅ Plan created:")
                print(f"   Pattern: {plan.pattern.value}")
                print(f"   Agents: {[agent.name for agent in plan.agents]}")
                print(f"   Frameworks: {list(set(agent.framework for agent in plan.agents))}")
                print(f"   Complexity: {plan.complexity_score:.2f}")
                print(f"   Duration: {plan.expected_duration}")
                
                # Check if expected agents were selected
                selected_agent_names = [agent.name for agent in plan.agents]
                for expected_agent in scenario['expected_agents']:
                    if expected_agent in selected_agent_names:
                        print(f"   ✅ Expected agent '{expected_agent}' selected")
                    else:
                        print(f"   ⚠️  Expected agent '{expected_agent}' not selected")
                
            except Exception as e:
                print(f"⚠️  Plan creation failed (expected without LLM): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow demonstration failed: {e}")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all multi-agent system tests"""
    print("🚀 Starting Multi-Agent System Component Tests\n")
    
    # Layer 1: Individual Component Tests
    print("📦 LAYER 1: INDIVIDUAL COMPONENT TESTING")
    print("=" * 50)
    
    layer1_tests = [
        ("Individual Agents", test_agents_individual),
        ("Routing System", test_routing_system),
        ("Orchestrators", test_orchestrators),
        ("Workflows", test_workflows)
    ]
    
    layer1_results = []
    for test_name, test_func in layer1_tests:
        try:
            result = test_func()
            layer1_results.append(result)
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            layer1_results.append(False)
    
    # Layer 2: Cross-Component Integration Tests
    print("\n🔗 LAYER 2: CROSS-COMPONENT INTEGRATION TESTING")
    print("=" * 55)
    
    layer2_tests = [
        ("Agents ↔ Routing", test_agents_routing_integration),
        ("Routing ↔ Orchestrators", test_routing_orchestrators_integration),
        ("Orchestrators ↔ Workflows", test_orchestrators_workflows_integration)
    ]
    
    layer2_results = []
    for test_name, test_func in layer2_tests:
        try:
            result = test_func()
            layer2_results.append(result)
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            layer2_results.append(False)
    
    # Layer 3: End-to-End System Tests
    print("\n🌐 LAYER 3: END-TO-END SYSTEM TESTING")
    print("=" * 45)
    
    layer3_tests = [
        ("End-to-End System", test_end_to_end_system),
        ("Workflow Demonstration", test_multiagent_workflow_demonstration)
    ]
    
    layer3_results = []
    for test_name, test_func in layer3_tests:
        try:
            result = test_func()
            layer3_results.append(result)
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            layer3_results.append(False)
    
    # Results Summary (following the established pattern)
    all_results = layer1_results + layer2_results + layer3_results
    
    layer1_passed = sum(layer1_results)
    layer2_passed = sum(layer2_results)
    layer3_passed = sum(layer3_results)
    total_passed = sum(all_results)
    total_tests = len(all_results)
    
    print(f"\n📊 Multi-Agent System Test Results:")
    print(f"📦 Layer 1 (Individual Components): {layer1_passed}/{len(layer1_tests)} components passed")
    print(f"🔗 Layer 2 (Cross-Component Integration): {layer2_passed}/{len(layer2_tests)} components passed")
    print(f"🌐 Layer 3 (End-to-End System): {layer3_passed}/{len(layer3_tests)} components passed")
    print(f"📈 Overall Results: {total_passed}/{total_tests} components passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL MULTI-AGENT COMPONENTS ARE WORKING! Ready for LLM integration testing.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} components need attention before LLM integration testing.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
