import logging
from scraper.notebook_scraper_v2 import NotebookScraperV2
from scraper.model_scraper_v2 import ModelScraperV2
from scraper.discussion_scraper_v2 import DiscussionScraperV2

logger = logging.getLogger(__name__)

class SectionMetadataLoader:
    def __init__(self):
        self.notebook_scraper = NotebookScraperV2()
        self.model_scraper = ModelScraperV2()
        self.discussion_scraper = DiscussionScraperV2()

    def get_section_metadata(self, section: str):
        """Return metadata depending on section."""
        if section == "code":
            return self.notebook_scraper.get_all_cleaned_notebooks()
        elif section == "discussion":
            return self.discussion_scraper.load_from_json()
        elif section == "model":
            return self.model_scraper.load_from_json()
        else:
            logger.warning(f"No metadata available for unknown section: {section}")
            return []

# Create a global instance and expose the function
_metadata_loader = SectionMetadataLoader()

def get_section_metadata(section: str, item=None):
    """Function interface for get_section_metadata"""
    return _metadata_loader.get_section_metadata(section)