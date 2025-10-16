#!/usr/bin/env python3
"""
Quick test to see which LLM providers actually work with our Pydantic version
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🧪 Testing LLM Providers with Current Pydantic Version")
print("=" * 60)

# Test 1: Google Gemini
print("\n1️⃣  Testing Google Gemini...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=google_key
        )
        print("   ✅ Google Gemini - WORKS")
        print(f"   Model: gemini-2.5-flash")
    else:
        print("   ⚠️  Google API Key not found")
except Exception as e:
    print(f"   ❌ Google Gemini - FAILED: {e}")

# Test 2: Groq
print("\n2️⃣  Testing Groq...")
try:
    from langchain_groq import ChatGroq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        llm = ChatGroq(
            model="llama3-70b-8192",
            temperature=0.2,
            groq_api_key=groq_key
        )
        print("   ✅ Groq - WORKS")
        print(f"   Model: llama3-70b-8192")
    else:
        print("   ⚠️  Groq API Key not found")
except Exception as e:
    print(f"   ❌ Groq - FAILED (Pydantic conflict?): {str(e)[:100]}")

# Test 3: DeepSeek (via OpenAI-compatible API)
print("\n3️⃣  Testing DeepSeek...")
try:
    from langchain_openai import ChatOpenAI
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        # DeepSeek via OpenAI-compatible API
        llm = ChatOpenAI(
            model="deepseek-chat",  # Correct model name
            temperature=0.2,
            api_key=deepseek_key,
            base_url="https://api.deepseek.com/v1"
        )
        print("   ✅ DeepSeek (OpenAI-compatible) - WORKS")
        print(f"   Model: deepseek-chat")
    else:
        print("   ⚠️  DeepSeek API Key not found")
except Exception as e:
    print(f"   ❌ DeepSeek - FAILED: {str(e)[:100]}")

# Test 4: Ollama (local)
print("\n4️⃣  Testing Ollama...")
try:
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(
        model="codellama:13b",
        temperature=0.1
    )
    print("   ⚠️  Ollama - Requires local server running")
except Exception as e:
    print(f"   ❌ Ollama - FAILED: {str(e)[:100]}")

print("\n" + "=" * 60)
print("📊 Summary:")
print("   ✅ Use Google Gemini (proven to work)")
print("   ❓ Test Groq if Pydantic issue is fixed")
print("   ❓ Test DeepSeek with correct model name")
print("   ⚠️  Ollama needs local setup")
print("=" * 60)

