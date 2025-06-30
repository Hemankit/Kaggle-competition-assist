import os
import json
import logging
from typing import Dict, Optional, Callable, Any
from scrape_handlers import scrapegraphai_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Import your available scraping handlers here ===
try:
    from scrape_handlers import scrapegraphai_handler  # You can add more
except ImportError as e:
    logger.warning("Handler import failed: %s", e)
    scrapegraphai_handler = None

# Registry of available handlers (mapped by string name)
available_handlers: Dict[str, Callable] = {
    "scrapegraphai_handler": scrapegraphai_handler,
    # Add other handlers as needed
}


class AIScrapeConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()
        self.validate_config()

    def user_query_handler(self, query: str) -> Optional[Callable]:
        """Return a handler function based on user query."""
        if query in self.config:
            return self.config[query].get('handler')
        return None

    def decide_scraping_strategy(self, query: str) -> Optional[Dict[str, Any]]:
        """Decide scraping strategy based on user query."""
        handler = self.user_query_handler(query)
        if handler:
            return {
                'query': query,
                'handler': handler,
                'params': self.config.get(query, {}).get('params', {})
            }
        return None

    def trigger_deep_scraping(self, query: str) -> None:
        """Trigger the AI scraper for intelligent filtering, summarizing, or comparison."""
        strategy = self.decide_scraping_strategy(query)
        if strategy:
            handler = strategy['handler']
            params = strategy['params']
            try:
                handler(**params)
                logger.info("Successfully triggered deep scraping for query: %s", query)
            except Exception as e:
                logger.error("Handler execution failed for query '%s': %s", query, e)
        else:
            logger.warning("No scraping strategy defined for query: %s", query)
            self.suggest_queries(query)

    def suggest_queries(self, query: str) -> None:
        """Suggest similar queries if an exact match isn't found."""
        suggestions = [key for key in self.config if query.lower() in key.lower()]
        if suggestions:
            logger.info("Did you mean one of the following? %s", ', '.join(suggestions))
        else:
            logger.info("No similar queries found for: %s", query)

    def load_config(self) -> None:
        """Load AI scrape configuration from JSON file."""
        logger.info("Loading AI scrape configuration from %s...", self.config_path)
        if not os.path.exists(self.config_path):
            logger.error("Configuration file '%s' not found.", self.config_path)
            return
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON: %s", e)
            return
        except Exception as e:
            logger.error("Unexpected error loading config: %s", e)
            return
        logger.info("AI scrape configuration loaded successfully.")

    def validate_config(self) -> None:
        """Validate and resolve handlers in the config."""
        if not isinstance(self.config, dict):
            logger.error("Configuration should be a dictionary.")
            return

        for key, value in self.config.items():
            if not isinstance(value, dict):
                logger.error("Configuration for '%s' should be a dictionary.", key)
                continue

            handler_name = value.get("handler")
            if not handler_name or not isinstance(handler_name, str):
                logger.error("Missing or invalid handler name for '%s'.", key)
                continue

            resolved_handler = available_handlers.get(handler_name)
            if not resolved_handler:
                logger.error("Handler '%s' for '%s' not found in available handlers.", handler_name, key)
                continue

            self.config[key]["handler"] = resolved_handler
            logger.info("Handler '%s' for '%s' resolved successfully.", handler_name, key)
            if "params" in value and not isinstance(value["params"], dict):
                logger.error("Params for '%s' should be a dictionary.", key)
                continue

        logger.info("AI scrape configuration validated and handlers resolved.")


# Optional manual test code
if __name__ == "__main__":
    config_path = "ai_scrape_config.json"
    ai_scrape_config = AIScrapeConfig(config_path)
    ai_scrape_config.trigger_deep_scraping("example_query")
#                 
    
