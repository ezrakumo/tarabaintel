import requests
import json
import os

# Force Python to bypass any system/VPN proxies for localhost
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

url = "http://127.0.0.1:8000/api/reports/"

# Django GIS natively understands this "POINT (longitude latitude)" format!
payload = {
    "location": "POINT (11.3 8.9)",
    "lga": 5,
    "description": "The main bridge connecting Jalingo to Wukari has collapsed. Emergency vehicles cannot pass. We need immediate infrastructure repair.",
    "issue_category": "AGRIC"
}

print("Sending report to Django (Proxy bypassed via NO_PROXY)...")

# No 'proxies' argument needed! Pylance is happy, and the OS handles the bypass.
response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")

if response.status_code in [200, 201]:
    print("\n--- 🎉 SUCCESS JSON RESPONSE 🎉 ---")
    print(json.dumps(response.json(), indent=2))
else:
    print("\n--- ERROR OCCURRED ---")
    print(response.text[:500])