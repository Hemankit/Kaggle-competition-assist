import json
import os
from langchain_community.chat_models import ChatOpenAI, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq  # Only if using groq

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

    if provider == "openai":
        return ChatOpenAI(model_name=model, temperature=temperature)
    elif provider == "ollama":
        return ChatOllama(model=model, temperature=temperature)
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=model, temperature=temperature)
    elif provider == "groq":
        return ChatGroq(model=model, temperature=temperature)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
