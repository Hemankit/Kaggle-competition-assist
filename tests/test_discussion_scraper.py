"""
Test script for discussion scraper on google-code-golf-2025
"""

import json
from scraper.discussion_scraper_v2 import DiscussionScraperV2

def test_basic_scraping():
    """Test basic discussion scraping without deep scraping"""
    print("=" * 60)
    print("TESTING DISCUSSION SCRAPER - BASIC MODE")
    print("=" * 60)
    
    # Initialize scraper
    competition = "google-code-golf-2025"
    scraper = DiscussionScraperV2(
        input_link=competition,
        output_dir="data/discussions"
    )
    
    print(f"\n[1/3] Initialized scraper for: {competition}")
    print(f"      Base URL: {scraper.base_url}")
    
    # Scrape discussions (without OCR for speed)
    print(f"\n[2/3] Starting to scrape discussions...")
    print("      (This may take 2-3 minutes)")
    
    try:
        discussions = scraper.scrape(retries=2, apply_ocr=False)
        
        print(f"\n[3/3] Scraping complete!")
        print(f"      Total discussions found: {len(discussions)}")
        
        # Analyze what we got
        if discussions:
            print("\n" + "=" * 60)
            print("DATA ANALYSIS")
            print("=" * 60)
            
            # Count pinned vs unpinned
            pinned = [d for d in discussions if d.get('is_pinned')]
            unpinned = [d for d in discussions if not d.get('is_pinned')]
            
            print(f"\nPinned discussions: {len(pinned)}")
            print(f"Unpinned discussions: {len(unpinned)}")
            
            # Show first discussion structure
            print("\n" + "-" * 60)
            print("SAMPLE DISCUSSION STRUCTURE:")
            print("-" * 60)
            sample = discussions[0]
            print(f"Title: {sample.get('title', 'N/A')}")
            print(f"Author: {sample.get('author', 'N/A')}")
            print(f"Date: {sample.get('date', 'N/A')}")
            print(f"Content length: {len(sample.get('content', ''))} chars")
            print(f"Is pinned: {sample.get('is_pinned', False)}")
            print(f"Has screenshot: {sample.get('has_screenshot', False)}")
            print(f"Markdown blocks: {len(sample.get('markdown_blocks', []))}")
            
            print("\nContent preview (first 300 chars):")
            content = sample.get('content', '')[:300]
            print(f"{content}...")
            
            # Check what fields we're getting
            print("\n" + "-" * 60)
            print("AVAILABLE FIELDS:")
            print("-" * 60)
            fields = list(sample.keys())
            for field in sorted(fields):
                value = sample.get(field)
                if isinstance(value, str):
                    print(f"  {field}: <string> ({len(value)} chars)")
                elif isinstance(value, list):
                    print(f"  {field}: <list> ({len(value)} items)")
                else:
                    print(f"  {field}: {type(value).__name__}")
            
            # Show a pinned discussion if exists
            if pinned:
                print("\n" + "-" * 60)
                print("SAMPLE PINNED DISCUSSION:")
                print("-" * 60)
                pinned_sample = pinned[0]
                print(f"Title: {pinned_sample.get('title', 'N/A')}")
                print(f"Author: {pinned_sample.get('author', 'N/A')}")
                print(f"Content preview: {pinned_sample.get('content', '')[:200]}...")
            
            # Save to JSON for inspection
            output_path = scraper.save_to_json()
            print(f"\n[SAVED] Full data saved to: {output_path}")
            
            # Check for missing fields
            print("\n" + "=" * 60)
            print("MISSING FIELDS CHECK:")
            print("=" * 60)
            missing = []
            if not sample.get('upvotes'):
                missing.append("upvotes (currently None)")
            if 'comments' not in sample:
                missing.append("comments (not extracted)")
            if 'author_rank' not in sample:
                missing.append("author_rank (not extracted)")
            if 'url' not in sample:
                missing.append("discussion_url (not extracted)")
            if 'comment_count' not in sample:
                missing.append("comment_count (not extracted)")
            
            if missing:
                print("\nFields we need to add:")
                for field in missing:
                    print(f"  - {field}")
            else:
                print("\nAll desired fields present!")
            
        else:
            print("\n[WARNING] No discussions found!")
            print("This could mean:")
            print("  1. The competition has no discussions")
            print("  2. Kaggle changed their HTML structure")
            print("  3. Selenium selectors need updating")
        
    except Exception as e:
        print(f"\n[ERROR] Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_basic_scraping()
    
    if success:
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Review the output above")
        print("  2. Check data/discussions/google-code-golf-2025_discussions.json")
        print("  3. Decide what enhancements are needed")
    else:
        print("\n" + "=" * 60)
        print("TEST FAILED")
        print("=" * 60)
        print("\nCheck the error messages above")


