#!/usr/bin/env python3
"""
Simple test to verify backend is working
"""
import requests
import json

def test_backend():
    print("🔍 Testing Backend...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test session initialize
        response = requests.post(
            "http://localhost:5000/session/initialize",
            json={
                "kaggle_username": "test_user",
                "competition_slug": "titanic"
            },
            timeout=10
        )
        print(f"✅ Session initialize: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backend()