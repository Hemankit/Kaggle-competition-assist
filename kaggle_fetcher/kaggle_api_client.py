"""Contains utility functions to interact with Kaggle API for downloading data, fetching notebooks, 
and accessing the leaderboard."""


from kaggle.api.kaggle_api_extended import KaggleApi
import time
from urllib.error import HTTPError
"""
    This function interacts with the Kaggle API to perform various tasks such as downloading datasets, 
    fetching notebooks, and accessing the leaderboard.
    """
def interact_with_kaggle_api(func):
    def wrapper(*args, **kwargs):
        print("Making Kaggle API call...")
        # Initialize the Kaggle API
        api = KaggleApi()
        api.authenticate()
        result = func(api, *args, **kwargs)
        print("data fetched successfully...")
        return result
    return wrapper

# Fetch public notebooks for a competition
@interact_with_kaggle_api
def get_notebooks_info(api, competition_slug: str, page: int = 1, page_size: int = 20, max_retries: int = 3, backoff_factor: float = 1.5):
    """
    Fetches public notebooks for the given competition with retry logic.

    Args:
        api: KaggleApi instance (injected by decorator).
        competition_slug (str): The competition slug.
        page (int): Page number.
        page_size (int): Number of notebooks per page.
        max_retries (int): Maximum number of retry attempts.
        backoff_factor (float): Multiplier for exponential backoff.

    Returns:
        List of dictionaries containing notebook metadata.
    """
    for attempt in range(max_retries):
        try:
            results = api.kernels_list(competition=competition_slug, page=page, page_size=page_size)
            return results
        except HTTPError as e:
            print(f"HTTPError on page {page}: {e}. Retrying ({attempt + 1}/{max_retries})...")
        except Exception as e:
            print(f"Error fetching notebooks on page {page}: {e}. Retrying ({attempt + 1}/{max_retries})...")

        # Wait before retrying
        sleep_time = backoff_factor * (2 ** attempt)
        time.sleep(sleep_time)

    print(f"Failed to fetch notebooks after {max_retries} attempts.")
    return []

# Fetch top leaderboard entries (up to top 50 only)
@interact_with_kaggle_api
def get_leaderboard_info(api, competition_slug: str):
    """
    Fetches the top leaderboard entries for the given competition (max 50 entries).

    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): The Kaggle competition identifier.

    Returns:
        List of leaderboard entries (dicts).
    """
    try:
        results = api.competition_leaderboard(competition=competition_slug, max_results=50)
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []
    return results
# Fetch dataset metadata
@interact_with_kaggle_api
def get_dataset_metadata(api, dataset_slug: str):
    """
    Fetches metadata for a specific dataset.

    Args:
        api: KaggleApi instance (injected by the decorator).
        dataset_slug (str): The Kaggle dataset identifier.

    Returns:
        Dictionary containing dataset metadata.
    """
    try:
        results = api.dataset_view(dataset_slug)
    except Exception as e:
        print(f"Error fetching dataset metadata: {e}")
        return {}
    return results

# Fetch total number of notebooks for a competition
@interact_with_kaggle_api
def get_total_notebooks_count(api, competition_slug: str) -> int:
    """
    Gets the total number of public notebooks for a competition.

    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): Identifier of the competition.

    Returns:
        int: Total number of notebooks.
    """
    try:
        results = api.kernels_list(competition=competition_slug, page=1, page_size=1)
        return results.totalCount if hasattr(results, 'totalCount') else len(results)
    except Exception as e:
        print(f"Error fetching total notebook count: {e}")
        return 0

