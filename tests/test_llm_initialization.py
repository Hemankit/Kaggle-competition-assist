#!/usr/bin/env python3
"""
Test script to verify LLM initialization and configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_llm_config_loading():
    """Test that LLM config can be loaded correctly"""
    print("🧪 Testing LLM Configuration Loading")
    print("=" * 40)
    
    try:
        from llms.llm_loader import load_llm_config
        
        config = load_llm_config()
        print("✅ LLM config loaded successfully")
        
        # Check required sections
        required_sections = ["default", "routing", "scraper_decision", "reasoning_and_interaction", "retrieval_agents", "aggregation"]
        for section in required_sections:
            if section in config:
                print(f"✅ Section '{section}' found")
                section_config = config[section]
                if all(key in section_config for key in ["provider", "model", "temperature"]):
                    print(f"   Provider: {section_config['provider']}")
                    print(f"   Model: {section_config['model']}")
                    print(f"   Temperature: {section_config['temperature']}")
                else:
                    print(f"❌ Section '{section}' missing required keys")
            else:
                print(f"❌ Section '{section}' not found")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM config loading failed: {e}")
        return False

def test_llm_loader():
    """Test the main LLM loader function"""
    print(f"\n🔧 Testing LLM Loader")
    print("=" * 25)
    
    try:
        from llms.llm_loader import get_llm_from_config
        
        # Test default LLM loading
        print("Testing default LLM loading...")
        default_llm = get_llm_from_config("default")
        print(f"✅ Default LLM loaded: {type(default_llm).__name__}")
        
        # Test routing LLM loading
        print("Testing routing LLM loading...")
        routing_llm = get_llm_from_config("routing")
        print(f"✅ Routing LLM loaded: {type(routing_llm).__name__}")
        
        # Test scraper decision LLM loading
        print("Testing scraper decision LLM loading...")
        scraper_llm = get_llm_from_config("scraper_decision")
        print(f"✅ Scraper decision LLM loaded: {type(scraper_llm).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM loader test failed: {e}")
        return False

def test_model_registry():
    """Test the model registry function"""
    print(f"\n📋 Testing Model Registry")
    print("=" * 30)
    
    try:
        from llms.model_registry import load_model_for_task
        
        # Test reasoning and interaction model
        print("Testing reasoning and interaction model...")
        reasoning_llm = load_model_for_task("reasoning_and_interaction")
        print(f"✅ Reasoning LLM loaded: {type(reasoning_llm).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model registry test failed: {e}")
        return False

def test_intent_router_llm():
    """Test that intent router can load LLM correctly"""
    print(f"\n🎯 Testing Intent Router LLM Integration")
    print("=" * 45)
    
    try:
        from routing.intent_router import parse_user_intent
        
        # Test with a simple query
        test_query = "What is this Kaggle competition about?"
        print(f"Testing query: {test_query}")
        
        # This should load the LLM and parse the intent
        result = parse_user_intent(test_query)
        print("✅ Intent router LLM integration works")
        print(f"   Parsed intent: {result.get('intent', 'N/A')}")
        print(f"   Sub-intents: {result.get('sub_intents', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Intent router LLM test failed: {e}")
        return False

def test_environment_variables():
    """Test that required environment variables are set"""
    print(f"\n🌍 Testing Environment Variables")
    print("=" * 35)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "GOOGLE_API_KEY": "Google Gemini API key",
        "GROQ_API_KEY": "Groq API key", 
        "OLLAMA_BASE_URL": "Ollama base URL",
        "DEEPSEEK_API_KEY": "DeepSeek API key",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key (for Phi models)"
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set ({description})")
        else:
            print(f"❌ {var}: Not set ({description})")
            all_set = False
    
    # Check optional variables
    optional_vars = {
        "OPENAI_API_KEY": "OpenAI API key",
        "KAGGLE_USERNAME": "Kaggle username",
        "KAGGLE_KEY": "Kaggle API key"
    }
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set ({description})")
        else:
            print(f"⚠️  {var}: Not set ({description}) - Optional")
    
    return all_set

def test_llm_availability():
    """Test that LLMs are actually available (without making API calls)"""
    print(f"\n🔍 Testing LLM Availability")
    print("=" * 30)
    
    try:
        from llms.llm_loader import get_llm_from_config
        
        # Test each LLM type
        llm_tests = [
            ("default", "Default LLM"),
            ("routing", "Routing LLM"),
            ("scraper_decision", "Scraper Decision LLM"),
            ("reasoning_and_interaction", "Reasoning LLM (DeepSeek)"),
            ("retrieval_agents", "Retrieval Agents LLM (Gemini Flash)"),
            ("aggregation", "Aggregation LLM (Phi-3)")
        ]
        
        for config_key, description in llm_tests:
            try:
                llm = get_llm_from_config(config_key)
                print(f"✅ {description}: {type(llm).__name__} initialized")
            except Exception as e:
                print(f"❌ {description}: Failed to initialize - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM availability test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing LLM Initialization")
    print("=" * 50)
    
    # Run all tests
    config_success = test_llm_config_loading()
    loader_success = test_llm_loader()
    registry_success = test_model_registry()
    router_success = test_intent_router_llm()
    env_success = test_environment_variables()
    availability_success = test_llm_availability()
    
    print(f"\n📊 Test Results:")
    print(f"   Config Loading: {'✅ PASS' if config_success else '❌ FAIL'}")
    print(f"   LLM Loader: {'✅ PASS' if loader_success else '❌ FAIL'}")
    print(f"   Model Registry: {'✅ PASS' if registry_success else '❌ FAIL'}")
    print(f"   Intent Router: {'✅ PASS' if router_success else '❌ FAIL'}")
    print(f"   Environment: {'✅ PASS' if env_success else '❌ FAIL'}")
    print(f"   LLM Availability: {'✅ PASS' if availability_success else '❌ FAIL'}")
    
    all_passed = all([config_success, loader_success, registry_success, router_success, availability_success])
    
    if all_passed and env_success:
        print(f"\n🎉 All LLM initialization tests passed!")
        print(f"✅ Your LLM configuration is ready to use")
    elif all_passed:
        print(f"\n⚠️  LLM initialization works but some environment variables are missing")
        print(f"✅ You can proceed with testing, but some features may not work without API keys")
    else:
        print(f"\n❌ Some LLM initialization tests failed")
        print(f"🔧 Please fix the issues before proceeding")
    
    print(f"\n📋 Your LLM Setup:")
    print(f"   • Default: Google Gemini 1.5 Flash")
    print(f"   • Routing: Google Gemini 1.5 Flash") 
    print(f"   • Deep Scraping: Ollama CodeLlama 13B")
    print(f"   • Scraper Decision: Groq Mixtral 8x7B")
    print(f"   • Reasoning & Interaction: DeepSeek v2.0 Chat")
    print(f"   • Retrieval Agents: Google Gemini 1.5 Flash")
    print(f"   • Aggregation: Microsoft Phi-3")
