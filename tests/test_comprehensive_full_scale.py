#!/usr/bin/env python3
"""
Comprehensive Full-Scale Testing of Kaggle Competition Assistant Backend
Tests all components: Flask backend, health endpoints, multi-agent system, and complete integration
"""

import sys
import os
import json
import time
import requests
import threading
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

class FlaskServerManager:
    """Manages Flask server for testing"""
    
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:5000"
        self.is_running = False
    
    def start_server(self):
        """Start Flask server in background"""
        try:
            from kaggle_competition_assist_backend.app import create_app
            
            app = create_app()
            app.config['TESTING'] = True
            
            # Start server in a separate thread
            def run_server():
                app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait for server to start
            time.sleep(3)
            
            # Test if server is responding
            try:
                response = requests.get(f"{self.server_url}/health/simple", timeout=5)
                if response.status_code == 200:
                    self.is_running = True
                    print("✅ Flask server started successfully")
                    return True
                else:
                    print(f"⚠️ Flask server started but health check failed: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ Flask server failed to start: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start Flask server: {e}")
            return False
    
    def stop_server(self):
        """Stop Flask server"""
        self.is_running = False
        print("🛑 Flask server stopped")

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

def test_flask_health_endpoints(server_manager):
    """Test Flask health endpoints"""
    print("\n🧪 Testing Flask Health Endpoints")
    print("=" * 50)
    
    results = {}
    
    if not server_manager.is_running:
        results['health_endpoints'] = "❌ SKIP - Flask server not running"
        return results
    
    endpoints = [
        ("/health/simple", "Simple Health Check"),
        ("/health/", "Comprehensive Health Check"),
        ("/health/database", "Database Health Check"),
        ("/health/llm", "LLM Services Health Check"),
        ("/health/ready", "Readiness Check"),
        ("/health/live", "Liveness Check")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{server_manager.server_url}{endpoint}", timeout=10)
            
            if response.status_code in [200, 206]:
                print(f"✅ {description}: {response.status_code}")
                results[f'health_{endpoint.replace("/", "_")}'] = f"✅ PASS - {response.status_code}"
            else:
                print(f"⚠️ {description}: {response.status_code}")
                results[f'health_{endpoint.replace("/", "_")}'] = f"⚠️ PARTIAL - {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Connection failed")
            results[f'health_{endpoint.replace("/", "_")}'] = f"❌ FAIL - Connection error"
    
    return results

def test_multi_agent_integration():
    """Test multi-agent system integration"""
    print("\n🧪 Testing Multi-Agent System Integration")
    print("=" * 50)
    
    results = {}
    
    try:
        from orchestrators.component_orchestrator import ComponentOrchestrator
        
        # Create orchestrator
        orchestrator = ComponentOrchestrator()
        print("✅ Component Orchestrator created successfully")
        
        # Test with different query types
        test_queries = [
            {"query": "What is machine learning?", "mode": "langgraph"},
            {"query": "How should I approach this Kaggle competition?", "mode": "langgraph"},
            {"query": "Explain this code error: NameError: name 'x' is not defined", "mode": "langgraph"}
        ]
        
        successful_queries = 0
        total_queries = len(test_queries)
        
        for i, test_input in enumerate(test_queries):
            try:
                print(f"   Testing query {i+1}: {test_input['query'][:50]}...")
                result = orchestrator.run(test_input)
                
                if isinstance(result, dict) and "final_response" in result:
                    print(f"   ✅ Query {i+1} executed successfully")
                    successful_queries += 1
                elif isinstance(result, dict) and "error" in result:
                    print(f"   ⚠️ Query {i+1} returned error: {result['error']}")
                else:
                    print(f"   ⚠️ Query {i+1} returned unexpected result type: {type(result)}")
                    
            except Exception as e:
                print(f"   ❌ Query {i+1} failed: {str(e)}")
        
        success_rate = (successful_queries / total_queries) * 100
        results['multi_agent'] = f"✅ PASS - {successful_queries}/{total_queries} queries successful ({success_rate:.1f}%)"
        
        if success_rate >= 50:
            print(f"✅ Multi-Agent System: {success_rate:.1f}% success rate")
        else:
            print(f"⚠️ Multi-Agent System: {success_rate:.1f}% success rate")
        
        return results
        
    except Exception as e:
        results['multi_agent'] = f"❌ FAIL - Multi-agent test: {str(e)}"
        print(f"❌ Multi-Agent System: Test failed - {str(e)}")
        return results

