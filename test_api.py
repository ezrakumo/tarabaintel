import requests
import json
import os

os.environ["NO_PROXY"] = "127.0.0.1,localhost"

# POINT THIS TO YOUR LIVE CLOUD URL!
url = "https://tarabaintel.onrender.com/api/reports/"

payload = {
    "location": {"type": "Point", "coordinates": [11.3, 8.9]},
    "lga": None,  # <--- WE ARE SKIPPING THE LGA TO BYPASS THE EMPTY DATABASE
    "description": "The main bridge connecting Jalingo to Wukari has collapsed. Emergency vehicles cannot pass. We need immediate infrastructure repair.",
    "issue_category": "AGRIC"
}

print("Sending report to LIVE CLOUD Django...")

response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")

if response.status_code in [200, 201]:
    print("\n--- 🎉 SUCCESS! REPORT SAVED TO CLOUD! 🎉 ---")
    print(json.dumps(response.json(), indent=2))
else:
    print("\n--- ERROR OCCURRED ---")
    print(response.text)