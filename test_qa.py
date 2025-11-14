"""Test script for the QA system."""
import requests
import time

# Wait for server to start
print("Waiting for server to start...")
time.sleep(3)

# Test health endpoint
print("\n1. Testing health endpoint...")
try:
    r = requests.get("http://localhost:8001/health", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test QA endpoint with example questions
test_questions = [
    "When is Layla planning her trip to London?",
    "How many cars does Vikram Desai have?",
    "What are Amira's favorite restaurants?"
]

print("\n2. Testing QA endpoint...")
for question in test_questions:
    print(f"\n   Question: {question}")
    try:
        r = requests.post(
            "http://localhost:8001/ask",
            json={"question": question},
            timeout=30
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            response = r.json()
            print(f"   Answer: {response.get('answer', 'N/A')}")
        else:
            print(f"   Error: {r.text}")
    except Exception as e:
        print(f"   Error: {e}")

print("\nDone!")