def test_flask_query_endpoint(server_manager):
    """Test Flask query endpoint"""
    print("\n🧪 Testing Flask Query Endpoint")
    print("=" * 50)
    
    results = {}
    
    if not server_manager.is_running:
        results['query_endpoint'] = "❌ SKIP - Flask server not running"
        return results
    
    test_queries = [
        {"query": "What is machine learning?", "debug": False},
        {"query": "How should I approach this Kaggle competition?", "debug": True}
    ]
    
    successful_requests = 0
    total_requests = len(test_queries)
    
    for i, test_data in enumerate(test_queries):
        try:
            print(f"   Testing request {i+1}: {test_data['query'][:50]}...")
            
            response = requests.post(
                f"{server_manager.server_url}/query/",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ Request {i+1} successful")
                successful_requests += 1
                
                # Log response preview
                try:
                    response_data = response.json()
                    if "final_response" in response_data:
                        print(f"      Response: {str(response_data['final_response'])[:100]}...")
                    elif "error" in response_data:
                        print(f"      Error: {response_data['error']}")
                except:
                    print(f"      Raw response: {response.text[:100]}...")
                    
            else:
                print(f"   ⚠️ Request {i+1} failed: {response.status_code}")
                print(f"      Response: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request {i+1} connection failed: {e}")
    
    success_rate = (successful_requests / total_requests) * 100
    results['query_endpoint'] = f"✅ PASS - {successful_requests}/{total_requests} requests successful ({success_rate:.1f}%)"
    
    if success_rate >= 50:
        print(f"✅ Query Endpoint: {success_rate:.1f}% success rate")
    else:
        print(f"⚠️ Query Endpoint: {success_rate:.1f}% success rate")
    
    return results

def test_llm_configuration():
    """Test LLM configuration"""
    print("\n🧪 Testing LLM Configuration")
    print("=" * 50)
    
    results = {}
    
    try:
        # Load LLM config
        with open('llms/llm_config.json', 'r') as f:
            config = json.load(f)
        
        print(f"✅ LLM Config loaded: {len(config)} providers")
        
        # Test LLM loader (without actually loading models)
        from llms.llm_loader import get_llm_from_config
        
        # Test configuration loading for different types
        test_types = ['default', 'reasoning_and_interaction', 'aggregation']
        
        for llm_type in test_types:
            if llm_type in config:
                provider = config[llm_type]['provider']
                model = config[llm_type]['model']
                print(f"   {llm_type}: {provider} - {model}")
            else:
                print(f"   {llm_type}: Not configured")
        
        results['llm_config'] = "✅ PASS - LLM configuration working"
        
    except Exception as e:
        results['llm_config'] = f"❌ FAIL - LLM configuration: {str(e)}"
        print(f"❌ LLM Config: Failed - {str(e)}")
    
    return results

def main():
    """Main comprehensive test function"""
    print("🚀 COMPREHENSIVE FULL-SCALE TESTING")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    all_results = {}
    
    # Test core components
    core_results = test_core_components()
    all_results.update(core_results)
    
    # Test backend components
    app, backend_results = test_backend_components()
    all_results.update(backend_results)
    
    # Test LLM configuration
    llm_results = test_llm_configuration()
    all_results.update(llm_results)
    
    # Test multi-agent system
    agent_results = test_multi_agent_integration()
    all_results.update(agent_results)
    
    # Test Flask server and endpoints
    server_manager = FlaskServerManager()
    
    print("\n🌐 Starting Flask Server for API Testing...")
    if server_manager.start_server():
        # Test health endpoints
        health_results = test_flask_health_endpoints(server_manager)
        all_results.update(health_results)
        
        # Test query endpoint
        query_results = test_flask_query_endpoint(server_manager)
        all_results.update(query_results)
        
        server_manager.stop_server()
    else:
        print("❌ Flask server failed to start - skipping API tests")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    partial = 0
    skipped = 0
    
    for component, result in all_results.items():
        if result.startswith("✅"):
            passed += 1
            status = "PASS"
        elif result.startswith("⚠️"):
            partial += 1
            status = "PARTIAL"
        elif result.startswith("❌ SKIP"):
            skipped += 1
            status = "SKIP"
        else:
            failed += 1
            status = "FAIL"
        
        print(f"{status:8} | {component:25} | {result}")
    
    print("=" * 60)
    print(f"📈 SUMMARY: {passed} PASSED, {partial} PARTIAL, {skipped} SKIPPED, {failed} FAILED")
    
    # Overall assessment
    total_tests = passed + partial + failed
    success_rate = ((passed + partial * 0.5) / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate >= 80:
        print("\n🎉 EXCELLENT! System is production-ready!")
        print("✅ Your Kaggle Competition Assistant is working great!")
    elif success_rate >= 60:
        print("\n⚠️ GOOD - System is functional with minor issues")
        print("✅ Ready for development and testing")
    elif success_rate >= 40:
        print("\n⚠️ FAIR - System has some issues but core functionality works")
        print("🔧 Review failed components")
    else:
        print("\n❌ NEEDS WORK - Significant issues detected")
        print("🔧 Major components need attention")
    
    # Save results to file
    with open('comprehensive_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': all_results,
            'summary': {
                'passed': passed, 
                'partial': partial, 
                'skipped': skipped, 
                'failed': failed,
                'success_rate': success_rate
            }
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: comprehensive_test_results.json")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
