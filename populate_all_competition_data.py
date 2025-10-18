"""
Master script to populate ALL competition data in ChromaDB
- Overview sections (Playwright)
- Data descriptions (Playwright)
- Top notebooks (API)
- Discussions (Playwright)
"""
import sys
import hashlib
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline

def populate_overview(competition_slug: str, rag_pipeline):
    """Scrape and cache overview sections."""
    print("\n" + "="*70)
    print("1. SCRAPING OVERVIEW SECTIONS")
    print("="*70)
    
    try:
        from scraper.overview_scraper import OverviewScraper
        
        scraper = OverviewScraper(competition_slug)
        overview_data = scraper.scrape()
        
        print(f"[OK] Scraped {len(overview_data['overview_sections'])} overview sections")
        
        # Add each section to ChromaDB
        chunks = []
        for section_title, section_content in overview_data['overview_sections'].items():
            if section_content['text'] and len(section_content['text']) > 50:
                content_hash = hashlib.md5(section_content['text'].encode()).hexdigest()
                chunks.append({
                    "content": f"{section_title}\n\n{section_content['text']}",
                    "metadata": {
                        "competition_slug": competition_slug,
                        "section": "overview",
                        "subsection": section_title.lower().replace(" ", "_"),
                        "type": "overview_section",
                        "content_hash": content_hash
                    }
                })
        
        if chunks:
            rag_pipeline.indexer._index_chunks(chunks)
            print(f"[SUCCESS] Indexed {len(chunks)} overview sections")
        
        return True
    except Exception as e:
        print(f"[ERROR] Overview scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def populate_data_description(competition_slug: str, rag_pipeline):
    """Scrape and cache data descriptions."""
    print("\n" + "="*70)
    print("2. SCRAPING DATA DESCRIPTIONS")
    print("="*70)
    
    try:
        from scraper.data_scraper import DataSectionScraper
        
        scraper = DataSectionScraper(competition_slug)
        data_desc = scraper.scrape_data_description()
        
        print(f"[OK] Scraped {len(data_desc['sections'])} data sections, {len(data_desc['column_info'])} columns")
        
        # Add sections
        chunks = []
        for section_title, section_content in data_desc['sections'].items():
            if section_content and len(section_content) > 50:
                content_hash = hashlib.md5(section_content.encode()).hexdigest()
                chunks.append({
                    "content": f"{section_title}\n\n{section_content}",
                    "metadata": {
                        "competition_slug": competition_slug,
                        "section": "data_description",
                        "subsection": section_title.lower().replace(" ", "_"),
                        "type": "section",
                        "content_hash": content_hash
                    }
                })
        
        # Add column info
        if data_desc['column_info']:
            column_text = "Data Columns:\n\n"
            for col in data_desc['column_info']:
                column_text += f"- **{col['column']}**: {col['description']}\n"
            
            content_hash = hashlib.md5(column_text.encode()).hexdigest()
            chunks.append({
                "content": column_text,
                "metadata": {
                    "competition_slug": competition_slug,
                    "section": "data_description",
                    "subsection": "columns",
                    "type": "column_info",
                    "content_hash": content_hash
                }
            })
        
        if chunks:
            rag_pipeline.indexer._index_chunks(chunks)
            print(f"[SUCCESS] Indexed {len(chunks)} data description chunks")
        
        return True
    except Exception as e:
        print(f"[ERROR] Data description scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def populate_notebooks(competition_slug: str, rag_pipeline):
    """Fetch and cache top notebooks."""
    print("\n" + "="*70)
    print("3. FETCHING TOP NOTEBOOKS (API)")
    print("="*70)
    
    try:
        from scraper.notebook_api_fetcher import NotebookAPIFetcher
        
        fetcher = NotebookAPIFetcher(competition_slug)
        # Fetch metadata only (content download is slow)
        notebook_data = fetcher.fetch(max_pinned=10, max_top_voted=20, min_votes=10, download_content=False)
        
        # Add notebook metadata to ChromaDB
        chunks = []
        for category, notebooks in notebook_data['notebook_categories'].items():
            for notebook in notebooks:
                metadata_obj = notebook['metadata']
                
                # Create text summary of notebook
                text = f"Notebook: {metadata_obj['title']}\n"
                text += f"Author: {metadata_obj['author']}\n"
                text += f"Votes: {metadata_obj['total_votes']}\n"
                text += f"Language: {metadata_obj['language']}\n"
                text += f"URL: {metadata_obj['url']}\n"
                
                content_hash = hashlib.md5(text.encode()).hexdigest()
                chunks.append({
                    "content": text,
                    "metadata": {
                        "competition_slug": competition_slug,
                        "section": "notebooks",
                        "subsection": category,
                        "type": "notebook_metadata",
                        "title": metadata_obj['title'],
                        "author": metadata_obj['author'],
                        "votes": metadata_obj['total_votes'],
                        "content_hash": content_hash
                    }
                })
        
        if chunks:
            rag_pipeline.indexer._index_chunks(chunks)
            print(f"[SUCCESS] Indexed {len(chunks)} notebook entries")
        
        return True
    except Exception as e:
        print(f"[ERROR] Notebook fetching failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def populate_discussions(competition_slug: str, rag_pipeline):
    """Scrape and cache discussions."""
    print("\n" + "="*70)
    print("4. SCRAPING DISCUSSIONS")
    print("="*70)
    
    try:
        from scraper.discussion_scraper_playwright import DiscussionScraperPlaywright
        
        scraper = DiscussionScraperPlaywright(competition_slug)
        discussions = scraper.scrape(max_discussions=30)
        
        print(f"[OK] Scraped {len(discussions)} discussions")
        
        # Add discussion metadata to ChromaDB
        chunks = []
        for disc in discussions:
            text = f"Discussion: {disc['title']}\n"
            text += f"Author: {disc['author']}\n"
            text += f"Date: {disc['date']}\n"
            text += f"Comments: {disc['comment_count']}\n"
            text += f"Pinned: {disc['is_pinned']}\n"
            text += f"URL: {disc['url']}\n"
            
            content_hash = hashlib.md5(text.encode()).hexdigest()
            chunks.append({
                "content": text,
                "metadata": {
                    "competition_slug": competition_slug,
                    "section": "discussions",
                    "subsection": "pinned" if disc['is_pinned'] else "unpinned",
                    "type": "discussion_metadata",
                    "title": disc['title'],
                    "author": disc['author'],
                    "is_pinned": disc['is_pinned'],
                    "content_hash": content_hash
                }
            })
        
        if chunks:
            rag_pipeline.indexer._index_chunks(chunks)
            print(f"[SUCCESS] Indexed {len(chunks)} discussion entries")
        
        return True
    except Exception as e:
        print(f"[ERROR] Discussion scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main(competition_slug: str):
    """Run all scrapers and populate ChromaDB."""
    print("="*70)
    print(f"POPULATING ALL DATA FOR: {competition_slug}")
    print("="*70)
    
    # Initialize ChromaDB with consistent embedding model
    print("\n[INFO] Connecting to ChromaDB...")
    rag_pipeline = ChromaDBRAGPipeline(
        collection_name="kaggle_competition_data",
        embedding_model="all-MiniLM-L6-v2"  # Standard 384-dim model
    )
    
    # Run all scrapers
    results = {
        "overview": populate_overview(competition_slug, rag_pipeline),
        "data_description": populate_data_description(competition_slug, rag_pipeline),
        "notebooks": populate_notebooks(competition_slug, rag_pipeline),
        "discussions": populate_discussions(competition_slug, rag_pipeline)
    }
    
    # Summary
    print("\n" + "="*70)
    print("POPULATION SUMMARY")
    print("="*70)
    for task, success in results.items():
        status = "[OK]" if success else "[FAILED]"
        print(f"{status} {task}")
    
    total = len(results)
    passed = sum(1 for s in results.values() if s)
    
    print(f"\nCompleted: {passed}/{total} tasks successful")
    
    if passed == total:
        print("\n*** ALL DATA POPULATED SUCCESSFULLY! ***")
        print("ChromaDB is now ready with rich competition data!")
    else:
        print(f"\n[WARNING] {total - passed} task(s) failed")
    
    return passed == total

if __name__ == "__main__":
    competition = sys.argv[1] if len(sys.argv) > 1 else "titanic"
    success = main(competition)
    sys.exit(0 if success else 1)


