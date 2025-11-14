"""Interactive test for the QA system."""
import requests

BASE_URL = "http://localhost:8001"

print("=" * 60)
print("QA System Interactive Test")
print("=" * 60)

# Test the three example questions from requirements
test_questions = [
    "When is Layla planning her trip to London?",
    "How many cars does Vikram Desai have?",
    "What are Amira's favorite restaurants?"
]

print("\nTesting example questions from requirements:\n")

for i, question in enumerate(test_questions, 1):
    print(f"{i}. Question: {question}")
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question},
            timeout=30
        )
        if response.status_code == 200:
            answer = response.json().get("answer", "No answer")
            print(f"   Answer: {answer}")
        else:
            print(f"   Error: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

# Interactive mode
print("\n" + "=" * 60)
print("Interactive Mode - Enter your own questions (or 'quit' to exit)")
print("=" * 60)

while True:
    question = input("\nEnter your question: ").strip()
    if question.lower() in ['quit', 'exit', 'q']:
        break
    if not question:
        continue
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question},
            timeout=30
        )
        if response.status_code == 200:
            answer = response.json().get("answer", "No answer")
            print(f"\nAnswer: {answer}")
        else:
            print(f"\nError: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"\nError: {e}")

print("\nGoodbye!")

