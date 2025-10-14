"""Quick cache debug test - just 2 queries to see metadata"""
import requests
import time

BACKEND_URL = "http://localhost:5000"

print("\n" + "=" * 80)
print("CACHE DEBUG TEST")
print("=" * 80)
print("Running 2 queries to debug cache metadata matching...")
print("=" * 80 + "\n")

# Query 1: Store data
print("[1] First query - storing data...")
query1 = "Explain the evaluation metric for google-code-golf-2025"
user_context = {
    "kaggle_username": "TestUser",
    "competition_slug": "google-code-golf-2025",
    "competition_name": "NeurIPS 2025 - Google Code Golf Championship"
}

start1 = time.time()
response1 = requests.post(
    f"{BACKEND_URL}/component-orchestrator/query",
    json={"query": query1, "user_context": user_context},
    timeout=120
)
elapsed1 = time.time() - start1

print(f"   Completed in {elapsed1:.2f}s")
print("   Look for: '[DEBUG] ChromaDB indexing result: Indexed 1 documents'")

time.sleep(2)

# Query 2: Should retrieve from cache
print("\n[2] Second query - should use cache...")
query2 = "What's the scoring for google-code-golf-2025?"

start2 = time.time()
response2 = requests.post(
    f"{BACKEND_URL}/component-orchestrator/query",
    json={"query": query2, "user_context": user_context},
    timeout=120
)
elapsed2 = time.time() - start2

print(f"   Completed in {elapsed2:.2f}s")
print("\n" + "=" * 80)
print("CHECK BACKEND LOGS FOR:")
print("=" * 80)
print("[DEBUG] Doc 1 metadata keys: [...]")
print("[DEBUG] Doc 1 - slug_match: True/False, section_match: True/False")
print("")
if elapsed2 < elapsed1 * 0.5:
    print("[SUCCESS] Cache working! Second query was faster!")
else:
    print("[ISSUE] No speedup - check metadata matching in logs")
print("=" * 80)



