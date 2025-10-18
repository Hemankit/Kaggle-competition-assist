"""
Add handler_used tracking to minimal_backend.py at correct locations
This fixes response labeling to show actual agents instead of fallback_agent
"""

with open('minimal_backend.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Helper function to find line index with pattern
def find_line(pattern):
    for i, line in enumerate(lines):
        if pattern in line:
            return i
    return -1

# 1. Add handler_used after data_section_agent response
data_response_idx = -1
for i, line in enumerate(lines):
    if 'Data information powered by Kaggle API + intelligent scraping + ChromaDB caching' in line and i > 1900:
        data_response_idx = i
        break

if data_response_idx > 0:
    # Insert after response is set
    lines.insert(data_response_idx + 1, '                                # ✅ TRACK: Data section agent handled this\n')
    lines.insert(data_response_idx + 2, '                                handler_used = "data_section_agent"\n')
    print(f"✅ Added handler_used for data_section_agent at line {data_response_idx}")

# 2. Add handler_used after evaluation response
eval_response_idx = -1
for i, line in enumerate(lines):
    if '*Analysis powered by AI agent using competition data from Kaggle.*"""' in line and i < 1700:
        eval_response_idx = i
        break

if eval_response_idx > 0:
    lines.insert(eval_response_idx + 1, '                            # ✅ TRACK: Evaluation agent handled this query\n')
    lines.insert(eval_response_idx + 2, '                            handler_used = "competition_summary_agent"\n')
    print(f"✅ Added handler_used for evaluation at line {eval_response_idx}")

# 3. Add handler_used after simple template evaluation response
eval_template_idx = -1
for i, line in enumerate(lines):
    if '*This information is based on actual competition data from Kaggle API.*"""' in line and 'evaluation' in lines[max(0, i-20):i]:
        eval_template_idx = i
        break

if eval_template_idx > 0:
    lines.insert(eval_template_idx + 1, '                    # ✅ TRACK: Evaluation handler processed this query\n')
    lines.insert(eval_template_idx + 2, '                    handler_used = "competition_summary_agent"\n')
    print(f"✅ Added handler_used for evaluation template at line {eval_template_idx}")

# Write back
with open('minimal_backend.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ All handler_used tracking added successfully!")

