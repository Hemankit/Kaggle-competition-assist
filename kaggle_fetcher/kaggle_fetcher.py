"""Handles fetching and storing Kaggle competition data using API client."""

import json
from typing import Union, Dict, List, Any, Optional
from kaggle_api_client import get_notebooks_info, get_leaderboard_info, get_dataset_metadata

JSONtype = Union[Dict[str, Any], List[Any]]

class KaggleFetcher:
    def __init__(self):
        self.notebooks_data: JSONtype = []
        self.leaderboard_data: JSONtype = []

    def fetch_notebooks_with_paging(self, competition_slug: str, page_count: int, page_size: int, filepath: str):
        """
        Fetches multiple pages of notebook metadata from a competition and stores it in a JSON file.

        Args:
            competition_slug (str): Identifier of the competition.
            page_count (int): Number of pages to fetch.
            page_size (int): Number of notebooks per page.
            filepath (str): Path to store the fetched notebook metadata.
        """
        for page in range(1, page_count + 1):
            print(f"Fetching page {page}...")
            page_data = get_notebooks_info(competition_slug, page=page, page_size=page_size)
            if page_data:

                self.notebooks_data.extend(page_data)
            else:
                print("No metadata fetched — check competition slug or page number.")
        try:

            with open(filepath, "w") as f:
                json.dump(self.notebooks_data, f, indent=4)
        except IOError as e:
            print(f"Error writing to file {filepath}: {e}")
        else:
            print(f"Fetched {len(self.notebooks_data)} notebooks from {page_count} pages.")

    def fetch_leaderboard_metadata(self, competition_slug: str, filepath: str):
        """
        Fetches leaderboard data for a competition and stores it in a JSON file.

        Args:
            competition_slug (str): Identifier of the competition.
            filepath (str): Path to store the fetched leaderboard data.
        """
        print(f"Fetching leaderboard for '{competition_slug}'...")
        leaderboard = get_leaderboard_info(competition_slug)
        self.leaderboard_data = leaderboard
        try:
            with open(filepath, "w") as f:
                json.dump(self.leaderboard_data, f, indent=4)
        except IOError as e:
            print(f"Error writing to file {filepath}: {e}")
        else:
            print(f"Fetched leaderboard data for '{competition_slug}' with {len(self.leaderboard_data)} entries.")

    def fetch_dataset_metadata(self, dataset_slug: str, filepath: str):
        """
        Fetches metadata for a specific dataset and stores it in a JSON file.

        Args:
            dataset_slug (str): Identifier of the dataset.
            filepath (str): Path to store the fetched dataset metadata.
        """
        print(f"Fetching dataset metadata for '{dataset_slug}'...")
        dataset_metadata = get_dataset_metadata(dataset_slug)
        try:
            with open(filepath, "w") as f:
                json.dump(dataset_metadata, f, indent=4)
        except IOError as e:
            print(f"Error writing to file {filepath}: {e}")
        else:
            print(f"Fetched dataset metadata for '{dataset_slug}'.")

        


        
        

    
    
        

        


