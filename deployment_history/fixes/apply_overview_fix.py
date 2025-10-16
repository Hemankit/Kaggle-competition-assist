#!/usr/bin/env python3
"""Apply the overview handler fix to minimal_backend.py"""
import shutil

print("Applying overview handler fix...")
print("=" * 70)

# Backup
shutil.copy('minimal_backend.py', 'minimal_backend.py.backup_overview')
print("✅ Created backup: minimal_backend.py.backup_overview")

# Read file
with open('minimal_backend.py', 'r') as f:
    lines = f.readlines()

# The new handler code
new_handler = '''                elif response_type == "explanation":
                    # Handle overview/explanation queries using ChromaDB + Agent
                    print(f"[DEBUG] Handling explanation/overview query for {competition_slug}")
                    
                    if CHROMADB_AVAILABLE and chromadb_pipeline:
                        try:
                            # Query ChromaDB for overview sections
                            overview_results = chromadb_pipeline.query(
                                query_texts=[query],
                                n_results=5,
                                where={
                                    "competition_slug": competition_slug,
                                    "section": "overview"
                                }
                            )
                            
                            if overview_results and overview_results.get('documents') and overview_results['documents'][0]:
                                # Combine relevant overview sections
                                overview_content = "\\n\\n".join(overview_results['documents'][0])
                                print(f"[DEBUG] Found {len(overview_results['documents'][0])} overview sections")
                                
                                # Use CompetitionSummaryAgent for intelligent synthesis
                                if AGENT_AVAILABLE:
                                    try:
                                        llm = get_llm_from_config("default")
                                        agent = CompetitionSummaryAgent(llm=llm)
                                        
                                        # Create mock fetch function to return our overview content
                                        def mock_fetch(query_dict, top_k=5):
                                            return [{"content": overview_content}]
                                        agent.fetch_sections = mock_fetch
                                        
                                        # Run agent analysis
                                        query_dict = {
                                            "cleaned_query": query,
                                            "original_query": query,
                                            "metadata": {
                                                "user_level": "intermediate",
                                                "tone": "helpful",
                                                "competition": competition_name
                                            }
                                        }
                                        
                                        result = agent.run(query_dict)
                                        agent_response = result.get('response', '')
                                        
                                        response = f"""📚 **Competition Overview: {competition_name}**

{agent_response}

---
*Analysis powered by AI using actual competition overview data from Kaggle*"""
                                        
                                    except Exception as agent_error:
                                        print(f"[WARN] Agent failed: {agent_error}, using direct content")
                                        # Fallback: Show overview content directly
                                        response = f"""📚 **Competition Overview: {competition_name}**

{overview_content[:2000]}

---
*This information is from the official competition overview*"""
                                else:
                                    # No agent available, show content directly
                                    response = f"""📚 **Competition Overview: {competition_name}**

{overview_content[:2000]}

---
*This information is from the official competition overview*"""
                            else:
                                print("[DEBUG] No overview data found in ChromaDB")
                                # Fallback to generic if no data
                                response = f"""📚 **Competition Overview: {competition_name}**

**Competition:** {competition_name}
**Participant:** {kaggle_username}

I don't have detailed overview information for this competition yet. Please check the competition page on Kaggle for full details.

**Where to find more information:**
- Competition description on Kaggle
- Discussion forums
- Public notebooks

*Visit: https://www.kaggle.com/competitions/{competition_slug}/overview*"""
                        except Exception as e:
                            print(f"[ERROR] Overview query error: {e}")
                            import traceback
                            traceback.print_exc()
                            response = f"Error retrieving overview: {str(e)}"
                    else:
                        print("[WARN] ChromaDB not available for overview query")
                        response = f"ChromaDB not available. Cannot retrieve overview data."
                
'''

# Find and replace lines 2742-2771 (the old explanation handler)
# Line 2742 is index 2741 (0-indexed)
start_line = 2741  # elif response_type == "explanation":
end_line = 2771    # *This explanation is generated...*"""

# Replace
new_lines = lines[:start_line] + [new_handler] + lines[end_line+1:]

# Write back
with open('minimal_backend.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Applied overview handler fix")
print(f"   Replaced lines {start_line+1}-{end_line+1} with intelligent handler")
print("\n⚠️  Remember to restart the backend to apply changes!")


