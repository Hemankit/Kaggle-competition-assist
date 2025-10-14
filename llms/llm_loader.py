import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Imports (all Pydantic v2 compatible)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq  # ✅ Now working with 0.3.8
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFacePipeline
from langchain_community.chat_models import ChatPerplexity  # ✅ Perplexity for reasoning

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "llm_config.json")

def load_llm_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def get_llm_from_config(section: str):
    config = load_llm_config().get(section)
    if not config:
        raise ValueError(f"No LLM config found for section: {section}")

    provider = config.get("provider")
    model = config.get("model")
    temperature = config.get("temperature", 0.2)
    
    # Environment-based override: Use Groq in production instead of Ollama
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production" and provider == "ollama":
        print(f"[PRODUCTION] Overriding Ollama → Groq Mixtral for {section}")
        provider = "groq"
        model = "mixtral-8x7b-32768"

    if provider == "google":
        # Google Gemini (fast, proven)
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return ChatGoogleGenerativeAI(
            model=model, 
            temperature=temperature,
            google_api_key=google_api_key
        )
    
    elif provider == "groq":
        # Groq (fast inference, great for code)
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=groq_api_key
        )
    
    elif provider == "ollama":
        # Ollama (local models, no API key needed)
        return ChatOllama(
            model=model,
            temperature=temperature
        )
    
    elif provider == "deepseek":
        # DeepSeek (strong reasoning)
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if not deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        return ChatDeepSeek(
            model=model,
            temperature=temperature,
            api_key=deepseek_api_key
        )
    
    elif provider == "perplexity":
        # Perplexity (reasoning + search-augmented)
        perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not perplexity_api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
        return ChatPerplexity(
            model=model,
            temperature=temperature,
            pplx_api_key=perplexity_api_key
        )
    
    elif provider == "huggingface":
        # HuggingFace (local or API models)
        return HuggingFacePipeline.from_model_id(
            model_id=model,
            task="text-generation",
            model_kwargs={"temperature": temperature},
            pipeline_kwargs={"max_new_tokens": 1024}
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
