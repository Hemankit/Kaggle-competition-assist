#!/usr/bin/env python3
"""Improve the overview query to get better sections"""

print("Improving overview query logic...")

with open('minimal_backend.py', 'r') as f:
    content = f.read()

# Find and replace the query section in the overview handler
# Change n_results from 5 to 10 to get more sections

old_query = '''overview_results = chromadb_pipeline.retriever._get_collection().query(
                                query_embeddings=[chromadb_pipeline.retriever.embedding_model.encode(query).tolist()],
                                n_results=5,'''

new_query = '''overview_results = chromadb_pipeline.retriever._get_collection().query(
                                query_embeddings=[chromadb_pipeline.retriever.embedding_model.encode(query).tolist()],
                                n_results=15,  # Get more sections to filter'''

if old_query in content:
    content = content.replace(old_query, new_query)
    print("✅ Changed n_results from 5 to 15")
else:
    print("⚠️  Query pattern not found, trying alternate...")
    # Try without exact spacing
    import re
    pattern = r'(overview_results = chromadb_pipeline\.retriever\._get_collection\(\)\.query\([^)]+\s+n_results=)5,'
    content = re.sub(pattern, r'\g<1>15,  # Get more sections', content)
    print("✅ Used regex to update n_results")

# Now add filtering logic after the query
old_filter = '''if overview_results and overview_results.get('documents') and overview_results['documents'][0]:
                                # Combine relevant overview sections
                                overview_content = "\\n\\n".join(overview_results['documents'][0])
                                print(f"[DEBUG] Found {len(overview_results['documents'][0])} overview sections")'''

new_filter = '''if overview_results and overview_results.get('documents') and overview_results['documents'][0]:
                                # Filter and prioritize sections
                                all_sections = overview_results['documents'][0]
                                metadatas = overview_results.get('metadatas', [[]])[0] if overview_results.get('metadatas') else []
                                
                                # Filter out tiny/useless sections
                                filtered = []
                                exclude_keywords = ['citation', 'tags', 'competition host', 'prizes & awards', 'participation']
                                
                                for i, doc in enumerate(all_sections):
                                    # Skip if too short (< 150 chars) or excluded
                                    if len(doc) < 150:
                                        continue
                                    
                                    # Check metadata title
                                    if metadatas and i < len(metadatas):
                                        title = metadatas[i].get('title', '').lower()
                                        if any(ex in title for ex in exclude_keywords):
                                            continue
                                    
                                    filtered.append(doc)
                                
                                # Prioritize longer sections (more detailed content)
                                filtered = sorted(filtered, key=len, reverse=True)[:5]
                                
                                overview_content = "\\n\\n".join(filtered)
                                print(f"[DEBUG] Filtered to {len(filtered)} relevant sections (from {len(all_sections)} total)")'''

content = content.replace(old_filter, new_filter)
print("✅ Added smart filtering logic")

with open('minimal_backend.py', 'w') as f:
    f.write(content)

print("\n✅ Overview query improved!")
print("   - Fetches 15 results instead of 5")
print("   - Filters out tiny/useless sections")
print("   - Prioritizes longer, more detailed content")


