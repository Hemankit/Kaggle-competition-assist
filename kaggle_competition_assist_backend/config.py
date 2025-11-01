import os
import json

# Function to load expert guidelines from a JSON file
def load_guidelines():
    with open("data/expert_guidelines.json", "r") as f:
        return json.load(f)
class Config:
    # API keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    # Models for tasks
    DEFAULT_ROUTING_AND_CLASSIFICATION_MODEL = "gemini-2.5-flash"
    DEFAULT_DEEP_SCRAPE_DECISION_MODEL = "mixtral-8x7b-32768"
    DEFAULT_AGENT_REASONING_MODEL = "deepseek-v2.0-chat"
    DEFAULT_AGGREGATION_AND_SUMMARIZATION_MODEL = "microsoft/phi-3-medium-128k-instruct"

    # File paths
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./vector_store/faiss_index")
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    LOG_DIR = os.getenv("LOG_DIR", "./logs")

    # Redis / Cache
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Flask app settings
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "your-default-secret-key")
    ENV = os.getenv("FLASK_ENV", "development")
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.path.join(LOG_DIR, "kaggle_assist.log")

    import json


    EXPERT_GUIDELINES = load_guidelines()

 
 
 
 