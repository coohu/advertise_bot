import requests
import json
key = "AIzaSyBuF6rG7kAlkYIVdzjSw0UE7mL9XxOIQUU"
project = "477544444220"
model = "gemini-1.5-flash"#"gemini-2.0-flash"
uri = "https://generativelanguage.googleapis.com/v1beta/models/"
# curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=YOUR_API_KEY" \
# -H 'Content-Type: application/json' \
# -X POST \
# -d '{
#   "contents": [{
#     "parts":[{"text": "Explain how AI works"}]
#     }]
#    }'

url = f"{uri}{model}:generateContent?key={key}"
API_KEY = "YOUR_API_KEY"  # Replace with your API key
headers = {
    "Authorization": f"Bearer {key}",  # Or however authentication is done
    "Content-Type": "application/json"  # Likely JSON
}

data = {
    "model": "gemini-2.0-flash",
    "prompt": "Write a story about a magic backpack.",
}

try:
    response = requests.post(
        "https://generativelanguage.googleapis.com/v2beta/",
        headers=headers,
        data=json.dumps(data),  # Convert data to JSON
        timeout=10  # 10-second timeout
    )

    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    response_json = response.json()  # Parse the JSON response
    print(response_json)

except requests.exceptions.Timeout:
    print("Request timed out!")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except json.JSONDecodeError:  # Handle JSON decoding errors
    print("Invalid JSON response received.")