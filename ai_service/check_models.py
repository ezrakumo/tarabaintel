import os
from dotenv import load_dotenv
from groq import Groq

# Load the API key from your .env file
load_dotenv()

# Initialize the client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Fetching available models for your account...\n")

try:
    models = client.models.list()
    print("✅ SUCCESS! Here are the models you can use:")
    print("-" * 40)
    for model in models.data:
        print(f"-> {model.id}")
    print("-" * 40)
    print("\nCopy the FIRST model name from the list above and paste it into main.py!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Check your .env file to ensure your GROQ_API_KEY is correct.")