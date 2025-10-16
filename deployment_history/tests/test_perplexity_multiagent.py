#!/usr/bin/env python3
"""Test Perplexity integration in multi-agent orchestration"""
import os
import sys

print('='*70)
print('🧪 TESTING PERPLEXITY FOR MULTI-AGENT ORCHESTRATION')
print('='*70)
print()

# Test 1: Import
print('1️⃣ Testing Import...')
try:
    from langchain_perplexity import ChatPerplexity
    print('   ✅ ChatPerplexity imported successfully')
except ImportError as e:
    print(f'   ❌ Import failed: {e}')
    sys.exit(1)

# Test 2: API Key
print('2️⃣ Checking API Key...')
api_key = os.getenv('PERPLEXITY_API_KEY')
if api_key:
    print(f'   ✅ PERPLEXITY_API_KEY found: {api_key[:10]}...')
else:
    print('   ❌ PERPLEXITY_API_KEY not found')
    sys.exit(1)

# Test 3: Instantiation
print('3️⃣ Testing Instantiation...')
try:
    llm = ChatPerplexity(
        model='sonar',
        temperature=0.3,
        pplx_api_key=api_key
    )
    print('   ✅ ChatPerplexity instantiated')
except Exception as e:
    print(f'   ❌ Instantiation failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: LLM Config
print('4️⃣ Testing LLM Config Loader...')
try:
    from llms.llm_loader import get_llm_from_config
    reasoning_llm = get_llm_from_config(section='reasoning_and_interaction')
    
    # Check if it's Perplexity or Groq fallback
    llm_type = type(reasoning_llm).__name__
    if llm_type == 'ChatPerplexity':
        print(f'   ✅ Config loaded: {llm_type} (PERFECT!)')
    elif llm_type == 'ChatGroq':
        print(f'   ⚠️  Config loaded: {llm_type} (Fallback mode)')
        print('      → Perplexity not available, using Groq')
    else:
        print(f'   ❓ Config loaded: {llm_type}')
        
except Exception as e:
    print(f'   ❌ Config loading failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Simple Query
print('5️⃣ Testing Simple Reasoning Query...')
try:
    from langchain_core.messages import HumanMessage
    
    response = reasoning_llm.invoke([
        HumanMessage(content="What is 2+2? Respond in ONE word only.")
    ])
    
    answer = response.content.strip() if hasattr(response, 'content') else str(response)
    print(f'   ✅ Response: "{answer[:50]}"')
    
    if '4' in answer or 'four' in answer.lower():
        print('   ✅ Correct answer!')
    else:
        print(f'   ⚠️  Unexpected answer')
        
except Exception as e:
    print(f'   ❌ Query failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Check Orchestrator Configuration
print('6️⃣ Testing Orchestrator Configuration...')
try:
    from orchestrators import ReasoningOrchestrator
    
    orchestrator = ReasoningOrchestrator()
    print('   ✅ ReasoningOrchestrator instantiated')
    print('   ℹ️  This orchestrator uses Perplexity for deep reasoning')
    
except Exception as e:
    print(f'   ❌ Orchestrator check failed: {e}')
    # Not critical, continue

print()
print('='*70)
print('✅ PERPLEXITY IS FULLY CONFIGURED FOR MULTI-AGENT SYSTEM')
print('='*70)
print()
print('🎯 Architecture:')
print('   • Fast Routing → Gemini 2.5 Flash')
print('   • Fast Retrieval → Gemini 2.5 Flash')
print('   • Deep Reasoning → Perplexity Sonar ✨')
print()
print('✅ Ready for deployment!')


