from scrapegraphai.graphs import SmartScraperGraph
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def select_urls_from_metadata(metadata: Optional[List[Any]]) -> List[str]:
    """
    Given a list of metadata dicts, extract the 'url' field for each entry.
    """
    if not isinstance(metadata, list) or not metadata:
        logger.warning("Invalid or empty metadata provided to select_urls_from_metadata.")
        return []

    urls = []
    for item in metadata:
        if isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
        else:
            logger.warning(f"Skipping invalid metadata item: {item}")
    return urls


def scrapegraphai_handler(
    query: str,
    mode: str = "summary",
    metadata: Optional[List[Dict[str, Any]]] = None,
    model: str = "codellama:13b",
    base_url: str = "http://localhost:11434"
) -> List[Dict[str, Any]]:
    """
    Runs SmartScraperGraph on a list of URLs extracted from metadata.
    Returns a list of results, one per URL.
    """
    if not metadata:
        logger.error("No metadata provided to scrapegraphai_handler.")
        return []

    url_list = select_urls_from_metadata(metadata)
    if not url_list:
        logger.warning("No valid URLs found in metadata.")
        return []

    results = []
    for url in url_list:
        graph_config = {
            "llm": {
                "type": "ollama",
                "model": model,
                "base_url": base_url,
            },
            "mode": mode,
            "source": url,
        }

        try:
            graph = SmartScraperGraph(
                prompt=query,
                source=url,
                config=graph_config,
            )
            output = graph.run()
            logger.info(f"Output from {url}: {output}")
            results.append({
                "url": url,
                "output": output
            })
        except (ValueError, RuntimeError, OSError) as e:
            logger.error(f"Failed to scrape {url}: {e}")
            results.append({
                "url": url,
                "output": None,
                "error": str(e)
            })
    return results
  