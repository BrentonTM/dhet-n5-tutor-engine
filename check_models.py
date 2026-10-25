import requests

# Paste your newly generated key inside the quotes below:
api_key = "PASTE_YOUR_NEW_KEY_HERE"

url = "http://localhost:20128/v1/models"
headers = {"Authorization": f"Bearer {api_key}"}

try:
    response = requests.get(url, headers=headers)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
except Exception as e:
    print("Error:", e)