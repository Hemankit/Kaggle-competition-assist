#!/usr/bin/env python3
"""Test if Perplexity is available and working"""
import sys
sys.path.insert(0, '.')

print('Testing Perplexity Configuration')
print('='*70)

# Check if Perplexity import works
print('\n[1/3] Checking Perplexity import...')
try:
    from langchain_community.chat_models import ChatPerplexity
    print('✅ ChatPerplexity import successful')
    perplexity_import = True
except ImportError as e:
    print(f'❌ ChatPerplexity import failed: {e}')
    perplexity_import = False

# Check if API key is set
print('\n[2/3] Checking Perplexity API key...')
import os
from dotenv import load_dotenv
load_dotenv()

perplexity_key = os.getenv('PERPLEXITY_API_KEY')
if perplexity_key:
    print(f'✅ PERPLEXITY_API_KEY found: {perplexity_key[:10]}...')
    has_key = True
else:
    print('❌ PERPLEXITY_API_KEY not found')
    has_key = False

# Check if llm_loader uses Perplexity
print('\n[3/3] Checking LLM configuration...')
try:
    from llms.llm_loader import get_llm_from_config, PERPLEXITY_AVAILABLE
    print(f'   PERPLEXITY_AVAILABLE flag: {PERPLEXITY_AVAILABLE}')
    
    if PERPLEXITY_AVAILABLE and has_key:
        print('   Attempting to load Perplexity LLM...')
        try:
            # This will fallback to Groq if Perplexity fails
            llm = get_llm_from_config('reasoning')
            print(f'✅ Reasoning LLM loaded: {type(llm).__name__}')
            
            if 'Perplexity' in type(llm).__name__:
                print('✅ Using Perplexity!')
            elif 'Groq' in type(llm).__name__:
                print('⚠️  Fallback to Groq (Perplexity unavailable)')
            else:
                print(f'⚠️  Using: {type(llm).__name__}')
                
        except Exception as e:
            print(f'❌ Failed to load reasoning LLM: {e}')
    else:
        print('   ⚠️  Perplexity not available, system will use Groq fallback')
        
except Exception as e:
    print(f'❌ Error checking LLM config: {e}')

print()
print('='*70)
print('SUMMARY')
print('='*70)

if perplexity_import and has_key:
    print('✅ Perplexity is properly configured')
    print('   System can use Perplexity for reasoning tasks')
elif has_key:
    print('⚠️  Perplexity API key exists but import failed')
    print('   System will fallback to Groq (this is fine!)')
else:
    print('⚠️  Perplexity not configured')
    print('   System will use Groq fallback (this is fine!)')


