import json
import os
from typing import Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Imports (all Pydantic v2 compatible)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq  # ✅ Now working with 0.3.8
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFacePipeline

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "llm_config.json")

def load_llm_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def load_model_for_task(task_name: str) -> Any:
    config = load_llm_config()
    
    if task_name not in config:
        raise ValueError(f"No configuration found for task '{task_name}' in llm_config.json")

    task_config = config[task_name]
    provider = task_config.get("provider")
    model = task_config.get("model")
    temperature = task_config.get("temperature", 0.3)

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
    
    elif provider == "huggingface":
        # HuggingFace (local or API models)
        return HuggingFacePipeline.from_model_id(
            model_id=model,
            task="text-generation",
            model_kwargs={"temperature": temperature},
            pipeline_kwargs={"max_new_tokens": 1024}
        )

    else:
        raise ValueError(f"Unsupported provider '{provider}' for task '{task_name}'")