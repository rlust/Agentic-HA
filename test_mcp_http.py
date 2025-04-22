import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "method": "search",
    "params": {},
    "id": 1
}
response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.json())
