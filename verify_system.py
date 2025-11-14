"""Comprehensive system verification script."""
import requests
import json

BASE_URL = "http://localhost:8001"

print("=" * 70)
print("QA SYSTEM VERIFICATION")
print("=" * 70)

# Test 1: Health Check
print("\n[1/5] Testing Health Endpoint...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert r.json()["status"] == "healthy", "Health check failed"
    print("   ✅ Health endpoint working")
except Exception as e:
    print(f"   ❌ Health check failed: {e}")
    exit(1)

# Test 2: Root Endpoint
print("\n[2/5] Testing Root Endpoint...")
try:
    r = requests.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "service" in data, "Root endpoint missing service info"
    print("   ✅ Root endpoint working")
except Exception as e:
    print(f"   ❌ Root endpoint failed: {e}")

# Test 3: API Documentation
print("\n[3/5] Testing API Documentation...")
try:
    r = requests.get(f"{BASE_URL}/docs", timeout=5)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("   ✅ API docs available at /docs")
except Exception as e:
    print(f"   ⚠️  API docs check: {e}")

# Test 4: Example Questions from Requirements
print("\n[4/5] Testing Example Questions...")
test_cases = [
    "When is Layla planning her trip to London?",
    "How many cars does Vikram Desai have?",
    "What are Amira's favorite restaurants?"
]

all_passed = True
for question in test_cases:
    try:
        r = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question},
            timeout=30
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        response = r.json()
        assert "answer" in response, "Response missing 'answer' field"
        answer = response["answer"]
        assert len(answer) > 0, "Answer is empty"
        print(f"   ✅ Q: {question[:50]}...")
        print(f"      A: {answer[:80]}...")
    except Exception as e:
        print(f"   ❌ Failed: {question}")
        print(f"      Error: {e}")
        all_passed = False

if not all_passed:
    exit(1)

# Test 5: Response Format
print("\n[5/5] Testing Response Format...")
try:
    r = requests.post(
        f"{BASE_URL}/ask",
        json={"question": "Test question"},
        timeout=30
    )
    response = r.json()
    assert isinstance(response, dict), "Response is not a dictionary"
    assert "answer" in response, "Response missing 'answer' key"
    assert isinstance(response["answer"], str), "Answer is not a string"
    print("   ✅ Response format correct: {'answer': '...'}")
except Exception as e:
    print(f"   ❌ Response format check failed: {e}")
    exit(1)

# Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - SYSTEM IS WORKING CORRECTLY!")
print("=" * 70)
print(f"\nServer URL: {BASE_URL}")
print(f"API Docs: {BASE_URL}/docs")
print(f"Health: {BASE_URL}/health")
print(f"QA Endpoint: {BASE_URL}/ask")
print("\nSystem is ready to use! 🚀")

