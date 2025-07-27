import json
import os
from typing import Any, Optional

# from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain_deepseek import ChatDeepSeek  # Ensure you have this installed if using DeepSeek

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

    if provider == "deepseek":
        return ChatDeepSeek(
            model_name=model,
            temperature=temperature
        )

    elif provider == "google":
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature
        )

    elif provider == "groq":
        return ChatGroq(
            model_name=model,
            temperature=temperature
        )

    elif provider == "ollama":
        return ChatOllama(
            model=model,
            temperature=temperature
        )

    else:
        raise ValueError(f"Unsupported provider '{provider}' for task '{task_name}'")