import requests
import json

BASE_URL = "http://localhost:8000"

test_messages = [
    "What is a moving average?",
    "How risky is investing in bitcoin?",
    "Should I buy AAPL stock?",
]


def test_chat(message: str):
    response = requests.get(f"{BASE_URL}/chat", params={"message": message})
    print(f"Q: {message}")
    print(f"A: {response.json()['response']}\n")


def main():
    print("Testing Quant Agent...\n")
    for message in test_messages:
        test_chat(message)


if __name__ == "__main__":
    main()
