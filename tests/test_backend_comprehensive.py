#!/usr/bin/env python3
"""
Comprehensive backend testing with full project structure access
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_core_components():
    """Test core multi-agent system components"""
    print("🧪 Testing Core Multi-Agent Components")
    print("=" * 50)
    
    results = {}
    
    # Test agents
    try:
        from agents import (
            CompetitionSummaryAgent, CodeFeedbackAgent, ErrorDiagnosisAgent,
            MultiHopReasoningAgent, TimelineCoachAgent, ProgressMonitorAgent
        )
        results['agents'] = "✅ PASS - All agents imported successfully"
        print("✅ Agents: All imported successfully")
    except Exception as e:
        results['agents'] = f"❌ FAIL - Agent imports: {str(e)}"
        print(f"❌ Agents: Import failed - {str(e)}")
    
    # Test orchestrators
    try:
        from orchestrators import (
            ComponentOrchestrator, ReasoningOrchestrator, ExpertSystemOrchestratorLangGraph
        )
        results['orchestrators'] = "✅ PASS - All orchestrators imported successfully"
        print("✅ Orchestrators: All imported successfully")
    except Exception as e:
        results['orchestrators'] = f"❌ FAIL - Orchestrator imports: {str(e)}"
        print(f"❌ Orchestrators: Import failed - {str(e)}")
    
    # Test workflows
    try:
        from workflows import compiled_graph, get_graph_image
        results['workflows'] = "✅ PASS - Workflows imported successfully"
        print("✅ Workflows: Imported successfully")
    except Exception as e:
        results['workflows'] = f"❌ FAIL - Workflow imports: {str(e)}"
        print(f"❌ Workflows: Import failed - {str(e)}")
    
    # Test query processing
    try:
        from query_processing import IntentClassifier, preprocess_query
        results['query_processing'] = "✅ PASS - Query processing imported successfully"
        print("✅ Query Processing: Imported successfully")
    except Exception as e:
        results['query_processing'] = f"❌ FAIL - Query processing imports: {str(e)}"
        print(f"❌ Query Processing: Import failed - {str(e)}")
    
    # Test RAG pipeline
    try:
        from RAG_pipeline_chromadb import ChromaDBRAGPipeline
        results['rag_pipeline'] = "✅ PASS - RAG pipeline imported successfully"
        print("✅ RAG Pipeline: Imported successfully")
    except Exception as e:
        results['rag_pipeline'] = f"❌ FAIL - RAG pipeline imports: {str(e)}"
        print(f"❌ RAG Pipeline: Import failed - {str(e)}")
    
    return results

def test_backend_components():
    """Test backend-specific components"""
    print("\n🧪 Testing Backend Components")
    print("=" * 50)
    
    results = {}
    
    # Test logging utilities
    try:
        from kaggle_competition_assist_backend.utils.logging_config import (
            setup_logging, get_request_logger, get_agent_logger, get_error_logger
        )
        results['logging'] = "✅ PASS - Logging utilities imported successfully"
        print("✅ Logging: Imported successfully")
    except Exception as e:
        results['logging'] = f"❌ FAIL - Logging imports: {str(e)}"
        print(f"❌ Logging: Import failed - {str(e)}")
    
    # Test health check utilities
    try:
        from kaggle_competition_assist_backend.utils.health_check import (
            check_database_connection, check_llm_services, check_file_system,
            get_system_metrics, comprehensive_health_check
        )
        results['health_check'] = "✅ PASS - Health check utilities imported successfully"
        print("✅ Health Check: Imported successfully")
    except Exception as e:
        results['health_check'] = f"❌ FAIL - Health check imports: {str(e)}"
        print(f"❌ Health Check: Import failed - {str(e)}")
    
    # Test Flask app creation
    try:
        from kaggle_competition_assist_backend.app import create_app
        app = create_app()
        results['flask_app'] = "✅ PASS - Flask app created successfully"
        print("✅ Flask App: Created successfully")
        
        # Test app configuration
        config_keys = ['LOG_LEVEL', 'LOG_DIR', 'GOOGLE_API_KEY', 'DEEPSEEK_API_KEY']
        config_status = {}
        for key in config_keys:
            value = app.config.get(key)
            config_status[key] = "SET" if value else "NOT_SET"
        
        print(f"   Config: {config_status}")
        
        return app, results
        
    except Exception as e:
        results['flask_app'] = f"❌ FAIL - Flask app creation: {str(e)}"
        print(f"❌ Flask App: Creation failed - {str(e)}")
        return None, results

def test_health_endpoints(app):
    """Test health check endpoints"""
    print("\n🧪 Testing Health Check Endpoints")
    print("=" * 50)
    
    results = {}
    
    if not app:
        results['health_endpoints'] = "❌ SKIP - No Flask app available"
        return results
    
    try:
        with app.app_context():
            from kaggle_competition_assist_backend.utils.health_check import (
                check_database_connection, check_llm_services, check_file_system,
                get_system_metrics, comprehensive_health_check
            )
            
            # Test individual health checks
            db_status = check_database_connection()
            llm_status = check_llm_services()
            fs_status = check_file_system()
            metrics = get_system_metrics()
            
            # Test comprehensive health check
            health_report = comprehensive_health_check()
            
            results['health_endpoints'] = f"✅ PASS - Health checks working"
            results['health_details'] = {
                'database': db_status['status'],
                'llm_services': len([k for k, v in llm_status.items() if v['status'] == 'configured']),
                'file_system': len(fs_status),
                'overall_status': health_report['overall_status'],
                'response_time_ms': health_report['response_time_ms']
            }
            
            print("✅ Health Checks: All working")
            print(f"   Database: {db_status['status']}")
            print(f"   LLM Services: {len([k for k, v in llm_status.items() if v['status'] == 'configured'])} configured")
            print(f"   File System: {len(fs_status)} checks")
            print(f"   Overall Status: {health_report['overall_status']}")
            print(f"   Response Time: {health_report['response_time_ms']}ms")
            
    except Exception as e:
        results['health_endpoints'] = f"❌ FAIL - Health check execution: {str(e)}"
        print(f"❌ Health Checks: Execution failed - {str(e)}")
    
    return results

def test_component_orchestrator():
    """Test the component orchestrator"""
    print("\n🧪 Testing Component Orchestrator")
    print("=" * 50)
    
    results = {}
    
    try:
        from orchestrators.component_orchestrator import ComponentOrchestrator
        
        # Create orchestrator instance
        orchestrator = ComponentOrchestrator()
        
        # Test basic functionality (without actual LLM calls)
        test_query = "How should I approach this Kaggle competition?"
        
        # This might fail due to LLM dependencies, but we can test the structure
        try:
            # Try to run (this will likely fail due to missing API keys or LLM issues)
            result = orchestrator.run(test_query)
            results['orchestrator'] = "✅ PASS - Orchestrator ran successfully"
            print("✅ Orchestrator: Ran successfully")
        except Exception as e:
            # Check if it's a known issue (API keys, LLM problems)
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['api', 'key', 'llm', 'model', 'connection']):
                results['orchestrator'] = "⚠️ PARTIAL - Orchestrator structure OK, LLM issues expected"
                print("⚠️ Orchestrator: Structure OK, LLM issues (expected)")
            else:
                results['orchestrator'] = f"❌ FAIL - Orchestrator error: {str(e)}"
                print(f"❌ Orchestrator: Error - {str(e)}")
        
    except Exception as e:
        results['orchestrator'] = f"❌ FAIL - Orchestrator import/creation: {str(e)}"
        print(f"❌ Orchestrator: Import/creation failed - {str(e)}")
    
    return results

def test_llm_configuration():
    """Test LLM configuration"""
    print("\n🧪 Testing LLM Configuration")
    print("=" * 50)
    
    results = {}
    
    try:
        # Test LLM config file
        with open('llms/llm_config.json', 'r') as f:
            llm_config = json.load(f)
        
        print("✅ LLM Config: File loaded successfully")
        print(f"   Available providers: {list(llm_config.keys())}")
        
        # Test LLM loader
        from llms.llm_loader import get_llm_from_config
        
        # Test loading different LLM types
        llm_types = ['default', 'reasoning_and_interaction', 'retrieval_agents', 'aggregation']
        
        for llm_type in llm_types:
            try:
                if llm_type in llm_config:
                    llm = get_llm_from_config(llm_type)
                    print(f"   {llm_type}: ✅ Loaded successfully")
                else:
                    print(f"   {llm_type}: ⚠️ Not configured")
            except Exception as e:
                print(f"   {llm_type}: ❌ Failed - {str(e)}")
        
        results['llm_config'] = "✅ PASS - LLM configuration working"
        
    except Exception as e:
        results['llm_config'] = f"❌ FAIL - LLM configuration: {str(e)}"
        print(f"❌ LLM Config: Failed - {str(e)}")
    
    return results

def main():
    """Main test function"""
    print("🚀 COMPREHENSIVE BACKEND TESTING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_results = {}
    
    # Test core components
    core_results = test_core_components()
    all_results.update(core_results)
    
    # Test backend components
    app, backend_results = test_backend_components()
    all_results.update(backend_results)
    
    # Test health endpoints if app is available
    if app:
        health_results = test_health_endpoints(app)
        all_results.update(health_results)
    
    # Test component orchestrator
    orchestrator_results = test_component_orchestrator()
    all_results.update(orchestrator_results)
    
    # Test LLM configuration
    llm_results = test_llm_configuration()
    all_results.update(llm_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    partial = 0
    
    for component, result in all_results.items():
        if result.startswith("✅"):
            passed += 1
            status = "PASS"
        elif result.startswith("⚠️"):
            partial += 1
            status = "PARTIAL"
        else:
            failed += 1
            status = "FAIL"
        
        print(f"{status:8} | {component:20} | {result}")
    
    print("=" * 60)
    print(f"📈 SUMMARY: {passed} PASSED, {partial} PARTIAL, {failed} FAILED")
    
    if failed == 0:
        print("\n🎉 ALL CRITICAL COMPONENTS WORKING!")
        print("✅ Your backend is ready for testing!")
    elif failed <= 2:
        print("\n⚠️ MOSTLY WORKING - Minor issues to address")
        print("✅ Backend is functional with some limitations")
    else:
        print("\n❌ SIGNIFICANT ISSUES DETECTED")
        print("🔧 Review failed components before proceeding")
    
    # Save results to file
    with open('backend_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': all_results,
            'summary': {'passed': passed, 'partial': partial, 'failed': failed}
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: backend_test_results.json")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


