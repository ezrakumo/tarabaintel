import requests
import json

print("🔄 Attempting to get token...")
# 1. Get Token
login_data = {"username": "ezrakumo1", "password": "SUPAUSER1@.kure2"}
token_res = requests.post("https://tarabaintel-ai.onrender.com/api/token/", json=login_data)

if token_res.status_code == 200:
    token = token_res.json()["access"]
    print("✅ Token acquired successfully!")
    
    # 2. Try to Redeem (Assuming reward ID is 1)
    print("🔄 Attempting to redeem reward ID 1...")
    headers = {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json"
    }
    redeem_data = {"reward_id": 1}
    
    redeem_res = requests.post(
        "https://tarabaintel-ai.onrender.com/api/rewards/redeem/", 
        json=redeem_data, 
        headers=headers
    )
    
    print("\n" + "="*50)
    print("👇 EXACT SERVER RESPONSE 👇")
    print(f"Status Code: {redeem_res.status_code}")
    print(f"Response Text:\n{redeem_res.text}")
    print("👆 EXACT SERVER RESPONSE 👆")
    print("="*50)
else:
    print(f"❌ Failed to get token. Status: {token_res.status_code}")
    print(token_res.text)