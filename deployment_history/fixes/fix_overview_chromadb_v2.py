#!/usr/bin/env python3
"""Fix overview handler to use correct ChromaDB query method"""

print("Fixing overview ChromaDB query calls...")

# Read file
with open('minimal_backend.py', 'r') as f:
    lines = f.readlines()

# Find the overview handler section (around line 2742+)
# Replace chromadb_pipeline.query with chromadb_pipeline.retriever._get_collection().query

fixed_lines = []
in_overview_handler = False
for i, line in enumerate(lines):
    # Detect start of overview handler
    if 'elif response_type == "explanation":' in line and i > 2700:
        in_overview_handler = True
    
    # Detect end of overview handler (next elif or end of multiagent block)
    if in_overview_handler and ('elif response_type ==' in line and 'explanation' not in line):
        in_overview_handler = False
    
    # Fix the query call
    if in_overview_handler and 'chromadb_pipeline.query(' in line:
        line = line.replace('chromadb_pipeline.query(', 'chromadb_pipeline.retriever._get_collection().query(')
        print(f"  Fixed line {i+1}")
    
    # Also need to fix query_texts to query_embeddings
    if in_overview_handler and 'query_texts=[query]' in line:
        # ChromaDB collection.query uses query_embeddings, not query_texts
        # We need to embed the query first
        line = line.replace('query_texts=[query]', 
                          'query_embeddings=[chromadb_pipeline.retriever.embedding_model.encode(query).tolist()]')
        print(f"  Fixed query_texts to query_embeddings at line {i+1}")
    
    fixed_lines.append(line)

# Write back
with open('minimal_backend.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed overview ChromaDB query calls")


