"""Uses OCR pipeline to handle screenshots in discussion posts, extracting text
out of images that inform agent details of the screenshot.
"""

import re
import requests
import logging
from io import BytesIO
from typing import List, Dict, Any, Optional, Union
from PIL import Image
import pytesseract as pytess

# Configure Tesseract path for Windows
pytess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Avoid global logging config at import time — just get a logger
logger = logging.getLogger(__name__)


def extract_text_from_screenshots(post: Dict[str, Any]) -> Dict[str, Any]:
    """
    For each discussion post flagged with a screenshot, extract text from images.

    Args:
        post (Dict[str, Any]): A single discussion post dictionary.
                              Can contain 'screenshot_urls' or extract from markdown 'content'.

    Returns:
        Dict[str, Any]: The same post dictionary with 'ocr_text' added if screenshots were processed.
    """
    if not isinstance(post, dict):
        logger.error("Invalid post type: expected dict, got %s", type(post))
        return {}

    if not post.get("has_screenshot", False):
        logger.debug("No screenshot flag set for post titled '%s'", post.get("title", ""))
        return post

    # Get image URLs - either from screenshot_urls list or from markdown content
    img_urls = post.get("screenshot_urls", [])
    
    if not img_urls:
        # Fallback: extract from markdown content
        content = post.get("content", "")
        if isinstance(content, str):
            img_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
    
    if not img_urls:
        logger.warning("No image URLs found in post")
        return post
    
    ocr_texts: List[str] = []

    for img_url in img_urls:
        if not isinstance(img_url, str) or not img_url.strip():
            logger.warning("Invalid image URL found in post.")
            continue

        try:
            image = download_image(img_url)
            if image:
                logger.info("Performing OCR on image: %s", img_url)
                ocr_text = perform_ocr(image)
                if not isinstance(ocr_text, str):
                    logger.warning("OCR did not return a string for %s", img_url)
                    continue
                if len(ocr_text) < 10 or re.fullmatch(r'^[\W\d\s]*$', ocr_text):
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
        Optional[Image.Image]: The downloaded image or None if failed.
    """
    if not isinstance(img_url, str) or not img_url.strip():
        logger.error("Invalid img_url: expected non-empty string.")
        return None

    try:
        logger.debug("Attempting to download image from: %s", img_url)
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()

        # Safety check for large content size ( >10MB )
        if len(response.content) > 10 * 1024 * 1024:
            logger.error("Image too large to process from URL: %s", img_url)
            return None

        return Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        logger.warning("Failed to download image from %s: %s", img_url, e)
        return None
    except OSError as e:  # replaces deprecated IOError
        logger.warning("Failed to open image from %s: %s", img_url, e)
        return None


def perform_ocr(image: Union[Image.Image, Any]) -> str:
    """
    Performs OCR on a PIL Image and returns the extracted text.

    Args:
        image (Image.Image): The image to process.

    Returns:
        str: Extracted text, or empty string if OCR fails.
    """
    if not isinstance(image, Image.Image):
        logger.error("Invalid image object passed to perform_ocr.")
        return ""

    try:
        ocr_text = pytess.image_to_string(image)
        if not isinstance(ocr_text, str):
            logger.error("OCR returned non-string result.")
            return ""
        return ocr_text.strip()
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return ""


def extract_text_from_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts text from screenshots in multiple discussion posts.

    Args:
        posts (List[Dict[str, Any]]): List of discussion posts.

    Returns:
        List[Dict[str, Any]]: Posts with 'ocr_text' added if applicable.
    """
    if not isinstance(posts, list):
        logger.error("Invalid posts input: expected list, got %s", type(posts))
        return []

    results = []
    for post in posts:
        if not isinstance(post, dict):
            logger.warning("Skipping invalid post of type %s", type(post))
            continue
        results.append(extract_text_from_screenshots(post))
    return results


    
    