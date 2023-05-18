import requests
import json

url = "http://193.168.49.71:5000/register"

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