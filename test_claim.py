import requests
import json
import os

os.environ["NO_PROXY"] = "127.0.0.1,localhost"

# 1. Get the list of verifications
print("Fetching field verifications...")
response = requests.get("http://127.0.0.1:8000/api/field-verifications/")
verifications = response.json()

# Find the first PENDING verification
pending_verifications = [v for v in verifications if v['status'] == 'PENDING']

if not pending_verifications:
    print("❌ No PENDING verifications found!")
    exit()

latest_verification = pending_verifications[0]
verification_id = latest_verification['id']
report_desc = latest_verification['report']['description'][:60] + "..."

print(f"✅ Found PENDING verification ID: {verification_id}")
print(f"📄 Report: {report_desc}")

# 2. Claim the verification
claim_payload = {
    "agent_id": "AGENT-001"
}

print(f"\n👮 Attempting to claim with AGENT-001...")
response = requests.post(
    f"http://127.0.0.1:8000/api/field-verifications/{verification_id}/claim/",
    json=claim_payload
)

print(f"Status Code: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)