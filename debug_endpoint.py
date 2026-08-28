import requests
import os

os.environ["NO_PROXY"] = "127.0.0.1,localhost"

response = requests.get("http://127.0.0.1:8000/api/field-verifications/")

print(f"Status Code: {response.status_code}")
print(f"\nRaw Response (first 1000 chars):")
print(response.text[:1000])