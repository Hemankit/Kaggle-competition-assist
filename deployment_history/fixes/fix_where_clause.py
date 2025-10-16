#!/usr/bin/env python3
"""Fix ChromaDB where clause in overview handler"""

print("Fixing where clause format...")

# Read file
with open('minimal_backend.py', 'r') as f:
    content = f.read()

# Find and replace the where clause format
# Old: where={"competition_slug": competition_slug, "section": "overview"}
# New: where={"$and": [{"competition_slug": competition_slug}, {"section": "overview"}]}

old_where = '''where={
                                    "competition_slug": competition_slug,
                                    "section": "overview"
                                }'''

new_where = '''where={
                                    "$and": [
                                        {"competition_slug": competition_slug},
                                        {"section": "overview"}
                                    ]
                                }'''

if old_where in content:
    content = content.replace(old_where, new_where)
    
    with open('minimal_backend.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed where clause to use $and operator")
else:
    print("⚠️  Where clause pattern not found")


