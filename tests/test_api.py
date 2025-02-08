import requests
import json

url = "http://localhost:8000/api/v1/query"
headers = {"Content-Type": "application/json"}
data = {
    "question": "What are limiting factors of OTA?",
    "conversation_id": "test123"
}

response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
