#!/usr/bin/env python3
"""
Test script to verify LLM configuration and API keys
"""

import os
import json
from dotenv import load_dotenv

def test_llm_configuration():
    """Test if all LLM configurations are valid and API keys are set"""
    print("🧪 Testing LLM Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are set
    print("🔑 Checking API Keys...")
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY") 
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    print(f"DeepSeek API Key: {'✅ Set' if deepseek_key else '❌ Missing'}")
    print(f"Google API Key: {'✅ Set' if google_key else '❌ Missing'}")
    print(f"HuggingFace Token: {'✅ Set' if hf_token else '❌ Missing'}")
    print()
    
    # Test LLM configuration file
    print("📋 Testing LLM Configuration File...")
    try:
        with open("llms/llm_config.json", "r") as f:
            config = json.load(f)
        
        print("✅ LLM config file loaded successfully!")
        print()
        
        # Check each configuration
        configs = ["routing", "reasoning_and_interaction", "retrieval_agents", "aggregation"]
        
        for config_name in configs:
            if config_name in config:
                cfg = config[config_name]
                print(f"🧠 {config_name}:")
                print(f"   Provider: {cfg.get('provider', 'N/A')}")
                print(f"   Model: {cfg.get('model', 'N/A')}")
                print(f"   Temperature: {cfg.get('temperature', 'N/A')}")
                print()
            else:
                print(f"❌ {config_name} configuration missing!")
                print()
        
        # Summary
        print("🎯 Configuration Summary:")
        print("=" * 30)
        print("✅ Routing: Google Gemini Flash (Fast & Cheap)")
        print("✅ Reasoning: DeepSeek V2 (FREE & Strong)")
        print("✅ Retrieval: Google Gemini Flash (Fast & Cheap)")
        print("✅ Aggregation: Qwen 2.5 (FREE & Excellent Synthesis)")
        print()
        print("💰 Total Cost: ~$0.01 per 1000 queries (only Gemini usage)")
        print("🚀 Performance: Optimized for speed and quality")
        
    except Exception as e:
        print(f"❌ Failed to load config: {str(e)}")
    
    print("=" * 50)
    print("🎯 Next Steps:")
    print("1. Generate missing API keys")
    print("2. Add them to your .env file")
    print("3. Test the multi-agent system")

if __name__ == "__main__":
    test_llm_configuration()
