"""Uses OCR pipeline to handle screenshots in discussion posts extracting text out of image that informs
agent details of the screenshot.
"""

import os
import re
import requests
import logging
from io import BytesIO
from typing import List, Dict, Optional
from PIL import Image
import pytesseract as pytess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_screenshots(post: dict) -> dict:
    """
    For each discussion post flagged with a screenshot, extract text from images.

    Args:
        post (dict): A single discussion post dictionary.

    Returns:
        dict: The same post dictionary with 'ocr_text' added if screenshots were processed.
    """
    if not post.get("has_screenshot"):
        logger.debug("No screenshot flag set for post titled '%s'", post.get("title", ""))
        return post

    img_urls = re.findall(r'!\[.*?\]\((.*?)\)', post.get("content", ""))
    ocr_texts = []

    for img_url in img_urls:
        try:
            image = download_image(img_url)
            if image:
                logger.info("Performing OCR on image: %s", img_url)
                ocr_text = perform_ocr(image)
                if len(ocr_text) < 10 or re.fullmatch(r'[\W\d\s]*', ocr_text):
                    logger.info("Discarded low-value OCR output from: %s", img_url)
                    continue
                ocr_texts.append(ocr_text)
            else:
                logger.warning("No image returned for URL: %s", img_url)
        except Exception as e:
            logger.error("Error processing image %s: %s", img_url, e)

    post["ocr_text"] = " ".join(ocr_texts).strip() if ocr_texts else ""
    return post




def download_image(img_url: str) -> Optional[Image.Image]:
    """
    Downloads an image from a URL and returns it as a PIL Image.

    Args:
        img_url (str): The URL of the image.

    Returns:
        Image.Image or None: The downloaded image or None if failed.
    """
    try:
        logger.debug("Attempting to download image from: %s", img_url)
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        logger.warning("Failed to download image from %s: %s", img_url, e)
        return None
    except IOError as e:
        logger.warning("Failed to open image from %s: %s", img_url, e)
        return None


def perform_ocr(image: Image.Image) -> str:
    """
    Performs OCR on a PIL Image and returns the extracted text.

    Args:
        image (Image.Image): The image to process.

    Returns:
        str: Extracted text.
    """
    try:
        ocr_text = pytess.image_to_string(image)
        return ocr_text.strip()
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return ""
    
def extract_text_from_posts(posts: List[Dict]) -> List[Dict]:
    """Extracts text from screenshots in discussion posts.
    Args:
        posts (List[Dict]): List of discussion posts."""
    return [extract_text_from_screenshots(post) for post in posts]

    
    