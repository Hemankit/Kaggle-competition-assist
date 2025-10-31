"""Handles fetching and storing Kaggle competition data using API client."""

import json
import math
from typing import Union, Dict, List, Any
from kaggle_api_client import (
    get_notebooks_info,
    get_leaderboard_info,
    get_dataset_metadata,
    get_total_notebooks_count,
)

JSONType = Union[Dict[str, Any], List[Any]]


class KaggleFetcher:
    def __init__(self):
        self.notebooks_data: JSONType = []
        self.leaderboard_data: JSONType = []
        self.dataset_metadata: JSONType = []

    def fetch_notebooks_with_paging(
        self, competition_slug: str, page_count: int, page_size: int, filepath: str
    ):
        """
        Fetches multiple pages of notebook metadata from a competition and stores it in a JSON file.

        Args:
            competition_slug (str): Identifier of the competition.
            page_count (int): Number of pages to fetch.
            page_size (int): Number of notebooks per page.
            filepath (str): Path to store the fetched notebook metadata.
        """
        if not competition_slug or page_count <= 0 or page_size <= 0:
            print("Invalid input parameters for fetching notebooks.")
            return

        for page in range(1, page_count + 1):
            print(f"Fetching page {page}...")
            page_data = get_notebooks_info(
                competition_slug, page=page, page_size=page_size
            )
            if page_data:
                self.notebooks_data.extend(page_data)
            else:
                print("No metadata fetched — check competition slug or page number.")

        try:
            with open(filepath, "w") as f:
                json.dump(self.notebooks_data, f, indent=4)
        except OSError as e:
            print(f"Error writing to file {filepath}: {e}")
        else:
            print(
                f"Fetched {len(self.notebooks_data)} notebooks from {page_count} pages."
            )

    def fetch_all_notebooks(self, competition_slug: str, page_size: int, filepath: str):
        """
        Fetches all public notebooks for a competition and saves to JSON.

        Args:
            competition_slug (str): Identifier of the competition.
            page_size (int): How many notebooks to fetch per page.
            filepath (str): Where to save the collected notebook metadata.
        """
        if not competition_slug or page_size <= 0:
            print("Invalid input parameters for fetching all notebooks.")
            return

        print(f"Checking total notebook count for '{competition_slug}'...")
        total_notebooks = get_total_notebooks_count(competition_slug)
        if not total_notebooks:
            print("No notebooks found or error occurred.")
            return

        page_count = math.ceil(total_notebooks / page_size)
        print(f"Fetching all {total_notebooks} notebooks across {page_count} pages...")

        self.fetch_notebooks_with_paging(
            competition_slug=competition_slug,
            page_count=page_count,
            page_size=page_size,
            filepath=filepath,
        )

    def fetch_leaderboard_metadata(self, competition_slug: str, filepath: str):
        """
        Fetches leaderboard data for a competition and stores it in a JSON file.

        Args:
            competition_slug (str): Identifier of the competition.
            filepath (str): Path to store the fetched leaderboard data.
        """
        if not competition_slug:
            print("Invalid competition slug for leaderboard fetch.")
            return

        print(f"Fetching leaderboard for '{competition_slug}'...")
        leaderboard = get_leaderboard_info(competition_slug)
        if not leaderboard or not isinstance(leaderboard, (list, dict)):
            print("Invalid leaderboard data returned.")
            return

        self.leaderboard_data = leaderboard
        try:
            with open(filepath, "w") as f:
                json.dump(self.leaderboard_data, f, indent=4)
        except OSError as e:
            print(f"Error writing to file {filepath}: {e}")
        else:
            size = len(self.leaderboard_data) if isinstance(self.leaderboard_data, list) else 1
            print(
                f"Fetched leaderboard data for '{competition_slug}' with {size} entries."
            )

    def fetch_dataset_metadata(self, dataset_slug: str, filepath: str):
        """
        Fetches metadata for a specific dataset and stores it in a JSON file.

        Args:
            dataset_slug (str): Identifier of the dataset.
            filepath (str): Path to store the fetched dataset metadata.
        """
        if not dataset_slug:
            print("Invalid dataset slug.")
            return

        print(f"Fetching dataset metadata for '{dataset_slug}'...")
        dataset_metadata = get_dataset_metadata(dataset_slug)
        if not dataset_metadata or not isinstance(dataset_metadata, (dict, list)):
            print("Invalid dataset metadata returned.")
            return

        try:
            with open(filepath, "w") as f:
                json.dump(dataset_metadata, f, indent=4)
        except OSError as e:
            print(f"Error writing to file {filepath}: {e}")
        else:
            print(f"Fetched dataset metadata for '{dataset_slug}'.")

        


        
        

    
    
        

        


