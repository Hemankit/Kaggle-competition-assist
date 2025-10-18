"""
Quick Frontend Sanity Check
Tests that the Streamlit frontend can communicate with the backend
"""

import requests
import json

BACKEND_URL = "http://18.219.148.57:5000"
FRONTEND_URL = "http://18.219.148.57:8501"

print("="*60)
print("FRONTEND SANITY CHECK")
print("="*60)

# Test 1: Backend health check
print("\n[1/3] Testing backend health...")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    if response.status_code == 200:
        print("[OK] Backend is healthy and responding")
    else:
        print(f"[WARN] Backend health check returned {response.status_code}")
except Exception as e:
    print(f"[ERROR] Backend health check failed: {e}")

# Test 2: Session initialization
print("\n[2/3] Testing session initialization...")
try:
    response = requests.post(
        f"{BACKEND_URL}/session/initialize",
        json={"kaggle_username": "test_user"},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        session_id = data.get("session_id")
        print(f"[OK] Session initialized: {session_id}")
    else:
        print(f"[WARN] Session init returned {response.status_code}")
        session_id = None
except Exception as e:
    print(f"[ERROR] Session init failed: {e}")
    session_id = None

# Test 3: Quick query test
print("\n[3/3] Testing a simple query...")
if session_id:
    try:
        response = requests.post(
            f"{BACKEND_URL}/component-orchestrator/query",
            json={
                "query": "What is this competition about?",
                "session_id": session_id,
                "context": {
                    "competition_slug": "titanic",
                    "competition_name": "Titanic - Machine Learning from Disaster",
                    "kaggle_username": "test_user"
                }
            },
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("final_response", "")
            if len(response_text) > 100:
                print(f"[OK] Query successful! Response length: {len(response_text)} chars")
                print(f"     Preview: {response_text[:100].encode('ascii', 'ignore').decode('ascii')}...")
            else:
                print(f"[WARN] Response seems short: {len(response_text)} chars")
        else:
            print(f"[ERROR] Query failed with status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Query test failed: {e}")
else:
    print("[WARN] Skipping query test (no session)")

# Test 4: Frontend accessibility
print("\n[4/4] Testing frontend accessibility...")
try:
    response = requests.get(FRONTEND_URL, timeout=10)
    if response.status_code == 200:
        print(f"[OK] Frontend is accessible at {FRONTEND_URL}")
    else:
        print(f"[WARN] Frontend returned {response.status_code}")
except Exception as e:
    print(f"[ERROR] Frontend check failed: {e}")

print("\n" + "="*60)
print("SANITY CHECK COMPLETE")
print("="*60)
print("\n*** If all checks passed, the system is ready for users! ***")
print(f"\nFrontend URL: {FRONTEND_URL}")
print(f"GitHub: https://github.com/Hemankit/Kaggle-competition-assist")

