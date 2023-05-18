import requests
import json

url = "http://127.0.0.1:5000/api/login"

data = {
    "username": "example_user",
    "password": "example_pas23"}

json_data = json.dumps(data)
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json_data, headers=headers)

if response.status_code == 200:
    print("Data sent successfully")
else:
    print("Failed to send data")