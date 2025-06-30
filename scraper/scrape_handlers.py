from scrapegraphai.graphs import SmartScraperGraph
import os
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)

def select_urls_from_metadata(metadata: List[Dict[str, Any]]) -> List[str]:
    """
    Given a list of metadata dicts, extract the 'url' field for each entry.
    """
    if not metadata:
        logging.warning("No metadata provided to select_urls_from_metadata.")
        return []
    return [item['url'] for item in metadata if 'url' in item and item['url']]

def scrapegraphai_handler(
    query: str,
    mode: str = "summary",
    metadata: Optional[List[Dict[str, Any]]] = None,
    model: str = "codellama:13b"
) -> List[Dict[str, Any]]:
    """
    Runs SmartScraperGraph on a list of URLs extracted from metadata.
    Returns a list of results, one per URL.
    """
    if metadata is None:
        logging.error("No metadata provided to scrapegraphai_handler.")
        return []

    url_list = select_urls_from_metadata(metadata)
    results = []
    for url in url_list:
        graph_config = {
            "llm": {
            "type": "ollama",
            "model": "codellama:13b",  # or llama3, phi3, etc.
            "base_url": "http://localhost:11434"
            },
            "mode": mode,
            "source": url,
        }

        graph = SmartScraperGraph(
            prompt=query,
            source=url,
            config=graph_config,
        )
        try:
            output = graph.run()
            logging.info(f"Output from {url}:\n{output}\n")
            results.append({
                "url": url,
                "output": output
            })
        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")
            results.append({
                "url": url,
                "output": None,
                "error": str(e)
            })
    return results   