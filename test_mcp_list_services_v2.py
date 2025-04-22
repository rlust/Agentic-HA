import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "method": "list_services",
    "params": {},
    "id": 7
}
response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.json())
