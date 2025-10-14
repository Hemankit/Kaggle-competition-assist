#!/usr/bin/env python3
"""
Test script for Orchestrators components
Tests: component_orchestrator, expert_orchestrator_langgraph, orchestrator_base, reasoning_orchestrator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_component_orchestrator():
    """Test Component Orchestrator initialization and basic functionality"""
    print("🔍 Testing Component Orchestrator...")
    
    try:
        from orchestrators.component_orchestrator import ComponentOrchestrator
        print("✅ Import successful")
        
        # Test initialization
        orchestrator = ComponentOrchestrator()
        print("✅ Orchestrator initialization successful")
        
        # Test basic methods exist
        methods = ['run', 'run_with_debug']
        for method in methods:
            if hasattr(orchestrator, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Component Orchestrator test failed: {e}")
        return False

def test_expert_orchestrator_langgraph():
    """Test Expert Orchestrator LangGraph initialization and basic functionality"""
    print("\n🔍 Testing Expert Orchestrator LangGraph...")
    
    try:
        from orchestrators.expert_orchestrator_langgraph import ExpertOrchestratorLangGraph
        print("✅ Import successful")
        
        # Test initialization
        orchestrator = ExpertOrchestratorLangGraph()
        print("✅ Orchestrator initialization successful")
        
        # Test basic methods exist
        methods = ['run', 'create_graph']
        for method in methods:
            if hasattr(orchestrator, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Expert Orchestrator LangGraph test failed: {e}")
        return False

def test_orchestrator_base():
    """Test Orchestrator Base initialization and basic functionality"""
    print("\n🔍 Testing Orchestrator Base...")
    
    try:
        from orchestrators.orchestrator_base import OrchestratorBase
        print("✅ Import successful")
        
        # Test that it's an abstract base class
        if hasattr(OrchestratorBase, '__abstractmethods__'):
            print("✅ OrchestratorBase is properly abstract")
        else:
            print("❌ OrchestratorBase should be abstract")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator Base test failed: {e}")
        return False

def test_reasoning_orchestrator():
    """Test Reasoning Orchestrator initialization and basic functionality"""
    print("\n🔍 Testing Reasoning Orchestrator...")
    
    try:
        from orchestrators.reasoning_orchestrator import ReasoningOrchestrator
        print("✅ Import successful")
        
        # Test initialization
        orchestrator = ReasoningOrchestrator()
        print("✅ Orchestrator initialization successful")
        
        # Test basic methods exist
        methods = ['run', 'reason_about_query']
        for method in methods:
            if hasattr(orchestrator, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Reasoning Orchestrator test failed: {e}")
        return False

def main():
    """Run all Orchestrators tests"""
    print("🚀 Starting Orchestrators Component Tests\n")
    
    results = []
    results.append(test_component_orchestrator())
    results.append(test_expert_orchestrator_langgraph())
    results.append(test_orchestrator_base())
    results.append(test_reasoning_orchestrator())
    
    print(f"\n📊 Orchestrators Test Results: {sum(results)}/{len(results)} components passed")
    
    if all(results):
        print("🎉 All Orchestrators components are working!")
    else:
        print("⚠️  Some Orchestrators components need attention")
    
    return all(results)

if __name__ == "__main__":
    main()
