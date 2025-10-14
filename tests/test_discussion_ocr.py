"""Quick test script to verify discussion deep scraping + OCR integration."""

import requests
import json

# Backend URL
BACKEND_URL = "http://localhost:5000"

# Step 1: Initialize session
print("=" * 60)
print("STEP 1: Initializing session")
print("=" * 60)

session_response = requests.post(
    f"{BACKEND_URL}/session/initialize",
    json={
        "kaggle_username": "Hemankit",
        "competition_slug": "google-code-golf-2025"
    }
)
session_data = session_response.json()
session_id = session_data.get("session_id")
print(f"Session ID: {session_id}")

# Step 2: Fetch competition data
print("\n" + "=" * 60)
print("STEP 2: Fetching competition data")
print("=" * 60)

fetch_response = requests.post(
    f"{BACKEND_URL}/session/fetch-data",
    json={
        "session_id": session_id,
        "query": "Initialize",
        "sections": ["overview", "discussion"]
    }
)
print(f"Fetch status: {fetch_response.status_code}")

# Step 3: Query discussion with deep scraping
print("\n" + "=" * 60)
print("STEP 3: Testing discussion query with deep scraping + OCR")
print("=" * 60)

query = "Explain the discussion titled Time limit?"
print(f"Query: {query}")

query_response = requests.post(
    f"{BACKEND_URL}/component-orchestrator/query",
    json={
        "query": query,
        "context": {
            "kaggle_username": "Hemankit",
            "competition_slug": "google-code-golf-2025",
            "session_id": session_id,
            "competition_name": "google-code-golf-2025"
        }
    }
)

print(f"\nResponse status: {query_response.status_code}")

if query_response.status_code == 200:
    result = query_response.json()
    response_text = result.get("response", "")
    
    print("\n" + "=" * 60)
    print("RESPONSE PREVIEW (first 500 chars)")
    print("=" * 60)
    print(response_text[:500])
    print("...")
    
    # Check for OCR section
    if "Screenshot Content (OCR)" in response_text or "OCR" in response_text:
        print("\n✅ OCR CONTENT DETECTED IN RESPONSE!")
    else:
        print("\n⚠️  No OCR content found in response")
    
    print("\n" + "=" * 60)
    print("CHECK BACKEND LOGS FOR:")
    print("=" * 60)
    print("- [DEEP SCRAPE] Success! Found X comments")
    print("- [OCR] Processing X screenshot(s)...")
    print("- [OCR] Extracted X chars, limited to Y chars")
    print("=" * 60)
else:
    print(f"Error: {query_response.text}")

print("\n✅ Test complete! Check backend terminal for detailed logs.")





