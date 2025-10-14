#!/usr/bin/env python3
"""
Test script for Agents components
Tests: base_agent, base_autogen_agent, base_crew_agent, base_rag_retrieval_agent, 
       code_feedback_agent, competition_summary_agent, discussion_helper_agent,
       error_diagnosis_agent, multihop_reasoning_agent, notebook_explainer_agent,
       progress_monitor_agent, timeline_coach_agent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_base_agent():
    """Test Base Agent initialization and basic functionality"""
    print("🔍 Testing Base Agent...")
    
    try:
        from agents.base_agent import BaseAgent
        print("✅ Import successful")
        
        # Test initialization with default parameters
        agent = BaseAgent("TestAgent")
        print("✅ Agent initialization successful")
        
        # Test initialization with all parameters
        agent_full = BaseAgent("TestAgent", "Test description", {"tool1": "value1"})
        print("✅ Full agent initialization successful")
        
        # Test basic methods exist
        methods = ['execute', 'get_tools']
        for method in methods:
            if hasattr(agent, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Base Agent test failed: {e}")
        return False

def test_base_autogen_agent():
    """Test Base AutoGen Agent initialization and basic functionality"""
    print("\n🔍 Testing Base AutoGen Agent...")
    
    try:
        from agents.base_autogen_agent import BaseAutoGenAgent
        print("✅ Import successful")
        
        # Test initialization
        agent = BaseAutoGenAgent("TestAgent", "Test description")
        print("✅ Agent initialization successful")
        
        # Test basic methods exist
        methods = ['create_agent', 'execute']
        for method in methods:
            if hasattr(agent, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Base AutoGen Agent test failed: {e}")
        return False

def test_base_crew_agent():
    """Test Base Crew Agent initialization and basic functionality"""
    print("\n🔍 Testing Base Crew Agent...")
    
    try:
        from agents.base_crew_agent import BaseCrewAgent
        print("✅ Import successful")
        
        # Test initialization
        agent = BaseCrewAgent("TestAgent", "Test description")
        print("✅ Agent initialization successful")
        
        # Test basic methods exist
        methods = ['create_agent', 'execute']
        for method in methods:
            if hasattr(agent, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Base Crew Agent test failed: {e}")
        return False

def test_base_rag_retrieval_agent():
    """Test Base RAG Retrieval Agent initialization and basic functionality"""
    print("\n🔍 Testing Base RAG Retrieval Agent...")
    
    try:
        from agents.base_rag_retrieval_agent import BaseRAGRetrievalAgent
        print("✅ Import successful")
        
        # Test initialization without LLM
        agent = BaseRAGRetrievalAgent("TestAgent", "Test description")
        print("✅ Agent initialization without LLM successful")
        
        # Test basic methods exist
        methods = ['execute', 'retrieve_context']
        for method in methods:
            if hasattr(agent, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Base RAG Retrieval Agent test failed: {e}")
        return False

def test_specialized_agents():
    """Test specialized agents initialization"""
    print("\n🔍 Testing Specialized Agents...")
    
    agents_to_test = [
        ("Code Feedback Agent", "agents.code_feedback_agent", "CodeFeedbackAgent"),
        ("Competition Summary Agent", "agents.competition_summary_agent", "CompetitionSummaryAgent"),
        ("Discussion Helper Agent", "agents.discussion_helper_agent", "DiscussionHelperAgent"),
        ("Error Diagnosis Agent", "agents.error_diagnosis_agent", "ErrorDiagnosisAgent"),
        ("MultiHop Reasoning Agent", "agents.multihop_reasoning_agent", "MultiHopReasoningAgent"),
        ("Notebook Explainer Agent", "agents.notebook_explainer_agent", "NotebookExplainerAgent"),
        ("Progress Monitor Agent", "agents.progress_monitor_agent", "ProgressMonitorAgent"),
        ("Timeline Coach Agent", "agents.timeline_coach_agent", "TimelineCoachAgent")
    ]
    
    results = []
    
    for agent_name, module_path, class_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            
            # Test initialization
            agent = agent_class()
            print(f"✅ {agent_name} initialization successful")
            results.append(True)
            
        except Exception as e:
            print(f"❌ {agent_name} test failed: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Run all Agents tests"""
    print("🚀 Starting Agents Component Tests\n")
    
    results = []
    results.append(test_base_agent())
    results.append(test_base_autogen_agent())
    results.append(test_base_crew_agent())
    results.append(test_base_rag_retrieval_agent())
    results.append(test_specialized_agents())
    
    print(f"\n📊 Agents Test Results: {sum(results)}/{len(results)} components passed")
    
    if all(results):
        print("🎉 All Agents components are working!")
    else:
        print("⚠️  Some Agents components need attention")
    
    return all(results)

if __name__ == "__main__":
    main()
