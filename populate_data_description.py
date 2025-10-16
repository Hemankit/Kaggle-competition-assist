"""
Populate ChromaDB with data description for a competition
"""
from scraper.data_scraper import DataSectionScraper
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
import sys

def populate_data_description(competition_slug: str):
    """Scrape and cache data description in ChromaDB."""
    
    print(f"[INFO] Scraping data description for {competition_slug}...")
    
    # Step 1: Scrape data description
    scraper = DataSectionScraper(competition_slug)
    data = scraper.scrape_data_description()
    
    if not data.get('scraped'):
        print(f"[ERROR] Failed to scrape data description")
        return False
    
    print(f"[INFO] Successfully scraped data description")
    print(f"  - Sections: {len(data['sections'])}")
    print(f"  - Columns: {len(data['column_info'])}")
    
    # Step 2: Initialize ChromaDB pipeline
    print(f"[INFO] Connecting to ChromaDB...")
    rag_pipeline = ChromaDBRAGPipeline(
        collection_name="kaggle_competition_data"
    )
    
    # Step 3: Store sections in ChromaDB
    print(f"[INFO] Storing sections in ChromaDB...")
    
    documents_to_add = []
    
    # Store each section
    for section_title, section_content in data['sections'].items():
        if section_content and len(section_content) > 50:
            documents_to_add.append({
                "content": f"{section_title}\n\n{section_content}",
                "metadata": {
                    "competition_slug": competition_slug,
                    "section": "data_description",
                    "subsection": section_title.lower().replace(" ", "_"),
                    "type": "section"
                }
            })
    
    # Store column information as a combined document
    if data['column_info']:
        column_text = "Data Columns:\n\n"
        for col in data['column_info']:
            column_text += f"- **{col['column']}**: {col['description']}\n"
        
        documents_to_add.append({
            "content": column_text,
            "metadata": {
                "competition_slug": competition_slug,
                "section": "data_description",
                "subsection": "columns",
                "type": "column_info"
            }
        })
    
    # Add all documents to ChromaDB using indexer
    if documents_to_add:
        print(f"[INFO] Adding {len(documents_to_add)} documents to ChromaDB...")
        
        # Prepare chunks with content hash for deduplication
        chunks_to_index = []
        for doc in documents_to_add:
            import hashlib
            content_hash = hashlib.md5(doc['content'].encode()).hexdigest()
            doc['metadata']['content_hash'] = content_hash
            chunks_to_index.append(doc)
        
        # Use indexer to add chunks
        success = rag_pipeline.indexer._index_chunks(chunks_to_index)
        if success:
            print(f"[SUCCESS] Added {len(documents_to_add)} data description documents!")
        else:
            print(f"[ERROR] Failed to index documents")
            return False
    else:
        print(f"[WARN] No documents to add")
    
    return True


if __name__ == "__main__":
    competition = sys.argv[1] if len(sys.argv) > 1 else "titanic"
    
    print("="*70)
    print(f"POPULATE DATA DESCRIPTION: {competition}")
    print("="*70)
    
    success = populate_data_description(competition)
    
    if success:
        print("\n" + "="*70)
        print("SUCCESS - Data description cached in ChromaDB!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("FAILED - Could not populate data description")
        print("="*70)

