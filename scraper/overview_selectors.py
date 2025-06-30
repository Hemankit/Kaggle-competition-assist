"""Contains all CSS/XPath selectors used in overview_scraper.py """
from bs4 import BeautifulSoup, Tag
from typing import Optional, List, Dict, Any
import logging

# selctors for the overview page
SECTION_SELECTOR = "div.main-content section"
TITLE_SELECTOR = "h2"
MARKDOWN_SELECTOR = "div.markdown"
CODE_BLOCK_SELECTOR = "pre"