"""
Playwright-based discussion scraper for Kaggle competitions.
Fast, stable, and handles React SPAs effectively.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
import re
import time
from typing import List, Dict, Optional, Any
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup


class DiscussionScraperPlaywright:
    def __init__(self, competition_slug: str, output_dir: str = "data/discussions"):
        """
        Initialize the Playwright-based discussion scraper.
        
        Args:
            competition_slug: Competition identifier (e.g., "google-code-golf-2025")
            output_dir: Directory to save scraped data
        """
        if not isinstance(competition_slug, str) or not competition_slug.strip():
            raise ValueError("competition_slug must be a non-empty string")
        if not isinstance(output_dir, str) or not output_dir.strip():
            raise ValueError("output_dir must be a non-empty string")
        
        self.competition_slug = competition_slug.strip()
        self.output_dir = output_dir
        self.base_url = f"https://www.kaggle.com/competitions/{self.competition_slug}/discussion"
        self.data: List[Dict[str, Any]] = []
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_rendered_html(self) -> str:
        """
        Get fully rendered HTML using Playwright.
        
        Returns:
            Rendered HTML content as string
        """
        print(f"Fetching discussions from: {self.base_url}")
        
        with sync_playwright() as p:
            # Launch browser (headless)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to discussions page
                print("Loading page...")
                page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
                
                # Wait for discussions to load - try multiple selectors
                print("Waiting for discussions to load...")
                try:
                    # Wait for the main discussion list container
                    page.wait_for_selector("ul.km-list", timeout=10000)
                    print("Found discussion list container")
                except PlaywrightTimeoutError:
                    print("Warning: Main container not found, trying alternative selector...")
                    page.wait_for_selector("div[class*='km-listitem']", timeout=5000)
                
                # Scroll to load more discussions
                print("Scrolling to load all discussions...")
                previous_height = page.evaluate("document.body.scrollHeight")
                scroll_attempts = 0
                max_scrolls = 10
                
                while scroll_attempts < max_scrolls:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.5)  # Wait for content to load
                    
                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height == previous_height:
                        break
                    
                    previous_height = new_height
                    scroll_attempts += 1
                
                print(f"Scrolled {scroll_attempts} times")
                
                # Extra wait for any lazy-loaded content
                time.sleep(2)
                
                # Get the fully rendered HTML
                html_content = page.content()
                print(f"Retrieved HTML: {len(html_content)} characters")
                
                return html_content
                
            finally:
                browser.close()
    
    def _parse_discussions(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse discussion data from rendered HTML.
        
        Args:
            html: Rendered HTML content
            
        Returns:
            List of discussion dictionaries
        """
        soup = BeautifulSoup(html, 'html.parser')
        discussions = []
        
        # Find all discussion containers
        # Main discussions are in <div class="km-listitem--medium">
        discussion_containers = soup.find_all('div', class_=lambda c: c and 'km-listitem--medium' in c)
        
        print(f"Found {len(discussion_containers)} discussion containers")
        
        seen_urls = set()  # Deduplicate
        
        for container in discussion_containers:
            try:
                # Find the main discussion link (not comment links)
                main_link = container.find('a', href=re.compile(r'/discussion/\d+$'))
                
                if not main_link:
                    continue
                
                # Get URL and deduplicate
                href = main_link.get('href', '')
                if not href or href in seen_urls:
                    continue
                
                seen_urls.add(href)
                
                # Extract discussion ID from URL
                discussion_id_match = re.search(r'/discussion/(\d+)', href)
                discussion_id = discussion_id_match.group(1) if discussion_id_match else None
                
                # Get full URL
                full_url = f"https://www.kaggle.com{href}" if href.startswith('/') else href
                
                # Extract title (clean up - remove icons and extra text)
                title_text = main_link.get_text(strip=True)
                # Remove common prefixes like "push_pin", "comment", etc.
                title = re.sub(r'^(push_pin|comment)\s*', '', title_text, flags=re.IGNORECASE)
                # Keep [Completed] tag but remove author/date info
                # Split on various separators and take the first meaningful part
                parts = re.split(r'[\u2022\u26f3]|(?<=[a-z])(?=[A-Z][a-z])', title)
                if parts:
                    title = parts[0].strip()
                # Remove trailing author names (capitalized words at the end)
                title = re.sub(r'\s+[A-Z][a-z]+\s+[A-Z]\.?\s*$', '', title).strip()
                
                # Check if pinned
                is_pinned = 'push_pin' in title_text.lower() or 'push_pin' in container.get_text()
                
                # Extract author (usually a link to user profile)
                author = "Unknown"
                # Author links are user profile links (not discussion or comment links)
                all_links = container.find_all('a', href=True)
                for link in all_links:
                    href_attr = link.get('href', '')
                    # Profile links match pattern: /username (single segment, no slashes after)
                    if re.match(r'^/[^/]+$', href_attr) and '/discussion' not in href_attr:
                        author_text = link.get_text(strip=True)
                        # Skip empty or icon text
                        if author_text and len(author_text) > 1 and author_text.lower() not in ['push_pin', 'comment']:
                            author = author_text
                            break
                
                # Extract author rank if present (e.g., "28th in this Competition")
                author_rank = None
                container_text = container.get_text()
                rank_match = re.search(r'(\d+(?:st|nd|rd|th)\s+in\s+this\s+Competition)', container_text)
                if rank_match:
                    author_rank = rank_match.group(1)
                
                # Extract date (look for "Xd/w/m/y ago" or "Last comment...")
                date = "Unknown"
                # Try "Last comment X ago by Author"
                last_comment_match = re.search(r'Last\s*comment\s*(\d+[dhwmy])\s*ago', container_text, re.IGNORECASE)
                if last_comment_match:
                    date = f"Last comment {last_comment_match.group(1)} ago"
                else:
                    # Try standalone date
                    date_match = re.search(r'(\d+[dhwmy])\s*ago', container_text)
                    if date_match:
                        date = f"{date_match.group(1)} ago"
                
                # Extract comment count
                comment_count = 0
                comment_match = re.search(r'(\d+)\s+comment', container_text)
                if comment_match:
                    comment_count = int(comment_match.group(1))
                
                # Extract vote count if visible
                upvotes = None
                vote_match = re.search(r'(\d+)\s+vote', container_text)
                if vote_match:
                    upvotes = int(vote_match.group(1))
                
                # Create discussion object
                discussion = {
                    "discussion_id": discussion_id,
                    "title": title,
                    "author": author,
                    "author_rank": author_rank,
                    "date": date,
                    "url": full_url,
                    "is_pinned": is_pinned,
                    "comment_count": comment_count,
                    "upvotes": upvotes,
                    "content": "",  # Will be filled by deep scraping
                    "comments": [],  # Will be filled by deep scraping
                    "section": "discussion.pinned" if is_pinned else "discussion.unpinned",
                    "competition_slug": self.competition_slug,
                    "last_scraped": self.timestamp,
                    "post_hash": hashlib.sha256(title.encode()).hexdigest(),
                }
                
                discussions.append(discussion)
                
            except Exception as e:
                print(f"Warning: Failed to parse discussion container: {e}")
                continue
        
        return discussions
    
    def scrape(self, max_discussions: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape discussion metadata (titles, authors, links).
        Does NOT fetch full content - that's done via deep scraping.
        
        Args:
            max_discussions: Maximum number of discussions to scrape
            
        Returns:
            List of discussion metadata dictionaries
        """
        print("=" * 60)
        print(f"SCRAPING DISCUSSIONS: {self.competition_slug}")
        print("=" * 60)
        
        try:
            # Get rendered HTML
            html = self._get_rendered_html()
            
            # Parse discussions
            discussions = self._parse_discussions(html)
            
            # Limit to max_discussions
            if max_discussions and len(discussions) > max_discussions:
                print(f"Limiting to {max_discussions} discussions (found {len(discussions)})")
                discussions = discussions[:max_discussions]
            
            self.data = discussions
            
            # Separate pinned and unpinned
            pinned = [d for d in discussions if d['is_pinned']]
            unpinned = [d for d in discussions if not d['is_pinned']]
            
            print("\n" + "=" * 60)
            print("SCRAPING COMPLETE")
            print("=" * 60)
            print(f"Total discussions: {len(discussions)}")
            print(f"  Pinned: {len(pinned)}")
            print(f"  Unpinned: {len(unpinned)}")
            
            return discussions
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape_full_discussion(self, discussion_url: str) -> Dict[str, Any]:
        """
        Deep scrape a specific discussion to get full content, comments, and screenshots.
        
        Args:
            discussion_url: Full URL to the discussion post
            
        Returns:
            Dictionary with full content, comments, and metadata
        """
        print(f"\n[DEEP SCRAPE] Fetching full content from: {discussion_url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to discussion page  
                page.goto(discussion_url, wait_until="networkidle", timeout=30000)
                print("[INFO] Page loaded, waiting for React content...")
                
                # Wait for React content to render - try multiple strategies
                content_loaded = False
                
                # Strategy 1: Wait for h1 (title) to appear
                try:
                    page.wait_for_selector("h1", timeout=10000)
                    content_loaded = True
                    print("[OK] Title loaded")
                except PlaywrightTimeoutError:
                    print("[WARN] Title not found")
                
                # Strategy 2: Wait for text content to indicate page is loaded
                try:
                    page.wait_for_function(
                        "document.body.innerText.length > 2000",
                        timeout=10000
                    )
                    content_loaded = True
                    print("[OK] Content text loaded")
                except PlaywrightTimeoutError:
                    print("[WARN] Insufficient text content")
                
                # Extra wait for any remaining dynamic content
                time.sleep(3)
                print(f"[INFO] Page text length: {page.evaluate('document.body.innerText.length')} chars")
                
                # Get rendered HTML
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract discussion ID from URL
                discussion_id_match = re.search(r'/discussion/(\d+)', discussion_url)
                discussion_id = discussion_id_match.group(1) if discussion_id_match else None
                
                # Extract title - it's the FIRST h3 tag (not h1 which is page title)
                title = "Unknown"
                # Look for all h3 tags, first one is usually the discussion title
                h3_tags = soup.find_all('h3')
                if h3_tags:
                    # First h3 is typically the discussion title
                    title = h3_tags[0].get_text(strip=True)
                
                # Extract main post content - try multiple approaches
                post_content = ""
                has_screenshot = False
                screenshot_urls = []  # Store screenshot URLs for OCR
                
                # Approach 1: Look for markdown divs
                markdown_divs = soup.find_all('div', class_=lambda c: c and 'markdown' in c.lower())
                
                # Approach 2: Look for paragraphs in main content area
                if not markdown_divs:
                    # Try finding main content by looking for paragraphs with substantial text
                    all_paragraphs = soup.find_all(['p', 'pre', 'code', 'blockquote'])
                    if all_paragraphs:
                        post_parts = []
                        for p in all_paragraphs:
                            text = p.get_text(strip=True)
                            if len(text) > 20:  # Meaningful content
                                post_parts.append(text)
                        if post_parts:
                            post_content = "\n\n".join(post_parts)
                            print(f"[INFO] Extracted content from {len(post_parts)} text blocks")
                
                # Approach 3: If markdown divs exist, use them
                elif markdown_divs:
                    main_post = markdown_divs[0]
                    post_content = main_post.get_text(separator="\n", strip=True)
                    
                    # Check for images (screenshots) and extract URLs
                    images = main_post.find_all('img')
                    if images:
                        has_screenshot = True
                        # Extract image URLs for OCR
                        for img in images:
                            img_src = img.get('src', '')
                            if img_src and ('http' in img_src or img_src.startswith('//')):
                                # Make URL absolute if needed
                                if img_src.startswith('//'):
                                    img_src = 'https:' + img_src
                                screenshot_urls.append(img_src)
                        print(f"[INFO] Found {len(images)} images in post ({len(screenshot_urls)} with URLs)")
                
                # Approach 4: Fallback - get all text from body (filtering out navigation)
                if not post_content:
                    body_text = soup.get_text(separator="\n", strip=True)
                    # Filter out common navigation text
                    lines = [l.strip() for l in body_text.split('\n') if l.strip()]
                    # Skip first 50 lines (usually navigation/header)
                    content_lines = [l for l in lines[50:] if len(l) > 30]
                    if content_lines:
                        post_content = "\n\n".join(content_lines[:20])  # Take first 20 meaningful lines
                        print(f"[INFO] Using fallback extraction: {len(content_lines)} lines")
                
                # Check for any images in the page
                if not has_screenshot:
                    all_images = soup.find_all('img', src=lambda s: s and ('kaggle' in s or 'http' in s))
                    # Filter out icons/logos (usually small or in specific paths)
                    content_images = [img for img in all_images if 'logo' not in img.get('src', '').lower() and 'icon' not in img.get('src', '').lower()]
                    if content_images:
                        has_screenshot = True
                        # Extract URLs
                        for img in content_images:
                            img_src = img.get('src', '')
                            if img_src:
                                if img_src.startswith('//'):
                                    img_src = 'https:' + img_src
                                screenshot_urls.append(img_src)
                        print(f"[INFO] Found {len(content_images)} potential screenshots ({len(screenshot_urls)} with URLs)")
                
                # Extract comments - use simple text-based extraction
                # The page text shows comments in a clear pattern we can parse
                comments = []
                
                # Get full page text
                page_text = page.evaluate("document.body.innerText")
                
                # Look for author names from h3 tags (skip first which is title)
                comment_authors = [h3.get_text(strip=True) for h3 in h3_tags[1:]]
                # Remove "X Comments" headers
                comment_authors = [a for a in comment_authors if not ('comment' in a.lower() and any(c.isdigit() for c in a))]
                
                print(f"[INFO] Found {len(comment_authors)} comment authors")
                
                # For each author, extract their comment from the page text
                for i, author in enumerate(comment_authors, 1):
                    try:
                        # Find author's comment in page text
                        author_pos = page_text.find(author)
                        if author_pos == -1:
                            continue
                        
                        # Get text after author name
                        text_after_author = page_text[author_pos + len(author):author_pos + len(author) + 1000]
                        
                        # Skip metadata lines
                        lines = text_after_author.split('\n')
                        content_lines = []
                        
                        for line in lines:
                            line_clean = line.strip()
                            
                            # Stop at next author or end markers
                            if i < len(comment_authors) and comment_authors[i] in line:
                                break
                            if line_clean in ['Please sign in to reply', 'Sign In', 'Register']:
                                break
                            
                            # Skip metadata
                            if any(kw in line_clean.lower() for kw in ['posted', 'ago', 'in this competition', 'topic author', 'arrow_drop_up']):
                                continue
                            
                            # Skip short/empty lines
                            if len(line_clean) < 10:
                                continue
                            
                            # This looks like content
                            content_lines.append(line_clean)
                            
                            # Stop after getting reasonable content
                            if len('\n'.join(content_lines)) > 500:
                                break
                        
                        comment_content = '\n'.join(content_lines)
                        
                        # Accept comments with at least 10 chars (captures short replies like "Thanks!")
                        if len(comment_content) >= 10:
                            comments.append({
                                "author": author,
                                "content": comment_content[:1000],
                                "date": "Unknown",  # Could extract from metadata if needed
                                "has_screenshot": False,  # Would need deeper inspection
                                "position": i
                            })
                    
                    except Exception as e:
                        print(f"[WARN] Failed to parse comment from {author}: {e}")
                        continue
                
                print(f"[INFO] Extracted {len(comments)} comments")
                
                # Build result
                result = {
                    "discussion_id": discussion_id,
                    "title": title,
                    "url": discussion_url,
                    "content": post_content,
                    "has_screenshot": has_screenshot,
                    "screenshot_urls": screenshot_urls,  # For OCR processing
                    "comments": comments,
                    "comment_count": len(comments),
                    "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "content_length": len(post_content),
                    "has_full_content": True
                }
                
                print(f"[SUCCESS] Scraped {len(post_content)} chars of content + {len(comments)} comments")
                return result
                
            except Exception as e:
                print(f"[ERROR] Failed to scrape full discussion: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "discussion_id": None,
                    "title": "Error",
                    "url": discussion_url,
                    "content": "",
                    "has_screenshot": False,
                    "comments": [],
                    "comment_count": 0,
                    "error": str(e),
                    "has_full_content": False
                }
            finally:
                browser.close()
    
    def save_to_json(self) -> str:
        """Save scraped data to JSON file."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(
                self.output_dir,
                f"{self.competition_slug}_discussions.json"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            print(f"\nSaved {len(self.data)} discussions to: {output_path}")
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to save discussions: {e}")
    
    def load_from_json(self) -> List[Dict[str, Any]]:
        """Load previously scraped data from JSON file."""
        output_path = os.path.join(
            self.output_dir,
            f"{self.competition_slug}_discussions.json"
        )
        
        if not os.path.exists(output_path):
            print(f"Warning: File not found: {output_path}")
            return []
        
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            print(f"Loaded {len(self.data)} discussions from: {output_path}")
            return self.data
            
        except Exception as e:
            raise RuntimeError(f"Failed to load discussions: {e}")


# Test/Example usage
if __name__ == "__main__":
    print("Testing Discussion Scraper (Playwright)")
    print("=" * 60)
    
    # Initialize scraper
    scraper = DiscussionScraperPlaywright("google-code-golf-2025")
    
    # Scrape discussions
    discussions = scraper.scrape(max_discussions=20)
    
    # Show sample
    if discussions:
        print("\n" + "=" * 60)
        print("SAMPLE DISCUSSIONS:")
        print("=" * 60)
        
        for i, disc in enumerate(discussions[:3], 1):
            print(f"\n{i}. {disc['title']}")
            print(f"   Author: {disc['author']}" + (f" ({disc['author_rank']})" if disc['author_rank'] else ""))
            print(f"   Date: {disc['date']}")
            print(f"   Pinned: {disc['is_pinned']}")
            print(f"   Comments: {disc['comment_count']}")
            print(f"   URL: {disc['url']}")
        
        # Save to file
        scraper.save_to_json()
    else:
        print("\nNo discussions found!")

