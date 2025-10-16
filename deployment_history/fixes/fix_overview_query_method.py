#!/usr/bin/env python3
"""Fix the query method call in overview handler"""
import re

print("Fixing overview handler query method...")

# Read file
with open('minimal_backend.py', 'r') as f:
    content = f.read()

# Find and replace the incorrect query call in the overview handler
# It's after "elif response_type == "explanation":" 
# Change chromadb_pipeline.query(...) to chromadb_pipeline.retriever._get_collection().query(...)

# Use regex to find the specific occurrence in the explanation section
old_pattern = r'(elif response_type == "explanation":.*?# Query ChromaDB for overview sections\s+overview_results = )chromadb_pipeline\.query\('

new_text = r'\1chromadb_pipeline.retriever._get_collection().query('

content_new = re.sub(old_pattern, new_text, content, flags=re.DOTALL)

if content != content_new:
    # Backup
    with open('minimal_backend.py.backup_query_fix', 'w') as f:
        f.write(content)
    
    # Write fixed version
    with open('minimal_backend.py', 'w') as f:
        f.write(content_new)
    
    print("✅ Fixed query method call in overview handler")
    print("✅ Created backup: minimal_backend.py.backup_query_fix")
else:
    print("⚠️  Pattern not found - fix may have already been applied or structure changed")


